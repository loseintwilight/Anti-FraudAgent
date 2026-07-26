"""
视觉大模型分析模块
基于 LangChain DashScope 实现图片分析
替代 Spring AI 的 AiController.analyzeImageWithVisionModel
"""

import base64
import logging
from typing import Any, Dict, Optional

from langchain_core.messages import HumanMessage
from langchain_dashscope import ChatDashScope

from app.llm.config import LLMConfig

logger = logging.getLogger(__name__)

# 视觉分析提示词
VISION_PROMPT = """
【重要】你是一个专业的OCR文字识别助手。请严格按照以下步骤分析图片：

第一步：逐字读取并输出图片中可见的 ALL 文字内容
- 包括大标题、小标题、正文、按钮文字、水印文字等
- 如果文字模糊或较小，请尽力辨认
- 按原文格式输出，不要省略、不要概括、不要猜测

第二步：描述图片场景
- 图片中有哪些人物、物品、环境

第三步：基于实际提取的文字判断诈骗类型
- 根据第一步提取的真实文字内容判断
- 不要根据画面外观猜测

输出格式要求：
=== 图片文字（原样输出）===
（这里填写第一步提取的所有文字）

=== 场景描述 ===
（这里填写第二步的场景描述）

=== 诈骗类型判断 ===
（这里填写基于文字内容的判断）
"""


class VisionAnalyzer:
    """
    图片分析器
    使用 qwen-vl-max 视觉模型分析图片
    """

    def __init__(self):
        self._model: Optional[ChatDashScope] = None

    @property
    def model(self) -> ChatDashScope:
        if self._model is None:
            self._model = ChatDashScope(
                model=LLMConfig.VISION_MODEL,
                dashscope_api_key=LLMConfig.DASHSCOPE_API_KEY,
                temperature=0.1,
                max_tokens=2048,
            )
        return self._model

    def analyze_image(
        self,
        image_base64: str,
        prompt: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        分析图片内容

        参数:
            image_base64: Base64 编码的图片数据
            prompt: 自定义提示词（可选，默认使用 VISION_PROMPT）

        返回:
            {"success": bool, "text": str, "error": Optional[str]}
        """
        if not LLMConfig.validate():
            return {
                "success": False,
                "text": "",
                "error": "DASHSCOPE_API_KEY 未配置",
            }

        if not image_base64:
            return {
                "success": False,
                "text": "",
                "error": "图片数据为空",
            }

        try:
            # 构建图片数据 URI
            image_data_url = f"data:image/jpeg;base64,{image_base64}"

            # 使用提示词
            user_prompt = prompt or VISION_PROMPT

            # 构建消息（支持多模态内容）
            msg = HumanMessage(
                content=[
                    {"type": "text", "text": user_prompt},
                    {"type": "image_url", "image_url": {"url": image_data_url}},
                ]
            )

            logger.info("调用视觉大模型 qwen-vl-max 进行图片分析...")
            response = self.model.invoke([msg])

            result_text = response.content if response.content else ""

            if result_text:
                logger.info(f"视觉大模型分析成功，结果长度: {len(result_text)}")
                return {"success": True, "text": result_text, "error": None}
            else:
                logger.warning("视觉大模型返回空结果")
                return {
                    "success": False,
                    "text": "图片内容分析中遇到问题，请尝试手动描述图片内容。",
                    "error": "模型返回空结果",
                }

        except Exception as e:
            logger.error(f"视觉大模型分析失败: {e}", exc_info=True)
            return {
                "success": False,
                "text": "图片内容分析中遇到问题，请尝试手动描述图片内容。",
                "error": str(e),
            }