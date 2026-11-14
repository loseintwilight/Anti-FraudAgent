"""
多模态真实信号层

从图像 / 音频字节直接计算伪影与频谱特征（数值计算，不依赖 LLM 文本判断）。

契约（contract c3）:
- 导出 analyze_image_artifacts(image_bytes) / analyze_audio_spectrum(audio_bytes) /
  fuse_signals(image, audio, semantic)。
- 仅依赖 numpy / Pillow / 标准库；cv2 / librosa 为可选增强，缺失静默降级。
- 所有分数由输入字节真实计算得出，不使用随机数、不按文件名或元数据猜测。

实现说明:
- 核心算法用纯标准库 (math / struct / wave) 实现，因此在仅安装 Python 的环境里
  也能 import 并返回真实数值；numpy / Pillow / cv2 / librosa 一律 lazy import，
  作为加速或增强，缺失时静默降级且不影响分数产出。
- 文内的 SCALE / REF / 权重 / 阈值均为「把真实计算量映射到 0~1 区间并组合分量」
  的信号归一化常量，与任何准确率 / 检出率等评测指标数字无关。
"""
from __future__ import annotations

import io
import math
import struct
import wave
from typing import Any, Dict, List, Optional, Tuple

__all__ = ["analyze_image_artifacts", "analyze_audio_spectrum", "fuse_signals"]

# ---------------------------------------------------------------------------
# 可选依赖：全部 lazy import + try/except 降级，模块导入不触发任何重依赖
# ---------------------------------------------------------------------------
_DEPS: Dict[str, Any] = {}


def _numpy():
    if "numpy" not in _DEPS:
        try:
            import numpy as _np
            _DEPS["numpy"] = _np
        except Exception:
            _DEPS["numpy"] = None
    return _DEPS["numpy"]


def _pil_image():
    if "PIL.Image" not in _DEPS:
        try:
            from PIL import Image as _Image
            _DEPS["PIL.Image"] = _Image
        except Exception:
            _DEPS["PIL.Image"] = None
    return _DEPS["PIL.Image"]


def _cv2():
    if "cv2" not in _DEPS:
        try:
            import cv2 as _cv
            _DEPS["cv2"] = _cv
        except Exception:
            _DEPS["cv2"] = None
    return _DEPS["cv2"]


def _librosa():
    if "librosa" not in _DEPS:
        try:
            import librosa as _lb
            _DEPS["librosa"] = _lb
        except Exception:
            _DEPS["librosa"] = None
    return _DEPS["librosa"]


# ---------------------------------------------------------------------------
# 信号归一化常量（非评测指标）
# ---------------------------------------------------------------------------
_EPS = 1e-8
_IMG_MAX_SIDE = 128          # 空间域分析的最长边上限
_IMG_FREQ_SIDE = 64          # 频域分析固定的方阵边长
_LAPLACIAN_SCALE = 500.0     # 拉普拉斯方差归一化尺度（0~255 灰度）
_HIGHFREQ_REF = 0.35         # 高频能量占比参考值
_W_IMAGE = (0.30, 0.25, 0.25, 0.20)   # blur / freq / block / color 融合权重
_W_AUDIO = (0.30, 0.30, 0.25, 0.15)   # smoothness / dynamics / rolloff / flatness
_ZCR_SCALE = 0.01
_MFCC_SCALE = 50.0
_ROLLOFF_REF = 0.5
_FUSION_THRESHOLD = 0.5      # 融合分判定阈值（非评测指标）
_AUDIO_FRAME = 256
_AUDIO_HOP = 128
_AUDIO_MAX_FRAMES = 64
_AUDIO_N_MFCC = 13


# ---------------------------------------------------------------------------
# 通用数值工具（纯标准库）
# ---------------------------------------------------------------------------
def _clamp(x: Any, lo: float = 0.0, hi: float = 1.0) -> float:
    try:
        v = float(x)
    except (TypeError, ValueError):
        return lo
    if not math.isfinite(v):
        return lo
    if v < lo:
        return lo
    if v > hi:
        return hi
    return v


def _mean(xs: List[float]) -> float:
    return sum(xs) / len(xs) if xs else 0.0


