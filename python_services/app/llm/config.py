"""
LLM 配置模块
从环境变量或 .env 文件加载 API Key 和模型配置
"""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# 加载 .env 文件（如果存在）
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)


class LLMConfig:
    """LLM 统一配置"""

    # DashScope API Key
    DASHSCOPE_API_KEY: Optional[str] = os.getenv(
        "DASHSCOPE_API_KEY",
        os.getenv("DASH_SCOPE_API_KEY", ""),
    )

    # 对话模型
    CHAT_MODEL: str = os.getenv("LLM_CHAT_MODEL", "qwen-plus")

    # 嵌入模型
    EMBEDDING_MODEL: str = os.getenv("LLM_EMBEDDING_MODEL", "text-embedding-v2")

    # 视觉模型
    VISION_MODEL: str = os.getenv("LLM_VISION_MODEL", "qwen-vl-max")

    # 推理模型（用于复杂推理）
    REASONING_MODEL: str = os.getenv("LLM_REASONING_MODEL", "qwen-plus")

    # 温度参数
    TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.7"))

    # 最大 Token 数
    MAX_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", "2048"))

    # 向量存储路径
    VECTOR_STORE_PATH: str = os.getenv(
        "VECTOR_STORE_PATH",
        str(Path(__file__).resolve().parent.parent.parent / "chroma_db"),
    )

    @classmethod
    def validate(cls) -> bool:
        """验证配置是否有效"""
        if not cls.DASHSCOPE_API_KEY:
            print("⚠️ DASHSCOPE_API_KEY 未配置，AI 对话功能将不可用")
            return False
        return True