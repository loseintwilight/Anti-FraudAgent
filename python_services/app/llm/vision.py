"""
视觉大模型分析模块
基于 LangChain DashScope 实现图片分析
替代 Spring AI 的 AiController.analyzeImageWithVisionModel
"""

import base64
import logging
from typing import Any, Dict, List, Optional

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
        # 重依赖延迟加载：类型标注用 Any，避免在模块导入时引用未安装的 SDK
        self._model: Optional[Any] = None

    @property
    def model(self) -> Any:
        if self._model is None:
            from langchain_dashscope import ChatDashScope
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

            # 构建消息（支持多模态内容）；重依赖在此处才加载
            from langchain_core.messages import HumanMessage
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

    def describe_image(
        self,
        image_base64: str,
        prompt: Optional[str] = None,
    ) -> str:
        """
        返回单张图片的文字描述（复用视觉模型调用）。
        模型不可用 / 未配置 Key / 返回空结果时返回空串，绝不返回预置话术。
        """
        result = self.analyze_image(image_base64, prompt=prompt)
        return result.get("text", "") if result.get("success") else ""

    def analyze_frames(
        self,
        frames_base64: List[str],
        prompt: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """逐帧分析视频帧列表，复用单图视觉模型调用。"""
        out: List[Dict[str, Any]] = []
        for idx, frame in enumerate(frames_base64):
            result = self.analyze_image(frame, prompt=prompt)
            out.append({
                "index": idx,
                "success": bool(result.get("success")),
                "text": result.get("text", ""),
                "error": result.get("error"),
            })
        return out


# 全局单例（构造轻量，模型仅在首次调用时才加载）
vision_analyzer = VisionAnalyzer()
