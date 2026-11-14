"""
集中式指标追踪系统
所有简历中宣称的量化数字都在此记录和产出
- 留痕迹记录数字的产出
- 每个指标都有来源、计算方式和时间戳
"""
from __future__ import annotations

import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)

# 指标存储目录
METRICS_DIR = Path(__file__).resolve().parent.parent.parent / "metrics_data"
METRICS_DIR.mkdir(parents=True, exist_ok=True)


class MetricsTracker:
    """集中式指标追踪器 — 简历中所有数字的单一来源"""

    def __init__(self):
        self._metrics: Dict[str, Any] = self._load_metrics()
        self._session_start = time.time()

    def _metrics_file(self) -> Path:
        return METRICS_DIR / "project_metrics.json"

    def get_all_metrics(self) -> Dict[str, Any]:
        """返回所有真实存在的指标；知识条目数按向量库实际 count 注入。"""
        metrics = _collect_metrics()
        metrics["knowledge_entries"] = _knowledge_entries()
        return metrics

    def generate_report(self) -> Dict[str, Any]:
        """只呈现评测产物里真实存在的结果，缺失项标注数据不足。"""
        metrics = self.get_all_metrics()
        reasons = _insufficient_reasons()
        reasons.setdefault(
            "knowledge_entries", "向量库不可用或为空，collection_count() 返回 None"
        )
        measured = {k: v for k, v in metrics.items() if v is not None}
        insufficient = {
            k: reasons.get(k, "评测产物中该指标为 null，无原始实验日志支撑")
            for k, v in metrics.items()
            if v is None
        }
        return {
            "measured": measured,
            "insufficient": insufficient,
            "sources": sorted(_read_result_files().keys()),
        }

    # --- 兼容既有调用：指标源为评测产物，运行时写入不改变指标源 ---
    def update_metric(
        self, category: str, metric_name: str, value: Any, note: str = ""
    ) -> None:
        logger.debug("指标源为评测产物: %s/%s", category, metric_name)

    def record_eval_result(self, eval_name: str, metrics: Dict[str, Any]) -> None:
        logger.debug("指标源为评测产物: %s", eval_name)

    def save(self) -> None:
        logger.debug("指标源为评测产物，无需持久化运行时状态")


# 全局实例
metrics_tracker = MetricsTracker()
