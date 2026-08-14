"""
爬虫进度管理器：支持断点续爬
"""
from __future__ import annotations

import json
import logging
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class CrawlProgressManager:
    """爬虫进度管理器：支持断点续爬"""

    def __init__(self, progress_dir: str = None):
        if progress_dir is None:
            progress_dir = os.path.join(
                os.path.dirname(__file__), "..", "..", "crawl_progress"
            )
        self.progress_dir = Path(progress_dir)
        self.progress_dir.mkdir(parents=True, exist_ok=True)

    def save_progress(self, task_id: str, completed_urls: List[str], total_urls: int) -> None:
        """保存爬取进度"""
        progress_file = self.progress_dir / f"{task_id}.json"
        progress = {
            "task_id": task_id,
            "total_urls": total_urls,
            "completed_urls": completed_urls,
            "completed_count": len(completed_urls),
            "status": "in_progress" if len(completed_urls) < total_urls else "completed",
            "last_updated": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        with open(progress_file, "w", encoding="utf-8") as f:
            json.dump(progress, f, ensure_ascii=False, indent=2)

    def load_progress(self, task_id: str) -> Optional[Dict[str, Any]]:
        """加载爬取进度"""
        progress_file = self.progress_dir / f"{task_id}.json"
        if not progress_file.exists():
            return None
        with open(progress_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_remaining_urls(self, task_id: str, all_urls: List[str]) -> List[str]:
        """获取待爬取的URL"""
        progress = self.load_progress(task_id)
        if progress is None:
            return all_urls
        completed = set(progress.get("completed_urls", []))
        return [url for url in all_urls if url not in completed]

    def mark_completed(self, task_id: str) -> None:
        """标记任务完成"""
        progress = self.load_progress(task_id)
        if progress:
            progress["status"] = "completed"
            progress["last_updated"] = time.strftime("%Y-%m-%d %H:%M:%S")
            progress_file = self.progress_dir / f"{task_id}.json"
            with open(progress_file, "w", encoding="utf-8") as f:
                json.dump(progress, f, ensure_ascii=False, indent=2)

    def cleanup_old_progress(self, max_age_days: int = 7) -> int:
        """清理过期进度文件"""
        deleted = 0
        cutoff = time.time() - max_age_days * 86400
        for progress_file in self.progress_dir.glob("*.json"):
            if progress_file.stat().st_mtime < cutoff:
                progress_file.unlink()
                deleted += 1
        return deleted


# 全局实例
progress_manager = CrawlProgressManager()