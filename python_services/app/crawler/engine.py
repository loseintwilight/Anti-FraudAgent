"""
通用爬虫引擎
基于 requests + BeautifulSoup 实现通用爬虫框架
支持多源爬取、请求重试、解析回调
"""

from __future__ import annotations

import logging
import time
from typing import Any, Callable, Dict, List, Optional

import requests
from bs4 import BeautifulSoup

from app.crawler.parsers import mps_gov, news_sites

logger = logging.getLogger(__name__)

# 默认请求头
DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}

# 请求超时（秒）
REQUEST_TIMEOUT = 15

# 最大重试次数
MAX_RETRIES = 3

# 请求间隔（秒）
REQUEST_INTERVAL = 2.0


class CrawlerEngine:
    """
    通用爬虫引擎
    支持注册解析器、发起请求、解析内容、存储结果
    """

    def __init__(self) -> None:
        """初始化爬虫引擎"""
        self.session = requests.Session()
        self.session.headers.update(DEFAULT_HEADERS)
        self.parsers: Dict[str, Callable[[str], List[Dict[str, Any]]]] = {}

        # 注册默认解析器
        self._register_default_parsers()

    def _register_default_parsers(self) -> None:
        """注册默认的站点解析器"""
        self.register_parser("mps_gov", mps_gov.parse)
        self.register_parser("news", news_sites.parse)

    def register_parser(
        self, name: str, parser_func: Callable[[str], List[Dict[str, Any]]]
    ) -> None:
        """
        注册一个解析器

        参数:
            name: 解析器名称
            parser_func: 解析函数，接收 HTML 文本，返回文章列表
        """
        self.parsers[name] = parser_func
        logger.info(f"注册解析器: {name}")

    def fetch(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        retries: int = MAX_RETRIES,
    ) -> Optional[str]:
        """
        获取 URL 内容
        支持自动重试

        参数:
            url: 目标 URL
            params: URL 参数字典
            retries: 重试次数

        返回:
            HTML 文本，若失败返回 None
        """
        last_error = None
        for attempt in range(1, retries + 1):
            try:
                logger.info(f"请求URL: {url} (尝试 {attempt}/{retries})")
                resp = self.session.get(
                    url, params=params, timeout=REQUEST_TIMEOUT
                )
                resp.raise_for_status()
                resp.encoding = resp.apparent_encoding

                # 请求间隔，避免对服务器造成压力
                if attempt < retries:
                    time.sleep(REQUEST_INTERVAL)

                return resp.text
            except requests.exceptions.Timeout as e:
                last_error = f"请求超时: {e}"
                logger.warning(f"超时重试 {attempt}/{retries}: {url}")
                time.sleep(REQUEST_INTERVAL * 2)
            except requests.exceptions.HTTPError as e:
                last_error = f"HTTP错误: {e}"
                logger.warning(f"HTTP错误重试 {attempt}/{retries}: {e}")
                time.sleep(REQUEST_INTERVAL)
            except requests.exceptions.RequestException as e:
                last_error = f"请求异常: {e}"
                logger.warning(f"请求异常重试 {attempt}/{retries}: {e}")
                time.sleep(REQUEST_INTERVAL)

        logger.error(f"所有重试失败: {url}, 错误: {last_error}")
        return None

    def parse_html(self, html: str) -> BeautifulSoup:
        """将 HTML 文本解析为 BeautifulSoup 对象"""
        return BeautifulSoup(html, "lxml")

    def crawl(self, source: str = "all") -> Dict[str, Any]:
        """
        执行爬取任务

        参数:
            source: 爬取来源，可选 mps_gov / news / all，默认为 all

        返回:
            {
                "sources_crawled": List[str],
                "articles_found": int,
                "sources": Dict[str, List[Dict]]
            }
        """
        logger.info(f"开始爬取任务: source={source}")

        sources_to_crawl: List[str] = []
        if source == "all":
            # 获取所有已注册解析器的来源 URL
            sources_to_crawl = self._get_all_source_urls()
        elif source in self.parsers:
            # 获取特定来源的 URL
            source_urls = self._get_source_urls(source)
            sources_to_crawl = source_urls
        else:
            logger.warning(f"未知爬取来源: {source}")
            return {"sources_crawled": [], "articles_found": 0, "sources": {}}

        results: Dict[str, List[Dict[str, Any]]] = {}

        for url_info in sources_to_crawl:
            parser_name = url_info.get("parser", "news")
            url = url_info.get("url", "")
            params = url_info.get("params")

            if not url:
                continue

            # 获取页面内容
            html = self.fetch(url, params=params)
            if html is None:
                logger.error(f"获取页面失败: {url}")
                continue

            # 使用对应的解析器解析内容
            parser_func = self.parsers.get(parser_name)
            if parser_func is None:
                logger.warning(f"未找到解析器: {parser_name}")
                continue

            try:
                articles = parser_func(html)
                if parser_name not in results:
                    results[parser_name] = []
                results[parser_name].extend(articles)
                logger.info(
                    f"解析完成: parser={parser_name}, articles={len(articles)}"
                )
            except Exception as e:
                logger.exception(f"解析失败: parser={parser_name}, error={e}")

            # 请求间隔
            time.sleep(REQUEST_INTERVAL)

        total_articles = sum(len(v) for v in results.values())
        logger.info(f"爬取完成: sources={list(results.keys())}, total={total_articles}")

        return {
            "sources_crawled": list(results.keys()),
            "articles_found": total_articles,
            "sources": results,
        }

    def _get_all_source_urls(self) -> List[Dict[str, Any]]:
        """获取所有爬取来源的 URL 列表"""
        urls = []
        for parser_name in self.parsers:
            urls.extend(self._get_source_urls(parser_name))
        return urls

    @staticmethod
    def _get_source_urls(parser_name: str) -> List[Dict[str, Any]]:
        """获取指定来源的 URL 配置"""
        if parser_name == "mps_gov":
            return [
                {
                    "url": "https://www.mps.gov.cn/n2255079/index.html",
                    "parser": "mps_gov",
                    "params": None,
                }
            ]
        elif parser_name == "news":
            return [
                {
                    "url": "https://news.sina.com.cn/c/2024-01-01/doc-xxxxx.shtml",
                    "parser": "news",
                    "params": None,
                }
            ]
        return []
