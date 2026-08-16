"""
工具调用追踪器
"""
from __future__ import annotations

import logging
import time
from typing import Any, Dict

logger = logging.getLogger(__name__)


class ToolCallTracker:
    """工具调用追踪器"""

    def __init__(self):
        self.executed_ids: Dict[str, float] = {}
        self.failure_log: list = []

    def is_duplicate(self, execution_id: str) -> bool:
        """检查是否重复执行"""
        return execution_id in self.executed_ids

    def mark_executed(self, execution_id: str):
        """标记执行完成"""
        self.executed_ids[execution_id] = time.time()

    def log_failure(self, tool_name: str, execution_id: str, error: str, context: Dict):
        """记录失败日志"""
        self.failure_log.append({
            "tool_name": tool_name,
            "execution_id": execution_id,
            "error": error,
            "context": context,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        })

    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            "total_executed": len(self.executed_ids),
            "total_failures": len(self.failure_log),
            "recent_failures": self.failure_log[-10:] if self.failure_log else [],
        }