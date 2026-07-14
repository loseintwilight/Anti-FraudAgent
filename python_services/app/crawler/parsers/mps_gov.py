"""
公安部刑侦局（MPS）文章解析器
从公安部网站提取反诈相关文章
"""

from __future__ import annotations

import logging
import re
from datetime import datetime
from typing import Any, Dict, List

from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# 反诈关键词过滤
FRAUD_KEYWORDS = [
    "诈骗", "反诈", "电信网络诈骗", "电信诈骗", "网络诈骗",
    "冒充", "刷单", "杀猪盘", "套路贷", "非法集资",
    "洗钱", "帮信罪", "断卡", "预警", "劝返",
]


def parse(html: str) -> List[Dict[str, Any]]:
    """
    解析公安部刑侦局页面，提取反诈类文章列表

    参数:
        html: 页面 HTML 文本

    返回:
        文章列表，每篇包含 title, url, date, summary, content
    """
    logger.info("开始解析公安部刑侦局页面")
    articles: List[Dict[str, Any]] = []

    try:
        soup = BeautifulSoup(html, "lxml")
    except Exception as e:
        logger.error(f"BeautifulSoup 解析失败: {e}")
        return articles

    # 尝试多种选择器匹配文章列表
    # 公安部网站常见结构
    article_items = (
        soup.select("ul.list-list li a")
        or soup.select(".news-list li a")
        or soup.select("div.news-content a")
        or soup.select("a[href*='.shtml']")
    )

    if not article_items:
        # 尝试更通用的选择
        article_items = soup.find_all("a", href=re.compile(r"\.shtml$"))

    for item in article_items:
        try:
            title = item.get_text(strip=True)
            href = item.get("href", "")

            if not title or not href:
                continue

            # 只保留含反诈关键词的文章
            if not any(kw in title for kw in FRAUD_KEYWORDS):
                continue

            # 补全 URL
            if href.startswith("/"):
                href = f"https://www.mps.gov.cn{href}"
            elif href.startswith("./"):
                href = f"https://www.mps.gov.cn{href[1:]}"
            elif not href.startswith("http"):
                href = f"https://www.mps.gov.cn/{href}"

            # 提取日期（通常包含在列表项中）
            date_str = ""
            parent = item.parent
            if parent:
                date_elem = parent.find("span", class_=re.compile(r"date|time"))
                if date_elem:
                    date_str = date_elem.get_text(strip=True)

            article = {
                "id": f"mps_{datetime.now().strftime('%Y%m%d%H%M%S')}_{len(articles)}",
                "title": title,
                "url": href,
                "date": date_str,
                "content": title,  # 完整内容需进一步抓取详情页
                "source": "mps_gov",
                "crawl_time": datetime.now().isoformat(),
            }
            articles.append(article)

        except Exception as e:
            logger.warning(f"解析单条文章失败: {e}")
            continue

    logger.info(f"公安部刑侦局解析完成: 获取 {len(articles)} 篇文章")
    return articles
