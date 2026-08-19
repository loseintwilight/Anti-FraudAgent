"""
AI 合成内容检测器
检测 AI 换脸 (Deepfake) 和 AI 拟声 (Voice Cloning)
- 视觉 artifacts 检测：皮肤纹理异常、光影不一致、面部边缘锯齿
- 音频频谱检测：频谱不连续性、频率分布异常
- 检出率目标：85%+
"""
from __future__ import annotations

import logging
import time
from typing import Any, Dict, List, Optional, Tuple

from langchain_core.messages import HumanMessage
from langchain_dashscope import ChatDashScope

from app.llm.config import LLMConfig

logger = logging.getLogger(__name__)

# AI 合成检测提示词（视觉）
AI_SYNTHESIS_IMAGE_PROMPT = """你是 AI 合成内容检测专家。请分析以下图片描述，判断是否为 AI 生成/换脸。

【图片描述】
{image_description}

【检测维度】
1. 皮肤纹理：是否有不自然的平滑、模糊区域？
2. 光影一致性：光源方向是否一致？阴影是否合理？
3. 面部边缘：发际线、耳朵边缘是否有锯齿/模糊？
4. 背景异常：背景是否有扭曲、融合痕迹？
5. 细节一致性：左右眼、牙齿、手指等细节是否对称自然？

【输出格式（JSON）】
{{
    "is_ai_generated": true/false,
    "confidence": 0.0-1.0,
    "artifacts_detected": ["检测到的异常列表"],
    "analysis": "详细分析"
}}"""

# AI 合成检测提示词（音频）
AI_SYNTHESIS_AUDIO_PROMPT = """你是 AI 语音合成检测专家。请分析以下音频描述，判断是否为 AI 生成/拟声。

【音频描述】
{audio_description}

【检测维度】
1. 频谱连续性：是否有不自然的频率跳变？
2. 基频稳定性：基频 (F0) 是否稳定自然？
3. 共振峰：共振峰过渡是否平滑？
4. 呼吸/停顿：是否有自然的呼吸声和停顿？
5. 背景噪声：噪声模式是否一致？

【输出格式（JSON）】
{{
    "is_ai_generated": true/false,
    "confidence": 0.0-1.0,
    "artifacts_detected": ["检测到的异常列表"],
    "analysis": "详细分析"
}}"""


class AISynthesisDetector:
    """AI 合成内容检测器"""

    def __init__(self):
        self._model: Optional[ChatDashScope] = None
        self._metrics: Dict[str, Any] = {
            "total_detected": 0,
            "correct_detections": 0,
            "false_positives": 0,
            "total_samples": 0,
            "ai_samples_total": 0,
            "real_samples_total": 0,
        }

    @property
    def model(self) -> ChatDashScope:
        if self._model is None:
            self._model = ChatDashScope(
                model=LLMConfig.CHAT_MODEL,
                dashscope_api_key=LLMConfig.DASHSCOPE_API_KEY,
                temperature=0.1,
                max_tokens=800,
            )
        return self._model

    def detect_image_synthesis(self, image_description: str) -> Dict[str, Any]:
        """检测图片是否为 AI 合成"""
        start_time = time.time()

        try:
            prompt = AI_SYNTHESIS_IMAGE_PROMPT.format(
                image_description=image_description[:1500]
            )
            response = self.model.invoke([HumanMessage(content=prompt)])
            result_text = response.content if response.content else ""

            import json
            try:
                json_start = result_text.find("{")
                json_end = result_text.rfind("}") + 1
                if json_start >= 0 and json_end > json_start:
                    result = json.loads(result_text[json_start:json_end])
                else:
                    result = {"is_ai_generated": False, "confidence": 0.0}
            except json.JSONDecodeError:
                result = {"is_ai_generated": False, "confidence": 0.0}

        except Exception as e:
            logger.error(f"AI合成图片检测失败: {e}")
            result = {"is_ai_generated": False, "confidence": 0.0, "error": str(e)}

        latency = (time.time() - start_time) * 1000
        result["_latency_ms"] = round(latency, 2)
        result["_media_type"] = "image"
        return result

    def detect_audio_synthesis(self, audio_description: str) -> Dict[str, Any]:
        """检测音频是否为 AI 合成"""
        start_time = time.time()

        try:
            prompt = AI_SYNTHESIS_AUDIO_PROMPT.format(
                audio_description=audio_description[:1500]
            )
            response = self.model.invoke([HumanMessage(content=prompt)])
            result_text = response.content if response.content else ""

            import json
            try:
                json_start = result_text.find("{")
                json_end = result_text.rfind("}") + 1
                if json_start >= 0 and json_end > json_start:
                    result = json.loads(result_text[json_start:json_end])
                else:
                    result = {"is_ai_generated": False, "confidence": 0.0}
            except json.JSONDecodeError:
                result = {"is_ai_generated": False, "confidence": 0.0}

        except Exception as e:
            logger.error(f"AI合成音频检测失败: {e}")
            result = {"is_ai_generated": False, "confidence": 0.0, "error": str(e)}

        latency = (time.time() - start_time) * 1000
        result["_latency_ms"] = round(latency, 2)
        result["_media_type"] = "audio"
        return result

    def record_detection_result(self, is_ai_generated: bool, detected: bool):
        """记录检测结果用于计算检出率"""
        self._metrics["total_samples"] += 1
        if is_ai_generated:
            self._metrics["ai_samples_total"] += 1
            if detected:
                self._metrics["correct_detections"] += 1
        else:
            self._metrics["real_samples_total"] += 1
            if detected:
                self._metrics["false_positives"] += 1

    def get_detection_rate(self) -> float:
        """获取 AI 合成检出率"""
        if self._metrics["ai_samples_total"] == 0:
            return 0.0
        return self._metrics["correct_detections"] / self._metrics["ai_samples_total"]

    def get_false_positive_rate(self) -> float:
        """获取误报率"""
        if self._metrics["real_samples_total"] == 0:
            return 0.0
        return self._metrics["false_positives"] / self._metrics["real_samples_total"]

    def get_metrics(self) -> Dict[str, Any]:
        """获取检测器指标"""
        return {
            "detection_rate": round(self.get_detection_rate() * 100, 1),
            "false_positive_rate": round(self.get_false_positive_rate() * 100, 1),
            "total_samples": self._metrics["total_samples"],
            "ai_samples_total": self._metrics["ai_samples_total"],
            "correct_detections": self._metrics["correct_detections"],
            "false_positives": self._metrics["false_positives"],
        }


# 全局实例
ai_synthesis_detector = AISynthesisDetector()