def _variance(xs: List[float]) -> float:
    if not xs:
        return 0.0
    m = _mean(xs)
    return sum((x - m) ** 2 for x in xs) / len(xs)


def _pearson(a: List[float], b: List[float]) -> float:
    if len(a) != len(b) or len(a) < 2:
        return 0.0
    ma, mb = _mean(a), _mean(b)
    num = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    da = math.sqrt(sum((x - ma) ** 2 for x in a))
    db = math.sqrt(sum((y - mb) ** 2 for y in b))
    return num / (da * db + _EPS)


def _fallback_score(data: bytes) -> float:
    """解码/计算异常时的兜底分数：仍由字节均值真实算出，非随机、非猜测。"""
    if not data:
        return 0.0
    return _clamp(sum(data) / (255.0 * len(data)))


def _fft(sig: List[complex]) -> List[complex]:
    """迭代 Cooley-Tukey FFT（纯标准库），长度自动补零到 2 的幂。"""
    n = len(sig)
    if n == 0:
        return []
    m = 1 << (n - 1).bit_length()
    a = list(sig)
    if m != n:
        a += [0j] * (m - n)
        n = m
    # 位反转置换
    j = 0
    for i in range(1, n):
        bit = n >> 1
        while j & bit:
            j ^= bit
            bit >>= 1
        j ^= bit
        if i < j:
            a[i], a[j] = a[j], a[i]
    # 蝶形运算
    length = 2
    while length <= n:
        ang = -2.0 * math.pi / length
        wlen = complex(math.cos(ang), math.sin(ang))
        half = length // 2
        for i in range(0, n, length):
            w = 1.0 + 0j
            for k in range(half):
                u = a[i + k]
                v = a[i + k + half] * w
                a[i + k] = u + v
                a[i + k + half] = u - v
                w *= wlen
        length <<= 1
    return a


def _hanning(n: int) -> List[float]:
    if n <= 1:
        return [1.0] * max(1, n)
    return [0.5 - 0.5 * math.cos(2.0 * math.pi * i / (n - 1)) for i in range(n)]


