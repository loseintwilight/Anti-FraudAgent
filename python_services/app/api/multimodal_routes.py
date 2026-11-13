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


# ========== 请求/响应模型 ==========

class CrossImageRequest(BaseModel):
    text_input: str = Field(default="", description="用户文字描述")
    image_descriptions: List[str] = Field(default_factory=list, description="各图片的视觉描述列表")
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
    expected_is_ai: Optional[bool] = Field(default=None, description="期望结果（用于评测记录）")


class AISynthesisResponse(BaseModel):
    is_ai_generated: bool
    confidence: float
    artifacts_detected: List[str]
    analysis: str
    media_type: str
    latency_ms: float


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


# ========== 跨图关联分析 ==========

@router.post("/cross-image", response_model=CrossImageResponse)
async def analyze_cross_image(request: CrossImageRequest) -> CrossImageResponse:
    """
    跨图关联分析：多张图片+文字混合输入，检测跨图关联的诈骗场景
    - 跨图识别率目标：89%
    """
    if not request.image_descriptions:
        raise HTTPException(status_code=400, detail="至少需要一张图片描述")

    result = multimodal_engine.analyze_cross_image(
        text_input=request.text_input,
        image_descriptions=request.image_descriptions,
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
    """
    if request.media_type == "audio":
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
    )


# ========== 意图分类 ==========

@router.post("/intent-classify", response_model=IntentClassifyResponse)
async def classify_intent(request: IntentClassifyRequest) -> IntentClassifyResponse:
    """
    三模式意图识别：闲聊/咨询/反诈预警
    - 准确率目标：93%+
    """
    result = intent_classifier.classify(request.user_message)

    # 记录评测结果
    if request.expected_intent:
        intent_classifier.record_result(
            predicted=result.get("intent", "chat"),
            expected=request.expected_intent,
            user_message=request.user_message,
        )
        try:
            metrics_tracker.record_eval_result("intent", {
                "accuracy": intent_classifier.get_accuracy() * 100,
            })
            metrics_tracker.save()
        except Exception:
            pass

    intent_cn = intent_classifier.INTENT_LABELS_CN.get(result.get("intent", "chat"), "未知")

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
    intent_metrics = intent_classifier.get_metrics()

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
