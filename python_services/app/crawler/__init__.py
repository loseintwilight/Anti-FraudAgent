"""
AI爬虫模块
- 可插拔语义过滤（规则 / 模型双模式，未配置模型时按规则如实标注）
- 断点续爬进度管理
"""
from app.crawler.keyword_filter import (
    AIContentFilter,
    NOISE_KEYWORDS,
    VALID_ANTI_FRAUD_KEYWORDS,
    content_filter,
)
from app.crawler.progress_manager import CrawlProgressManager, progress_manager

__all__ = [
    "AIContentFilter",
    "NOISE_KEYWORDS",
    "VALID_ANTI_FRAUD_KEYWORDS",
    "content_filter",
    "CrawlProgressManager",
    "progress_manager",
]