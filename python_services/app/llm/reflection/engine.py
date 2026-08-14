"""
Agent 反思机制
在 Agent 输出后自动复查，检查是否存在：
- 事实错误（幻觉）
- 意图误判
- 风险等级不当
- 知识库使用不当
"""
from __future__ import annotations

import json
import logging
from typing import Any, Dict, Optional, Tuple

from langchain_core.prompts import ChatPromptTemplate
from langchain_dashscope import ChatDashScope

from app.llm.config import LLMConfig

logger = logging.getLogger(__name__)

# 反思提示词
REFLECTION_PROMPT = """你是一个反诈 Agent 的质量审核员。请审视以下 Agent 输出，检查是否存在问题。

【原始用户问题】
{user_message}

【Agent 意图判定】
{intent}

【Agent 输出】
{agent_output}

【知识库上下文】
{context}

【审核标准】
1. 事实检查：Agent 输出中是否有编造的信息？是否与知识库上下文矛盾？
2. 意图检查：Agent 的意图判定是否准确？是否误判了闲聊/咨询/诈骗？
3. 风险检查：如果涉及诈骗，风险等级判定是否恰当？
4. 合规检查：闲聊模式是否错误出现了反诈内容？咨询模式是否错误出现了风险警告？
5. 格式检查：是否使用了禁止的标签格式（如【风险等级】等）？

【审核结果】
请以 JSON 格式返回审核结果：
{{
    "has_issues": true/false,
    "issue_type": "事实错误/意图误判/风险不当/合规问题/格式问题/无",
    "issue_description": "具体问题描述",
    "correction": "修正建议（如有问题）",
    "confidence": 0.0-1.0
}}

审核结果："""


class ReflectionEngine:
    """反思引擎：在 Agent 输出后自动复查"""

    def __init__(self):
        self._model: Optional[ChatDashScope] = None

    @property
    def model(self) -> ChatDashScope:
        if self._model is None:
            self._model = ChatDashScope(
                model=LLMConfig.CHAT_MODEL,
                dashscope_api_key=LLMConfig.DASHSCOPE_API_KEY,
                temperature=0.1,  # 低温度，确保反思结果稳定
                max_tokens=500,
            )
        return self._model

    def reflect(
        self,
        user_message: str,
        agent_output: str,
        intent: str = "unknown",
        context: str = "",
    ) -> Dict[str, Any]:
        """
        反思 Agent 输出

        参数:
            user_message: 用户原始消息
            agent_output: Agent 输出
            intent: 意图判定结果
            context: 知识库上下文

        返回:
            {
                "has_issues": bool,
                "issue_type": str,
                "issue_description": str,
                "correction": str,
                "confidence": float,
                "original_output": str,
            }
        """
        if not LLMConfig.validate():
            return {
                "has_issues": False,
                "issue_type": "无",
                "issue_description": "API Key 未配置，跳过反思",
                "correction": "",
                "confidence": 1.0,
                "original_output": agent_output,
            }

        try:
            prompt = ChatPromptTemplate.from_messages([
                ("human", REFLECTION_PROMPT),
            ])

            chain = prompt | self.model
            response = chain.invoke({
                "user_message": user_message[:500],
                "intent": intent,
                "agent_output": agent_output[:1000],
                "context": context[:500] if context else "无知识库上下文",
            })

            result_text = response.content if response.content else ""

            try:
                json_start = result_text.find("{")
                json_end = result_text.rfind("}") + 1
                if json_start >= 0 and json_end > json_start:
                    json_str = result_text[json_start:json_end]
                    result = json.loads(json_str)
                else:
                    result = {
                        "has_issues": False,
                        "issue_type": "无",
                        "issue_description": "无法解析反思结果",
                        "correction": "",
                        "confidence": 0.5,
                    }
            except json.JSONDecodeError:
                result = {
                    "has_issues": False,
                    "issue_type": "无",
                    "issue_description": "反思结果解析失败",
                    "correction": "",
                    "confidence": 0.5,
                }

            result["original_output"] = agent_output

            if result.get("has_issues"):
                logger.warning(
                    f"反思发现问题: {result.get('issue_type')} - "
                    f"{result.get('issue_description', '')[:100]}"
                )
            else:
                logger.info("反思通过，未发现问题")

            return result

        except Exception as e:
            logger.error(f"反思失败: {e}")
            return {
                "has_issues": False,
                "issue_type": "反思异常",
                "issue_description": str(e),
                "correction": "",
                "confidence": 0,
                "original_output": agent_output,
            }

    def reflect_and_correct(
        self,
        user_message: str,
        agent_output: str,
        intent: str = "unknown",
        context: str = "",
        max_corrections: int = 2,
    ) -> Tuple[str, int]:
        """
        反思并修正输出（最多修正 max_corrections 次）

        返回: (修正后的输出, 修正次数)
        """
        current_output = agent_output
        corrections = 0

        for _ in range(max_corrections):
            reflection = self.reflect(
                user_message=user_message,
                agent_output=current_output,
                intent=intent,
                context=context,
            )

            if not reflection.get("has_issues"):
                break

            correction = reflection.get("correction", "")
            if not correction:
                break

            current_output = correction
            corrections += 1
            logger.info(f"反思修正 #{corrections}: {reflection.get('issue_type')}")

        return current_output, corrections


# 全局实例
reflection_engine = ReflectionEngine()