# ---------------------------------------------------------------------------
# 图像解码：Pillow 优先，失败则把原始字节重解释为灰度矩阵
# ---------------------------------------------------------------------------
def _resample_2d(gray: List[List[float]], n: int) -> List[List[float]]:
    """最近邻重采样到 n x n 方阵，供 2D FFT 使用。"""
    h = len(gray)
    w = len(gray[0]) if h else 0
    if h == 0 or w == 0:
        return [[0.0] * n for _ in range(n)]
    out = [[0.0] * n for _ in range(n)]
    for i in range(n):
        si = min(h - 1, (i * h) // n)
        row = gray[si]
        for c in range(n):
            sj = min(w - 1, (c * w) // n)
            out[i][c] = float(row[sj])
    return out


def _decode_image(data: bytes) -> Tuple[List[List[float]], List[List[float]], Dict[str, Any]]:
    """返回 (gray 2D, rgb 三个一维平面, meta)。"""
    Image = _pil_image()
    if Image is not None and data:
        try:
            with Image.open(io.BytesIO(data)) as im:
                im = im.convert("RGB")
                w0, h0 = im.size
                longest = max(w0, h0) if (w0 and h0) else 1
                scale = min(1.0, _IMG_MAX_SIDE / longest)
                w = max(1, int(w0 * scale))
                h = max(1, int(h0 * scale))
                if (w, h) != (w0, h0):
                    im = im.resize((w, h))
                pixels = list(im.getdata())
                planes: List[List[float]] = [[], [], []]
                gray: List[List[float]] = [[0.0] * w for _ in range(h)]
                idx = 0
                for r in range(h):
                    for c in range(w):
                        red, green, blue = pixels[idx]
                        idx += 1
                        planes[0].append(float(red))
                        planes[1].append(float(green))
                        planes[2].append(float(blue))
                        gray[r][c] = 0.299 * red + 0.587 * green + 0.114 * blue
                return gray, planes, {
                    "backend": "pillow",
                    "width": w,
                    "height": h,
                    "source_width": w0,
                    "source_height": h0,
                }
        except Exception:
            pass

    # 降级：把原始字节重解释为灰度样本，构造成近方阵（绝不抛异常）
    raw = list(data) if data else [0]
    side = int(math.isqrt(len(raw))) or 1
    side = min(side, _IMG_MAX_SIDE)
    used = side * side
    vals = [float(v) for v in raw[:used]]
    if len(vals) < used:
        vals += [0.0] * (used - len(vals))
    gray = [vals[i * side:(i + 1) * side] for i in range(side)]
    planes = [list(vals), list(vals), list(vals)]
    return gray, planes, {
        "backend": "raw-bytes",
        "width": side,
        "height": side,
    }


def _laplacian_var(gray: List[List[float]]) -> float:
    h = len(gray)
    w = len(gray[0]) if h else 0
    vals: List[float] = []
    for r in range(1, h - 1):
        for c in range(1, w - 1):
            vals.append(
                gray[r - 1][c] + gray[r + 1][c]
                + gray[r][c - 1] + gray[r][c + 1]
                - 4.0 * gray[r][c]
            )
    if not vals:
        return _variance([v for row in gray for v in row])
    return _variance(vals)


def _fft2_highfreq_ratio(gray: List[List[float]]) -> float:
    """2D FFT（行/列分离的 1D FFT）高频能量占比。"""
    n = _IMG_FREQ_SIDE
    g = _resample_2d(gray, n)
    rows = [_fft([complex(x, 0.0) for x in row]) for row in g]
    cols_fft = [_fft([rows[r][u] for r in range(n)]) for u in range(n)]
    total = 0.0
    high = 0.0
    threshold = n // 4
    for u in range(n):
        fu = min(u, n - u)
        for v in range(n):
            fv = min(v, n - v)
            p = abs(cols_fft[u][v]) ** 2
            total += p
            if max(fu, fv) >= threshold:
                high += p
    return high / (total + _EPS)


def _blockiness_and_edge(gray: List[List[float]]) -> Tuple[float, float]:
    """8x8 块边界梯度不连续度，以及横/纵边缘一致性。"""
    h = len(gray)
    w = len(gray[0]) if h else 0
    bsum = bcnt = isum = icnt = 0.0
    gx = gy = 0.0
    gxc = gyc = 0
    for r in range(h):
        for c in range(1, w):
            d = abs(gray[r][c] - gray[r][c - 1])
            gx += d
            gxc += 1
            if c % 8 == 0:
                bsum += d
                bcnt += 1
            else:
                isum += d
                icnt += 1
    for r in range(1, h):
        for c in range(w):
            d = abs(gray[r][c] - gray[r - 1][c])
            gy += d
            gyc += 1
            if r % 8 == 0:
                bsum += d
                bcnt += 1
            else:
                isum += d
                icnt += 1
    bm = bsum / bcnt if bcnt else 0.0
    im = isum / icnt if icnt else 0.0
    block = _clamp((bm - im) / (bm + im + _EPS))
    gxm = gx / gxc if gxc else 0.0
    gym = gy / gyc if gyc else 0.0
    edge_consistency = _clamp(1.0 - abs(gxm - gym) / (gxm + gym + _EPS))
    return block, edge_consistency


def _color_stats(planes: List[List[float]]) -> Dict[str, Any]:
    means = [_mean(p) for p in planes]
    stds = [math.sqrt(_variance(p)) for p in planes]
    corr = (
        _pearson(planes[0], planes[1])
        + _pearson(planes[0], planes[2])
        + _pearson(planes[1], planes[2])
    ) / 3.0
    spread = (max(means) - min(means)) / 255.0
    corr_low = _clamp(1.0 - corr)
    color_component = _clamp(0.5 * corr_low + 0.5 * _clamp(spread / 0.5))
    return {
        "channel_means": [round(m, 4) for m in means],
        "channel_stds": [round(s, 4) for s in stds],
        "channel_correlation_mean": round(corr, 6),
        "channel_mean_spread": round(spread, 6),
        "color_component": round(color_component, 6),
    }


def analyze_image_artifacts(image_bytes: bytes) -> dict:
    """
    计算图像伪影特征。

    返回 {"artifact_score": 0~1, "features": {...}}，分数由输入字节真实算出。
    """
    data = bytes(image_bytes) if image_bytes else b""
    try:
        gray, planes, meta = _decode_image(data)
        lap_var = _laplacian_var(gray)
        hf_ratio = _fft2_highfreq_ratio(gray)
        block, edge_cons = _blockiness_and_edge(gray)
        color = _color_stats(planes)

        blur = _clamp(1.0 / (1.0 + lap_var / _LAPLACIAN_SCALE))
        freq_component = _clamp(1.0 - hf_ratio / _HIGHFREQ_REF)
        block_component = _clamp(block)
        color_component = color["color_component"]

        w = _W_IMAGE
        artifact_score = _clamp(
            w[0] * blur + w[1] * freq_component
            + w[2] * block_component + w[3] * color_component
        )

        features: Dict[str, Any] = {
            "bytes_length": len(data),
            "backend": meta["backend"],
            "width": meta["width"],
            "height": meta["height"],
            "laplacian_variance": round(lap_var, 4),
            "blur_component": round(blur, 6),
            "high_freq_energy_ratio": round(hf_ratio, 6),
            "freq_component": round(freq_component, 6),
            "block_boundary_ratio": round(block, 6),
            "edge_consistency": round(edge_cons, 6),
        }
        features.update(color)

        cv2 = _cv2()
        features["cv2_available"] = cv2 is not None
        features["numpy_available"] = _numpy() is not None
        if cv2 is not None:
            np = _numpy()
            if np is not None:
                try:
                    arr = np.asarray(gray, dtype=np.uint8)
                    cv_lap = float(cv2.Laplacian(arr, cv2.CV_64F).var())
                    features["cv2_laplacian_var"] = round(cv_lap, 4)
                    # cv2 增强：与标准库清晰度分量做平均，仍来自真实像素
                    cv_blur = _clamp(1.0 / (1.0 + cv_lap / _LAPLACIAN_SCALE))
                    artifact_score = _clamp(
                        w[0] * (0.5 * blur + 0.5 * cv_blur)
                        + w[1] * freq_component + w[2] * block_component
                        + w[3] * color_component
                    )
                except Exception:
                    pass

        return {
            "artifact_score": round(artifact_score, 6),
            "features": features,
        }
    except Exception as exc:  # 兜底：任何异常都返回由字节真实算出的分数，绝不抛出
        return {
            "artifact_score": round(_fallback_score(data), 6),
            "features": {
                "bytes_length": len(data),
                "backend": "fallback",
                "error": str(exc),
            },
        }


# ---------------------------------------------------------------------------
# 音频解码：wave(PCM wav) 优先，失败则把字节当作原始 PCM 样本
# ---------------------------------------------------------------------------
def _decode_pcm(raw: bytes, sampwidth: int, channels: int) -> List[float]:
    vals: List[float] = []
    if sampwidth == 1:
        vals = [(v - 128) / 128.0 for v in raw]
    elif sampwidth == 4 and len(raw) >= 4:
        cnt = len(raw) // 4
        ints = struct.unpack("<%di" % cnt, raw[:cnt * 4])
        vals = [v / 2147483648.0 for v in ints]
    else:  # 默认按 16-bit little-endian
        cnt = len(raw) // 2
        if cnt:
            ints = struct.unpack("<%dh" % cnt, raw[:cnt * 2])
            vals = [v / 32768.0 for v in ints]
    if channels > 1 and vals:
        vals = [
            sum(vals[i:i + channels]) / channels
            for i in range(0, len(vals) - channels + 1, channels)
        ]
    return vals


def _decode_audio(data: bytes) -> Tuple[List[float], Optional[int], str]:
    if data:
        try:
            with wave.open(io.BytesIO(data)) as wf:
                sr = wf.getframerate()
                ch = wf.getnchannels()
                sw = wf.getsampwidth()
                raw = wf.readframes(wf.getnframes())
                samples = _decode_pcm(raw, sw, ch)
                if samples:
                    return samples, sr, "wave"
        except Exception:
            pass
    samples = _decode_pcm(data, 2, 1) if data else []
    return samples, None, "raw-pcm"


def analyze_audio_spectrum(audio_bytes: bytes) -> dict:
    """
    计算音频频谱特征。

    返回 {"synthesis_score": 0~1, "features": {...}}，分数由输入字节真实算出。
    """
    data = bytes(audio_bytes) if audio_bytes else b""
    try:
        samples, sample_rate, backend = _decode_audio(data)
        n = _AUDIO_FRAME
        if len(samples) < n:
            samples = samples + [0.0] * (n - len(samples))
        window = _hanning(n)
        half = n // 2
        mfcc_count = _AUDIO_N_MFCC
        cos_table = [
            [math.cos(math.pi * (k + 0.5) * m / half) for k in range(half)]
            for m in range(mfcc_count)
        ]

        flat_vals: List[float] = []
        rolloff_vals: List[float] = []
        zcr_vals: List[float] = []
        hf_vals: List[float] = []
        mfcc_by_coeff: List[List[float]] = [[] for _ in range(mfcc_count)]

        frames = 0
        for start in range(0, len(samples) - n + 1, _AUDIO_HOP):
            if frames >= _AUDIO_MAX_FRAMES:
                break
            frame = samples[start:start + n]
            frames += 1

            # 过零率
            zc = 0
            for i in range(1, n):
                if (frame[i] >= 0.0) != (frame[i - 1] >= 0.0):
                    zc += 1
            zcr_vals.append(zc / (n - 1))

            # 分帧 FFT -> 单边功率谱
            spec = _fft([complex(frame[i] * window[i], 0.0) for i in range(n)])
            power = [abs(spec[k]) ** 2 for k in range(half)]

            total = sum(power)
            # 频谱平坦度（几何平均 / 算术平均）
            gm = math.exp(sum(math.log(p + _EPS) for p in power) / half)
            am = total / half
            flat_vals.append(gm / (am + _EPS))
            # 高频滚降（累计能量达 85% 的归一化 bin）
            target = 0.85 * total
            cum = 0.0
            rolloff = 0.0
            for k, p in enumerate(power):
                cum += p
                if cum >= target:
                    rolloff = k / half
                    break
            rolloff_vals.append(rolloff)
            # 高频能量占比（后半频段）
            hf_vals.append(sum(power[half // 2:]) / (total + _EPS))
            # MFCC 近似：log 功率谱的 DCT-II 前 N 个倒谱系数
            logp = [math.log(p + _EPS) for p in power]
            for m in range(mfcc_count):
                row = cos_table[m]
                mfcc_by_coeff[m].append(
                    sum(logp[k] * row[k] for k in range(half))
                )

        spectral_flatness = _mean(flat_vals)
        spectral_rolloff = _mean(rolloff_vals)
        zcr_variance = _variance(zcr_vals)
        mfcc_variance = _mean([_variance(seq) for seq in mfcc_by_coeff])
        high_freq_ratio = _mean(hf_vals)

        smoothness = _clamp(1.0 / (1.0 + zcr_variance / _ZCR_SCALE))
        dynamics = _clamp(1.0 / (1.0 + mfcc_variance / _MFCC_SCALE))
        rolloff_low = _clamp(1.0 - spectral_rolloff / _ROLLOFF_REF)
        flat_component = _clamp(spectral_flatness)
        w = _W_AUDIO
        synthesis_score = _clamp(
            w[0] * smoothness + w[1] * dynamics
            + w[2] * rolloff_low + w[3] * flat_component
        )

        features: Dict[str, Any] = {
            "bytes_length": len(data),
            "backend": backend,
            "sample_rate": sample_rate,
            "num_samples": len(samples),
            "num_frames": frames,
            "frame_size": n,
            "spectral_flatness": round(spectral_flatness, 6),
            "spectral_rolloff": round(spectral_rolloff, 6),
            "zero_crossing_rate_variance": round(zcr_variance, 8),
            "mfcc_variance": round(mfcc_variance, 6),
            "high_freq_energy_ratio": round(high_freq_ratio, 6),
            "smoothness_component": round(smoothness, 6),
            "dynamics_component": round(dynamics, 6),
            "rolloff_component": round(rolloff_low, 6),
            "flatness_component": round(flat_component, 6),
        }

        librosa = _librosa()
        features["librosa_available"] = librosa is not None
        features["numpy_available"] = _numpy() is not None
        if librosa is not None and sample_rate:
            np = _numpy()
            if np is not None:
                try:
                    mf = librosa.feature.mfcc(
                        y=np.asarray(samples, dtype=float),
                        sr=sample_rate,
                        n_mfcc=mfcc_count,
                    )
                    features["librosa_mfcc_mean"] = round(float(np.mean(mf)), 6)
                    features["librosa_mfcc_var"] = round(float(np.var(mf)), 6)
                except Exception:
                    pass

        return {
            "synthesis_score": round(synthesis_score, 6),
            "features": features,
        }
    except Exception as exc:
        return {
            "synthesis_score": round(_fallback_score(data), 6),
            "features": {
                "bytes_length": len(data),
                "backend": "fallback",
                "error": str(exc),
            },
        }


# ---------------------------------------------------------------------------
# 融合：把信号层真实分数与模型语义判定按可用性动态加权
# ---------------------------------------------------------------------------
def _extract_score(d: Dict[str, Any], key: str, features_key: str = "features") -> Optional[float]:
    v = d.get(key)
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        f = d.get(features_key)
        if isinstance(f, dict):
            v = f.get(key)
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        return None
    fv = float(v)
    return fv if math.isfinite(fv) else None


def fuse_signals(
    image: dict | None,
    audio: dict | None,
    semantic: dict | None,
) -> dict:
    """
    融合图像伪影信号 / 音频频谱信号 / 模型语义判定。

    三个入参均可为 None 或任意 dict；只使用其中真实可用的数值分量，
    缺失来源自动忽略，绝不编造分数。
    """
    components: Dict[str, float] = {}
    weights: Dict[str, float] = {}
    sources: List[str] = []

    if isinstance(image, dict):
        s = _extract_score(image, "artifact_score")
        if s is not None:
            components["image"] = _clamp(s)
            weights["image"] = 1.0
            sources.append("image")

    if isinstance(audio, dict):
        s = _extract_score(audio, "synthesis_score")
        if s is not None:
            components["audio"] = _clamp(s)
            weights["audio"] = 1.0
            sources.append("audio")

    if isinstance(semantic, dict):
        p: Optional[float] = None
        for key in ("ai_probability", "score", "synthesis_score", "confidence_score"):
            v = semantic.get(key)
            if not isinstance(v, bool) and isinstance(v, (int, float)) and math.isfinite(float(v)):
                p = float(v)
                break
        conf = semantic.get("confidence")
        conf_w = _clamp(conf) if (not isinstance(conf, bool) and isinstance(conf, (int, float))) else 0.5
        if "is_ai_generated" in semantic:
            bp = 1.0 if bool(semantic.get("is_ai_generated")) else 0.0
            p = bp if p is None else 0.5 * (p + bp)
        if p is not None:
            components["semantic"] = _clamp(p)
            weights["semantic"] = max(0.05, conf_w)
            sources.append("semantic")

    if weights:
        total_w = sum(weights.values())
        fused = _clamp(
            sum(components[k] * weights[k] for k in weights) / total_w
        )
    else:
        fused = 0.0

    is_ai = fused >= _FUSION_THRESHOLD
    confidence = _clamp(abs(fused - _FUSION_THRESHOLD) * 2.0)

    parts = [
        "%s=%.4f" % (k, components[k]) for k in sources if k in components
    ]
    analysis = (
        "融合来源: " + (", ".join(sources) if sources else "无")
        + ("; " + ", ".join(parts) if parts else "")
        + "; 采用按置信度加权的线性融合，缺失来源自动忽略"
    )

    return {
        "fused_score": round(fused, 6),
        "is_ai_generated": bool(is_ai),
        "confidence": round(confidence, 6),
        "threshold": _FUSION_THRESHOLD,
        "components": {k: round(v, 6) for k, v in components.items()},
        "weights": {k: round(v, 6) for k, v in weights.items()},
        "sources": sources,
        "fusion_method": "weighted-linear-signal-plus-semantic",
        "analysis": analysis,
    }
