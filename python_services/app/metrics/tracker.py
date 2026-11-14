"""
指标读取视图
集中读取 evaluation/results/ 下由评测脚本产出的确定性评测结果。
指标的唯一数据源是评测产物；缺失字段一律返回 None，不提供默认值。
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# 评测产物目录（results/*.json 是唯一指标数据源）
RESULTS_DIR = Path(__file__).resolve().parent.parent.parent / "evaluation" / "results"

# 汇总报告文件不参与指标合并
_REPORT_FILENAME = "metrics_report.json"


def _read_result_files() -> Dict[str, Dict[str, Any]]:
    """读取 results 目录下所有评测产物，返回 {文件名: 内容}。"""
    out: Dict[str, Dict[str, Any]] = {}
    if not RESULTS_DIR.is_dir():
        return out
    for path in sorted(RESULTS_DIR.glob("*.json")):
        if path.name == _REPORT_FILENAME:
            continue
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, ValueError) as e:
            logger.warning("评测产物读取失败: %s (%s)", path.name, e)
            continue
        if isinstance(data, dict):
            out[path.name] = data
    return out


def _collect_metrics() -> Dict[str, Any]:
    """合并所有评测产物中的 metrics 字段。"""
    merged: Dict[str, Any] = {}
    for data in _read_result_files().values():
        metrics = data.get("metrics")
        if isinstance(metrics, dict):
            for key, value in metrics.items():
                merged[key] = value
    return merged


def _insufficient_reasons() -> Dict[str, str]:
    """汇总各产物中标注为数据不足的原因。"""
    reasons: Dict[str, str] = {}
    for data in _read_result_files().values():
        insufficient = data.get("insufficient")
        if isinstance(insufficient, dict):
            reasons.update(
                {k: v for k, v in insufficient.items() if isinstance(v, str)}
            )
    return reasons


def _knowledge_entries() -> Optional[int]:
    """知识条目数取自向量库实际 count；客户端不可用 / 空库返回 None。"""
    try:
        from app.vector_store.hybrid import collection_count
    except Exception:
        return None
    try:
        count = collection_count()
    except Exception:
        return None
    return count if isinstance(count, int) else None


class MetricsTracker:
    """评测产物驱动的指标视图：只读取 results/*.json，缺字段返回 None。"""

    def __init__(self) -> None:
        self._results_dir = RESULTS_DIR

    def get_metric(self, name: str) -> Any:
        """取单个指标；不存在返回 None。"""
        return _collect_metrics().get(name)

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
