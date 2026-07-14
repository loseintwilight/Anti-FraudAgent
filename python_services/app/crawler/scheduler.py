"""
定时爬虫调度器
使用 schedule 库实现每 6 小时自动定时爬取

调度流程:
  1. 每 6 小时触发一次爬取任务
  2. 爬取结果写入 vector_store (ChromaDB)
  3. 支持手动立即触发
"""

from __future__ import annotations

import logging
import time
from datetime import datetime
from threading import Event, Thread
from typing import Any, Dict, Optional

try:
    import schedule
except ImportError:
    schedule = None  # type: ignore

from app.crawler.engine import CrawlerEngine

logger = logging.getLogger(__name__)

# 默认调度间隔（秒）
DEFAULT_INTERVAL_HOURS = 6


class CrawlerScheduler:
    """
    爬虫定时调度器
    支持后台线程定时执行爬取任务
    """

    def __init__(
        self,
        interval_hours: int = DEFAULT_INTERVAL_HOURS,
        auto_start: bool = False,
    ) -> None:
        """
        初始化调度器

        参数:
            interval_hours: 调度间隔（小时），默认 6
            auto_start: 是否自动启动调度
        """
        self.interval_hours = interval_hours
        self._thread: Optional[Thread] = None
        self._stop_event = Event()
        self._engine = CrawlerEngine()
        self._last_run: Optional[str] = None
        self._last_result: Optional[Dict[str, Any]] = None
        self._running = False

        if auto_start:
            self.start()

    def start(self) -> None:
        """在后台线程中启动定时调度"""
        if schedule is None:
            logger.error("schedule 库未安装，无法启动定时调度")
            return

        if self._running:
            logger.warning("调度器已在运行中")
            return

        self._running = True
        self._stop_event.clear()
        self._thread = Thread(target=self._run_loop, daemon=True, name="CrawlerScheduler")
        self._thread.start()
        logger.info(
            f"爬虫调度器已启动: 每 {self.interval_hours} 小时执行一次"
        )

    def stop(self) -> None:
        """停止定时调度"""
        self._stop_event.set()
        self._running = False
        if self._thread:
            self._thread.join(timeout=5.0)
        logger.info("爬虫调度器已停止")

    def trigger_now(self, source: str = "all") -> Dict[str, Any]:
        """
        立即触发爬取任务（不等待定时）

        参数:
            source: 爬取来源

        返回:
            爬取结果字典
        """
        logger.info(f"手动触发爬取: source={source}")
        result = self._engine.crawl(source=source)
        self._last_run = datetime.now().isoformat()
        self._last_result = result

        # 爬取结果写入向量存储
        self._store_results(result)

        return result

    def _run_loop(self) -> None:
        """调度主循环"""
        if schedule is None:
            return

        # 配置定时任务
        schedule.every(self.interval_hours).hours.do(self._scheduled_task)

        # 启动时立即执行一次
        logger.info("调度器启动，立即执行首次爬取...")
        self._scheduled_task()

        # 循环检查定时任务
        while not self._stop_event.is_set():
            schedule.run_pending()
            self._stop_event.wait(30)  # 每 30 秒检查一次

        logger.info("调度器循环已退出")

    def _scheduled_task(self) -> None:
        """定时执行的任务"""
        try:
            logger.info(
                f"定时爬取任务开始: 间隔={self.interval_hours}小时"
            )
            result = self._engine.crawl(source="all")
            self._last_run = datetime.now().isoformat()
            self._last_result = result

            # 爬取结果写入向量存储
            self._store_results(result)

            logger.info(
                f"定时爬取任务完成: "
                f"来源={result['sources_crawled']}, "
                f"文章数={result['articles_found']}"
            )
        except Exception as e:
            logger.exception(f"定时爬取任务失败: {e}")

    def _store_results(self, result: Dict[str, Any]) -> None:
        """
        将爬取结果存储到向量数据库

        参数:
            result: 爬取结果字典
        """
        try:
            from app.vector_store.embedder import TextEmbedder
            from app.vector_store.retriever import VectorRetriever

            embedder = TextEmbedder()
            retriever = VectorRetriever()

            sources = result.get("sources", {})
            for parser_name, articles in sources.items():
                for article in articles:
                    text = article.get("content", "") or article.get("title", "")
                    if not text:
                        continue

                    # 生成向量
                    embedding = embedder.embed(text)

                    # 存储到 ChromaDB
                    retriever.add_document(
                        document_id=article.get("id", ""),
                        text=text,
                        metadata={
                            "title": article.get("title", ""),
                            "source": parser_name,
                            "url": article.get("url", ""),
                            "date": article.get("date", ""),
                        },
                        embedding=embedding,
                    )

            logger.info(
                f"爬取结果已写入向量存储: "
                f"{sum(len(v) for v in sources.values())} 篇文档"
            )
        except ImportError as e:
            logger.warning(f"向量存储模块不可用，跳过写入: {e}")
        except Exception as e:
            logger.exception(f"写入向量存储失败: {e}")

    @property
    def status(self) -> Dict[str, Any]:
        """获取调度器当前状态"""
        return {
            "running": self._running,
            "interval_hours": self.interval_hours,
            "last_run": self._last_run,
            "last_result": self._last_result,
        }
