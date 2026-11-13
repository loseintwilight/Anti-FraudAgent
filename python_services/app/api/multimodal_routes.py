"""
多模态识别 API 路由
- 跨图关联分析：多张图片+文字混合输入
- AI 合成内容检测：换脸/拟声检测
- 意图分类：三模式（闲聊/咨询/反诈预警）
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.llm.multimodal_engine import multimodal_engine
from app.llm.ai_synthesis_detector import ai_synthesis_detector
from app.llm.intent_classifier import intent_classifier
from app.metrics.tracker import metrics_tracker

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/multimodal", tags=["Multimodal"])


def _get_intent_classifier():
    """
    意图分类模块顶层依赖 LangChain，改为按需 lazy import：
    保证 main.py 挂载本路由时不会因缺少重依赖而导入失败。
    """
    try:
        from app.llm.intent_classifier import intent_classifier
        return intent_classifier
    except Exception as e:
        logger.warning(f"意图分类模块不可用，相关能力降级: {e}")
        return None


def _decode_b64(value: str) -> bytes:
    """解码 base64（兼容 data URI 前缀），失败返回空字节（信号层仍可计算）。"""
    if not value:
        return b""
    clean = value.split(",", 1)[1] if "," in value else value
    try:
        return base64.b64decode(clean)
    except Exception:
        return b""


def _maybe_transcribe(audio_bytes: bytes):
    """
    可选 ASR 转写：仅当配置了 ASR_API_URL 时才尝试（标准库 urllib，lazy）。
    未配置或调用失败时如实返回 (None, asr_configured, note)，绝不返回预置话术。
    """
    endpoint = os.getenv("ASR_API_URL", "").strip()
    if not endpoint:
        return None, False, "未配置 ASR_API_URL，未进行转写，仅返回真实频谱特征"

    api_key = os.getenv("ASR_API_KEY", "").strip()
    try:
        import json
        import urllib.request

        boundary = "----signalboundary"
        head = (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="file"; filename="audio.bin"\r\n'
            f"Content-Type: application/octet-stream\r\n\r\n"
        ).encode("utf-8")
        tail = f"\r\n--{boundary}--\r\n".encode("utf-8")
        body = head + audio_bytes + tail
        headers = {"Content-Type": f"multipart/form-data; boundary={boundary}"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        req = urllib.request.Request(endpoint, data=body, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=10) as resp:
            payload = json.loads(resp.read().decode("utf-8", "ignore"))
        text = None
        if isinstance(payload, dict):
            data = payload.get("data")
            text = payload.get("text") or payload.get("transcript")
            if not text and isinstance(data, dict):
                text = data.get("text") or data.get("transcript")
        if text:
            return str(text), True, "ASR 转写完成"
        return None, True, "ASR 接口未返回转写文本"
    except Exception as e:
        return None, True, f"ASR 调用失败: {e}"


# ========== 请求/响应模型 ==========

class CrossImageRequest(BaseModel):
    text_input: str = Field(default="", description="用户文字描述")
    image_descriptions: List[str] = Field(default_factory=list, description="各图片的视觉描述列表（向后兼容）")
    images_base64: List[str] = Field(default_factory=list, description="真实图片 base64 列表（新增能力，优先经视觉模型解析）")
    expected_is_fraud: Optional[bool] = Field(default=None, description="期望结果（用于评测记录）")


class CrossImageResponse(BaseModel):
    is_fraud: bool
    fraud_type: str
    cross_image_correlation: bool
    correlation_confidence: float
    analysis: str
    risk_level: str
    latency_ms: float


class AISynthesisRequest(BaseModel):
    media_type: str = Field(default="image", description="媒体类型: image/audio")
    description: str = Field(..., description="图片/音频描述")
    media_base64: Optional[str] = Field(default=None, description="真实图片/音频 base64（新增，触发信号层融合）")
    expected_is_ai: Optional[bool] = Field(default=None, description="期望结果（用于评测记录）")


class AISynthesisResponse(BaseModel):
    is_ai_generated: bool
    confidence: float
    artifacts_detected: List[str]
    analysis: str
    media_type: str
    latency_ms: float
    signal_features: Optional[Dict[str, Any]] = Field(default=None, description="信号层真实数值特征（新增可选字段）")


class IntentClassifyRequest(BaseModel):
    user_message: str = Field(..., description="用户消息")
    expected_intent: Optional[str] = Field(default=None, description="期望意图（用于评测记录）")


class IntentClassifyResponse(BaseModel):
    intent: str
    intent_cn: str
    confidence: float
    reason: str
    latency_ms: float


class MetricsResponse(BaseModel):
    cross_image_accuracy: float
    ai_synthesis_detection_rate: float
    ai_synthesis_false_positive_rate: float
    intent_accuracy: float
    intent_confusion_matrix: Dict[str, Dict[str, int]]


# ---- 新增：信号层与音视频输入通道 ----

class SignalImageRequest(BaseModel):
    image_base64: str = Field(..., description="真实图片 base64")


class SignalImageResponse(BaseModel):
    artifact_score: float = Field(..., description="由图像字节真实计算得到的伪影分 0~1")
    features: Dict[str, Any] = Field(..., description="真实数值特征")


class AudioSpectrumRequest(BaseModel):
    audio_base64: str = Field(..., description="真实音频字节的 base64")


class AudioSpectrumResponse(BaseModel):
    synthesis_score: float = Field(..., description="由音频字节真实计算得到的合成可疑分 0~1")
    features: Dict[str, Any] = Field(..., description="真实频谱特征")
    transcript: Optional[str] = Field(default=None, description="可选 ASR 转写文本（未配置时为 None）")
    asr_configured: bool = Field(default=False, description="是否配置了可选 ASR")
    note: str = Field(default="", description="ASR 状态说明（如实标注，非预置话术）")


class VideoFramesRequest(BaseModel):
    frames_base64: List[str] = Field(..., description="视频帧 base64 列表（按时间顺序）")
    prompt: Optional[str] = Field(default=None, description="逐帧视觉分析自定义提示词")


class VideoFramesResponse(BaseModel):
    frame_count: int
    mean_artifact_score: float = Field(..., description="各帧真实伪影分的均值")
    frames: List[Dict[str, Any]]


# ========== 跨图关联分析 ==========

@router.post("/cross-image", response_model=CrossImageResponse)
async def analyze_cross_image(request: CrossImageRequest) -> CrossImageResponse:
    """
    跨图关联分析：多张图片+文字混合输入，检测跨图关联的诈骗场景
    - 跨图识别率目标：89%
    """
    if not request.image_descriptions and not request.images_base64:
        raise HTTPException(status_code=400, detail="至少需要一张图片描述或一张真实图片")

    result = multimodal_engine.analyze_cross_image(
        text_input=request.text_input,
        image_descriptions=request.image_descriptions,
        images_base64=request.images_base64 or None,
    )

    # 记录评测结果
    if request.expected_is_fraud is not None:
        multimodal_engine.record_cross_image_result(
            expected=request.expected_is_fraud,
            actual=result.get("is_fraud", False),
        )
        acc = multimodal_engine.get_cross_image_accuracy()
        try:
            metrics_tracker.record_eval_result("cross_image", {"accuracy": acc * 100})
            metrics_tracker.save()
        except Exception:
            pass

    return CrossImageResponse(
        is_fraud=result.get("is_fraud", False),
        fraud_type=result.get("fraud_type", ""),
        cross_image_correlation=result.get("cross_image_correlation", False),
        correlation_confidence=result.get("correlation_confidence", 0.0),
        analysis=result.get("analysis", ""),
        risk_level=result.get("risk_level", "low"),
        latency_ms=result.get("_latency_ms", 0),
    )


# ========== AI 合成内容检测 ==========

@router.post("/ai-synthesis-detect", response_model=AISynthesisResponse)
async def detect_ai_synthesis(request: AISynthesisRequest) -> AISynthesisResponse:
    """
    AI 合成内容检测：检测换脸(Deepfake)和拟声(Voice Cloning)
    - 检出率目标：85%+
    - 提供 media_base64 时，融合真实信号层分数与模型语义判定
    """
    if request.media_base64:
        media_bytes = _decode_b64(request.media_base64)
        result = ai_synthesis_detector.detect_with_signals(
            media_type=request.media_type,
            description=request.description,
            media_bytes=media_bytes,
        )
    elif request.media_type == "audio":
        result = ai_synthesis_detector.detect_audio_synthesis(request.description)
    else:
        result = ai_synthesis_detector.detect_image_synthesis(request.description)

    # 记录评测结果
    if request.expected_is_ai is not None:
        ai_synthesis_detector.record_detection_result(
            is_ai_generated=request.expected_is_ai,
            detected=result.get("is_ai_generated", False),
        )
        try:
            metrics_tracker.record_eval_result("ai_synthesis", {
                "detection_rate": ai_synthesis_detector.get_detection_rate() * 100,
            })
            metrics_tracker.save()
        except Exception:
            pass

    return AISynthesisResponse(
        is_ai_generated=result.get("is_ai_generated", False),
        confidence=result.get("confidence", 0.0),
        artifacts_detected=result.get("artifacts_detected", []),
        analysis=result.get("analysis", ""),
        media_type=result.get("_media_type", request.media_type),
        latency_ms=result.get("_latency_ms", 0),
        signal_features=result.get("signal_features"),
    )


# ========== 意图分类 ==========

@router.post("/intent-classify", response_model=IntentClassifyResponse)
async def classify_intent(request: IntentClassifyRequest) -> IntentClassifyResponse:
    """
    三模式意图识别：闲聊/咨询/反诈预警
    - 准确率目标：93%+
    """
    clf = _get_intent_classifier()
    if clf is None:
        raise HTTPException(status_code=503, detail="意图分类依赖当前不可用")
    result = clf.classify(request.user_message)

    # 记录评测结果
    if request.expected_intent:
        clf.record_result(
            predicted=result.get("intent", "chat"),
            expected=request.expected_intent,
            user_message=request.user_message,
        )
        try:
            metrics_tracker.record_eval_result("intent", {
                "accuracy": clf.get_accuracy() * 100,
            })
            metrics_tracker.save()
        except Exception:
            pass

    intent_cn = clf.INTENT_LABELS_CN.get(result.get("intent", "chat"), "未知")

    return IntentClassifyResponse(
        intent=result.get("intent", "chat"),
        intent_cn=intent_cn,
        confidence=result.get("confidence", 0.0),
        reason=result.get("reason", ""),
        latency_ms=result.get("_latency_ms", 0),
    )


# ========== 综合指标查询 ==========

@router.get("/metrics", response_model=MetricsResponse)
async def get_multimodal_metrics() -> MetricsResponse:
    """获取多模态识别引擎的综合指标"""
    cross_img_metrics = multimodal_engine.get_metrics()
    synthesis_metrics = ai_synthesis_detector.get_metrics()
    clf = _get_intent_classifier()
    intent_metrics = clf.get_metrics() if clf is not None else {}

    return MetricsResponse(
        cross_image_accuracy=cross_img_metrics.get("cross_image_accuracy", 0),
        ai_synthesis_detection_rate=synthesis_metrics.get("detection_rate", 0),
        ai_synthesis_false_positive_rate=synthesis_metrics.get("false_positive_rate", 0),
        intent_accuracy=intent_metrics.get("accuracy", 0),
        intent_confusion_matrix=intent_metrics.get("confusion_matrix", {}),
    )


# ========== 信号层：图像伪影（无需 API Key，返回真实数值）==========

@router.post("/signal/image", response_model=SignalImageResponse, tags=["Multimodal Signals"])
async def image_signal(request: SignalImageRequest) -> SignalImageResponse:
    """对真实图片字节计算视觉伪影特征（拉普拉斯清晰度/FFT 高频/块效应/色彩统计）。"""
    sig = analyze_image_artifacts(_decode_b64(request.image_base64))
    return SignalImageResponse(
        artifact_score=sig["artifact_score"],
        features=sig["features"],
    )


# ========== 音频输入通道：真实频谱 + 可选 ASR ==========

@router.post("/audio/spectrum", response_model=AudioSpectrumResponse, tags=["Multimodal Signals"])
async def audio_spectrum(request: AudioSpectrumRequest) -> AudioSpectrumResponse:
    """
    接收音频字节，返回由分帧 FFT 真实计算的频谱特征。
    配置 ASR_API_URL 时尝试转写；未配置时如实返回频谱结果，不返回预置话术。
    """
    raw = _decode_b64(request.audio_base64)
    sig = analyze_audio_spectrum(raw)
    transcript, asr_configured, note = _maybe_transcribe(raw)
    return AudioSpectrumResponse(
        synthesis_score=sig["synthesis_score"],
        features=sig["features"],
        transcript=transcript,
        asr_configured=asr_configured,
        note=note,
    )


# ========== 视频帧逐帧分析（复用 vision.py，不依赖 Java 控制器）==========

@router.post("/video/frames", response_model=VideoFramesResponse, tags=["Multimodal Signals"])
async def video_frames(request: VideoFramesRequest) -> VideoFramesResponse:
    """接收真实视频帧列表，逐帧复用视觉模型分析，并计算各帧真实伪影特征。"""
    frames_out: List[Dict[str, Any]] = []
    scores: List[float] = []
    vision_results = vision_analyzer.analyze_frames(request.frames_base64, prompt=request.prompt)
    for idx, (b64, vr) in enumerate(zip(request.frames_base64, vision_results)):
        sig = analyze_image_artifacts(_decode_b64(b64))
        scores.append(sig["artifact_score"])
        frames_out.append({
            "index": idx,
            "vision": vr,
            "signal": {
                "artifact_score": sig["artifact_score"],
                "features": sig["features"],
            },
        })
    mean_score = sum(scores) / len(scores) if scores else 0.0
    return VideoFramesResponse(
        frame_count=len(request.frames_base64),
        mean_artifact_score=round(mean_score, 6),
        frames=frames_out,
    )
