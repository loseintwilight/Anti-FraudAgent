"""
通用新闻站点解析器
从各新闻网站提取反诈相关文章
"""

from __future__ import annotations

import logging
import re
from datetime import datetime
from typing import Any, Dict, List

from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# 反诈相关关键词
FRAUD_KEYWORDS = [
    "诈骗", "反诈", "电信网络诈骗", "电信诈骗", "网络诈骗",
    "冒充", "刷单", "杀猪盘", "套路贷", "非法集资",
    "洗钱", "帮信罪", "断卡", "预警", "劝返",
    "反电信网络诈骗法", "96110", "国家反诈中心",
]


def parse(html: str) -> List[Dict[str, Any]]:
    """
    解析通用新闻站点页面，提取反诈类文章

    参数:
        html: 页面 HTML 文本

    返回:
        文章列表，每篇包含 title, url, date, summary, content
    """
    logger.info("开始解析新闻站点页面")
    articles: List[Dict[str, Any]] = []

    try:
        soup = BeautifulSoup(html, "lxml")
    except Exception as e:
        logger.error(f"BeautifulSoup 解析失败: {e}")
        return articles

    # 尝试多种通用选择器
    article_items = []

    # 1. 常见文章列表结构
    selectors = [
        "article",
        "div.article",
        "div.news-item",
        "li.news-item",
        "div.list-item",
        "div.post-item",
        "div.item",
        "ul.list li",
        "div.news-list li",
        "div.content-list li",
    ]

    for selector in selectors:
        items = soup.select(selector)
        if items:
            article_items = items
            break

    # 2. 如果没找到，尝试从所有链接中提取
    if not article_items:
        all_links = soup.find_all("a", href=True)
        article_items = [
            link for link in all_links
            if link.get_text(strip=True) and len(link.get_text(strip=True)) > 10
        ]

    for item in article_items:
        try:
            # 提取标题
            title_elem = (
                item.find("h2")
                or item.find("h3")
                or item.find("h4")
                or item.find("a")
            )
            if title_elem is None:
                continue

            title = title_elem.get_text(strip=True)
            if not title or len(title) < 5:
                continue

            # 检查是否包含反诈关键词
            if not any(kw in title for kw in FRAUD_KEYWORDS):
                # 检查摘要中是否包含
                summary_elem = item.find("p", class_=re.compile(r"summary|desc|abstract"))
                if summary_elem:
                    summary_text = summary_elem.get_text(strip=True)
                    if not any(kw in summary_text for kw in FRAUD_KEYWORDS):
                        continue
                else:
                    continue

            # 提取链接
            link_elem = item.find("a") or title_elem
            href = ""
            if link_elem and link_elem.name == "a":
                href = link_elem.get("href", "")
            elif title_elem and title_elem.name == "a":
                href = title_elem.get("href", "")

            if not href:
                continue

            # 补全 URL
            if href.startswith("/"):
                href = f"https://news.sina.com.cn{href}"
            elif href.startswith("./"):
                href = f"https://news.sina.com.cn{href[1:]}"
            elif not href.startswith("http"):
                href = f"https://news.sina.com.cn/{href}"

            # 提取日期
            date_str = ""
            date_elem = (
                item.find("span", class_=re.compile(r"date|time|pub"))
                or item.find("time")
                or item.find("i", class_=re.compile(r"date|time"))
            )
            if date_elem:
                date_str = date_elem.get_text(strip=True)

            # 提取摘要
            summary = ""
            summary_elem = item.find("p", class_=re.compile(r"summary|desc|abstract"))
            if summary_elem:
                summary = summary_elem.get_text(strip=True)

            article = {
                "id": f"news_{datetime.now().strftime('%Y%m%d%H%M%S')}_{len(articles)}",
                "title": title,
                "url": href,
                "date": date_str,
                "summary": summary,
                "content": f"{title}。{summary}",
                "source": "news",
                "crawl_time": datetime.now().isoformat(),
            }
            articles.append(article)

        except Exception as e:
            logger.warning(f"解析单条新闻失败: {e}")
            continue

    logger.info(f"新闻站点解析完成: 获取 {len(articles)} 篇文章")
    return articles
