"""
混合多模态识别引擎
实现图/视频/音频/文本混合输入与跨图关联分析
- 跨图关联识别：多张图片之间的语义关联分析
- 跨图识别率目标：89%
"""
from __future__ import annotations

import json
import logging
import time
from typing import Any, Dict, List, Optional, Tuple

from langchain_core.messages import HumanMessage
from langchain_dashscope import ChatDashScope

from app.llm.config import LLMConfig

logger = logging.getLogger(__name__)

# 跨图关联分析提示词
CROSS_IMAGE_PROMPT = """你是一个反诈多模态分析专家。用户上传了多张图片和文字描述，请综合分析。

【用户文字描述】
{text_input}

【图片描述】
{image_descriptions}

【分析要求】
1. 检查图片之间是否存在关联（如：聊天截图+转账记录+身份证照片的组合）
2. 判断是否构成诈骗场景
3. 如果多张图片共同指向同一诈骗类型，请标注跨图关联识别结果
4. 输出跨图识别置信度

【输出格式（JSON）】
{{
    "is_fraud": true/false,
    "fraud_type": "诈骗类型",
    "cross_image_correlation": true/false,
    "correlation_confidence": 0.0-1.0,
    "analysis": "综合分析",
    "risk_level": "low/medium/high/critical"
}}"""


class MultimodalEngine:
    """混合多模态识别引擎"""

    def __init__(self):
        self._model: Optional[ChatDashScope] = None
        self._metrics: Dict[str, Any] = {
            "total_requests": 0,
            "cross_image_correct": 0,
            "cross_image_total": 0,
            "latency_records": [],
        }

    @property
    def model(self) -> ChatDashScope:
        if self._model is None:
            self._model = ChatDashScope(
                model=LLMConfig.CHAT_MODEL,
                dashscope_api_key=LLMConfig.DASHSCOPE_API_KEY,
                temperature=0.1,
                max_tokens=1000,
            )
        return self._model

    def analyze_cross_image(
        self,
        text_input: str,
        image_descriptions: List[str],
    ) -> Dict[str, Any]:
        """
        跨图关联分析

        参数:
            text_input: 用户文字描述
            image_descriptions: 各图片的视觉描述列表

        返回:
            分析结果字典
        """
        start_time = time.time()
        self._metrics["total_requests"] += 1

        if len(image_descriptions) <= 1:
            return {
                "is_fraud": False,
                "fraud_type": "",
                "cross_image_correlation": False,
                "correlation_confidence": 0.0,
                "analysis": "单张图片，无需跨图关联",
                "risk_level": "low",
            }

        try:
            images_text = "\n".join(
                f"图片{i+1}: {desc}" for i, desc in enumerate(image_descriptions)
            )

            prompt = CROSS_IMAGE_PROMPT.format(
                text_input=text_input[:500],
                image_descriptions=images_text[:2000],
            )

            response = self.model.invoke([HumanMessage(content=prompt)])
            result_text = response.content if response.content else ""

            try:
                json_start = result_text.find("{")
                json_end = result_text.rfind("}") + 1
                if json_start >= 0 and json_end > json_start:
                    result = json.loads(result_text[json_start:json_end])
                else:
                    result = {"is_fraud": False, "cross_image_correlation": False}
            except json.JSONDecodeError:
                result = {"is_fraud": False, "cross_image_correlation": False}

        except Exception as e:
            logger.error(f"跨图分析失败: {e}")
            result = {"is_fraud": False, "cross_image_correlation": False, "error": str(e)}

        latency = (time.time() - start_time) * 1000
        self._metrics["latency_records"].append(latency)

        result["_latency_ms"] = round(latency, 2)
        return result

    def record_cross_image_result(self, expected: bool, actual: bool):
        """记录跨图识别结果用于计算准确率"""
        self._metrics["cross_image_total"] += 1
        if expected == actual:
            self._metrics["cross_image_correct"] += 1

    def get_cross_image_accuracy(self) -> float:
        """获取跨图识别准确率"""
        if self._metrics["cross_image_total"] == 0:
            return 0.0
        return self._metrics["cross_image_correct"] / self._metrics["cross_image_total"]

    def get_metrics(self) -> Dict[str, Any]:
        """获取引擎指标"""
        latencies = self._metrics["latency_records"]
        if latencies:
            latencies_sorted = sorted(latencies)
            p50_idx = int(len(latencies_sorted) * 0.5)
            p99_idx = int(len(latencies_sorted) * 0.99)
            return {
                "total_requests": self._metrics["total_requests"],
                "cross_image_accuracy": round(self.get_cross_image_accuracy() * 100, 1),
                "cross_image_total": self._metrics["cross_image_total"],
                "cross_image_correct": self._metrics["cross_image_correct"],
                "avg_latency_ms": round(sum(latencies) / len(latencies), 2),
                "p50_latency_ms": round(latencies_sorted[p50_idx], 2),
                "p99_latency_ms": round(latencies_sorted[p99_idx], 2) if p99_idx < len(latencies_sorted) else round(latencies_sorted[-1], 2),
            }
        return {
            "total_requests": self._metrics["total_requests"],
            "cross_image_accuracy": round(self.get_cross_image_accuracy() * 100, 1),
            "avg_latency_ms": 0,
        }


# 全局实例
multimodal_engine = MultimodalEngine()