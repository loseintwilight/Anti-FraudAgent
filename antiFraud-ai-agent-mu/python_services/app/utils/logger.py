"""
日志工具模块
统一日志格式，支持文件和控制台输出
"""

import logging
import sys
from pathlib import Path

from ..config import settings


def setup_logger(name: str = "anti_fraud") -> logging.Logger:
    """
    初始化并返回配置好的日志器

    Args:
        name: 日志器名称

    Returns:
        配置好的 Logger 实例
    """
    logger = logging.getLogger(name)
    logger.setLevel(settings.LOG_LEVEL)

    # 避免重复添加 handler
    if logger.handlers:
        return logger

    # 控制台 handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(settings.LOG_LEVEL)
    console_formatter = logging.Formatter(settings.LOG_FORMAT)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # 文件 handler
    log_dir = Path(settings.BASE_DIR) / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    file_handler = logging.FileHandler(
        log_dir / "anti_fraud_service.log",
        encoding="utf-8"
    )
    file_handler.setLevel(settings.LOG_LEVEL)
    file_formatter = logging.Formatter(settings.LOG_FORMAT)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    return logger


# 全局日志器实例
logger = setup_logger()