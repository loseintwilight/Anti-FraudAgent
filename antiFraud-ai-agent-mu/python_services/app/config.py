"""
应用配置模块
从环境变量或 .env 文件读取配置，禁止硬编码敏感信息
"""

import os
import logging
from pathlib import Path
from typing import Optional

# 项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent


class Settings:
    """应用全局配置，所有配置项集中管理"""

    def __init__(self):
        # ---------- DeepSeek API 配置 ----------
        self.DEEPSEEK_API_KEY: str = os.getenv(
            "DEEPSEEK_API_KEY",
            "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"  # 请替换为实际 API Key 或通过环境变量注入
        )
        self.DEEPSEEK_API_BASE: str = os.getenv(
            "DEEPSEEK_API_BASE",
            "https://api.deepseek.com/v1"
        )
        self.DEEPSEEK_MODEL: str = os.getenv(
            "DEEPSEEK_MODEL",
            "deepseek-chat"
        )
        self.DEEPSEEK_TIMEOUT: int = int(os.getenv("DEEPSEEK_TIMEOUT", "60"))
        self.DEEPSEEK_MAX_RETRIES: int = int(os.getenv("DEEPSEEK_MAX_RETRIES", "3"))
        self.DEEPSEEK_RETRY_DELAY: float = float(os.getenv("DEEPSEEK_RETRY_DELAY", "1.0"))
        self.DEEPSEEK_MAX_TOKENS: int = int(os.getenv("DEEPSEEK_MAX_TOKENS", "2048"))
        self.DEEPSEEK_TEMPERATURE: float = float(os.getenv("DEEPSEEK_TEMPERATURE", "0.7"))

        # ---------- FastAPI 服务配置 ----------
        self.SERVICE_HOST: str = os.getenv("SERVICE_HOST", "0.0.0.0")
        self.SERVICE_PORT: int = int(os.getenv("SERVICE_PORT", "8501"))
        self.SERVICE_NAME: str = "AI反诈智能体-Python辅助服务"
        self.SERVICE_VERSION: str = "1.0.0"
        self.DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

        # ---------- 知识库配置 ----------
        # 知识库检索置信度阈值，低于此值降级到大模型
        self.KB_CONFIDENCE_THRESHOLD: float = float(
            os.getenv("KB_CONFIDENCE_THRESHOLD", "0.6")
        )
        # 知识库最多返回的匹配结果数
        self.KB_MAX_RESULTS: int = int(os.getenv("KB_MAX_RESULTS", "5"))

        # ---------- 对话上下文配置 ----------
        # 保留的最大对话轮次
        self.MAX_CONVERSATION_TURNS: int = int(
            os.getenv("MAX_CONVERSATION_TURNS", "20")
        )
        # 上下文内存文件存储路径
        self.CONTEXT_STORAGE_PATH: str = os.getenv(
            "CONTEXT_STORAGE_PATH",
            str(BASE_DIR / "data" / "conversations")
        )

        # ---------- 报告生成配置 ----------
        self.REPORT_OUTPUT_PATH: str = os.getenv(
            "REPORT_OUTPUT_PATH",
            str(BASE_DIR / "data" / "reports")
        )
        # 报告图片字体路径（Windows 用 msyh.ttc，Linux 需自行安装）
        self.REPORT_FONT_PATH: str = os.getenv(
            "REPORT_FONT_PATH",
            "C:/Windows/Fonts/msyh.ttc"
        )

        # ---------- 日志配置 ----------
        self.LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()
        self.LOG_FORMAT: str = (
            "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s"
        )

    def ensure_dirs(self):
        """确保必要的目录存在"""
        dirs = [
            self.CONTEXT_STORAGE_PATH,
            self.REPORT_OUTPUT_PATH,
            BASE_DIR / "logs",
        ]
        for d in dirs:
            Path(d).mkdir(parents=True, exist_ok=True)


# 全局单例
settings = Settings()