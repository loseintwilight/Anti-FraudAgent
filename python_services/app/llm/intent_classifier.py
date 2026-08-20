"""
意图识别分类器
三模式识别：闲聊/咨询/反诈预警
- 准确率目标：93%+
- 输出混淆矩阵
"""
from __future__ import annotations

import json
import logging
import time
from typing import Any, Dict, List, Optional, Tuple

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_dashscope import ChatDashScope

from app.llm.config import LLMConfig

logger = logging.getLogger(__name__)

# 意图识别提示词
INTENT_CLASSIFY_PROMPT = """你是反诈意图识别专家。请对用户消息进行分类。

【分类标签】
- chat: 闲聊（问候、天气、日常话题、身份询问等）
- consult: 咨询（询问反诈知识、诈骗定义、如何防范等）
- alert: 反诈预警（用户描述个人遭遇、收到可疑信息、正在经历诈骗场景等）

【用户消息】
{user_message}

【输出格式（JSON）】
{{
    "intent": "chat/consult/alert",
    "confidence": 0.0-1.0,
    "reason": "分类理由"
}}"""


class IntentClassifier:
    """意图识别分类器"""

    INTENT_LABELS = ["chat", "consult", "alert"]
    INTENT_LABELS_CN = {"chat": "闲聊", "consult": "咨询", "alert": "反诈预警"}

    def __init__(self):
        self._model: Optional[ChatDashScope] = None
        self._metrics: Dict[str, Any] = {
            "total_predictions": 0,
            "correct_predictions": 0,
            "confusion_matrix": {
                "chat": {"chat": 0, "consult": 0, "alert": 0},
                "consult": {"chat": 0, "consult": 0, "alert": 0},
                "alert": {"chat": 0, "consult": 0, "alert": 0},
            },
            "latency_records": [],
            "bad_cases": [],
        }

    @property
    def model(self) -> ChatDashScope:
        if self._model is None:
            self._model = ChatDashScope(
                model=LLMConfig.CHAT_MODEL,
                dashscope_api_key=LLMConfig.DASHSCOPE_API_KEY,
                temperature=0.0,
                max_tokens=200,
            )
        return self._model

    def classify(self, user_message: str) -> Dict[str, Any]:
        """分类用户意图"""
        start_time = time.time()

        try:
            prompt = INTENT_CLASSIFY_PROMPT.format(user_message=user_message[:500])
            response = self.model.invoke([HumanMessage(content=prompt)])
            result_text = response.content if response.content else ""

            try:
                json_start = result_text.find("{")
                json_end = result_text.rfind("}") + 1
                if json_start >= 0 and json_end > json_start:
                    result = json.loads(result_text[json_start:json_end])
                else:
                    result = {"intent": "chat", "confidence": 0.5}
            except json.JSONDecodeError:
                result = {"intent": "chat", "confidence": 0.5}

        except Exception as e:
            logger.error(f"意图识别失败: {e}")
            result = {"intent": "chat", "confidence": 0.0, "error": str(e)}

        latency = (time.time() - start_time) * 1000
        self._metrics["latency_records"].append(latency)
        self._metrics["total_predictions"] += 1

        result["_latency_ms"] = round(latency, 2)
        return result

    def record_result(self, predicted: str, expected: str, user_message: str = ""):
        """记录分类结果"""
        # 更新混淆矩阵
        if predicted in self.INTENT_LABELS and expected in self.INTENT_LABELS:
            self._metrics["confusion_matrix"][expected][predicted] += 1

        if predicted == expected:
            self._metrics["correct_predictions"] += 1
        else:
            self._metrics["bad_cases"].append({
                "message": user_message[:200],
                "predicted": predicted,
                "expected": expected,
                "predicted_cn": self.INTENT_LABELS_CN.get(predicted, predicted),
                "expected_cn": self.INTENT_LABELS_CN.get(expected, expected),
            })

    def get_accuracy(self) -> float:
        """获取准确率"""
        if self._metrics["total_predictions"] == 0:
            return 0.0
        return self._metrics["correct_predictions"] / self._metrics["total_predictions"]

    def get_metrics(self) -> Dict[str, Any]:
        """获取分类器指标"""
        latencies = self._metrics["latency_records"]
        lat_data = {}
        if latencies:
            sorted_lat = sorted(latencies)
            lat_data = {
                "avg_latency_ms": round(sum(latencies) / len(latencies), 2),
                "p50_latency_ms": round(sorted_lat[int(len(sorted_lat) * 0.5)], 2),
                "p99_latency_ms": round(sorted_lat[int(len(sorted_lat) * 0.99)], 2),
            }

        return {
            "accuracy": round(self.get_accuracy() * 100, 1),
            "total_predictions": self._metrics["total_predictions"],
            "correct_predictions": self._metrics["correct_predictions"],
            "confusion_matrix": self._metrics["confusion_matrix"],
            "bad_cases_count": len(self._metrics["bad_cases"]),
            "bad_cases": self._metrics["bad_cases"][-10:],
            **lat_data,
        }


# 全局实例
intent_classifier = IntentClassifier()