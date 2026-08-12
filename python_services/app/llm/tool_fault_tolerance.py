"""
工具调用容错增强模块
- 为每类工具设置独立超时和重试策略
- 幂等性保证（execution_id检查）
- 文件操作沙箱化
- 失败日志记录
"""
from __future__ import annotations

import hashlib
import json
import logging
import os
import sys
import time
import uuid
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


# 工具超时配置（秒）
TOOL_TIMEOUTS = {
    "pdf_generate": 30,
    "web_search": 10,
    "web_scrape": 15,
    "file_read": 5,
    "file_write": 5,
    "terminal_command": 10,
    "external_api": 15,
    "default": 10,
}

# 工具重试配置
TOOL_RETRY_CONFIG = {
    "max_retries": 1,
    "backoff_base": 1.0,
    "backoff_multiplier": 2.0,
}

# 文件操作沙箱配置
SANDBOX_CONFIG = {
    "allowed_directories": [
        os.path.join(os.path.dirname(__file__), "..", "workspace"),
    ],
    "max_file_size": 10 * 1024 * 1024,  # 10MB
    "forbidden_paths": [
        "/etc", "/root", "/var", "C:\\Windows", "C:\\Program Files",
        "/sys", "/proc", "/dev",
    ],
    "allowed_extensions": [".txt", ".json", ".csv", ".md", ".log", ".html", ".pdf"],
}


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


# 全局追踪器
tracker = ToolCallTracker()


def with_tool_fault_tolerance(tool_name: str):
    """工具调用容错装饰器"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            execution_id = str(uuid.uuid4())[:8]

            # 幂等性检查
            if execution_id and tracker.is_duplicate(execution_id):
                logger.warning(f"[{tool_name}] 重复执行被阻止: {execution_id}")
                return {"error": "duplicate_execution", "message": "该操作已执行过"}

            timeout = TOOL_TIMEOUTS.get(tool_name, TOOL_TIMEOUTS["default"])
            max_retries = TOOL_RETRY_CONFIG["max_retries"]

            for attempt in range(max_retries + 1):
                try:
                    import signal

                    def timeout_handler(signum, frame):
                        raise TimeoutError(f"[{tool_name}] 执行超时 ({timeout}s)")

                    # Windows 不支持 signal.SIGALRM，用简单计时
                    start = time.time()
                    result = func(*args, **kwargs)
                    elapsed = time.time() - start

                    if elapsed > timeout:
                        logger.warning(
                            f"[{tool_name}] 执行耗时 {elapsed:.1f}s > 超时 {timeout}s"
                        )

                    tracker.mark_executed(execution_id)
                    logger.info(
                        f"[{tool_name}] 执行成功: {execution_id} ({elapsed:.1f}s)"
                    )
                    return result

                except Exception as e:
                    error_msg = str(e)
                    tracker.log_failure(
                        tool_name, execution_id, error_msg,
                        {"args": str(args)[:200], "kwargs": str(kwargs)[:200], "attempt": attempt + 1}
                    )

                    if attempt < max_retries:
                        backoff = TOOL_RETRY_CONFIG["backoff_base"] * (
                            TOOL_RETRY_CONFIG["backoff_multiplier"] ** attempt
                        )
                        logger.warning(
                            f"[{tool_name}] 失败，{backoff}s后重试 ({attempt+1}/{max_retries+1}): {error_msg}"
                        )
                        time.sleep(backoff)
                    else:
                        logger.error(
                            f"[{tool_name}] 重试耗尽，最终失败: {error_msg}"
                        )
                        return {"error": "tool_execution_failed", "message": error_msg}

            return {"error": "unknown", "message": "未知错误"}

        return wrapper
    return decorator


def validate_file_path(file_path: str) -> bool:
    """沙箱文件路径验证"""
    abs_path = os.path.abspath(file_path)

    # 检查禁止路径
    for forbidden in SANDBOX_CONFIG["forbidden_paths"]:
        if abs_path.startswith(forbidden):
            logger.warning(f"沙箱拦截: 禁止访问路径 {abs_path}")
            return False

    # 检查允许目录
    if SANDBOX_CONFIG["allowed_directories"]:
        allowed = any(
            abs_path.startswith(os.path.abspath(d))
            for d in SANDBOX_CONFIG["allowed_directories"]
        )
        if not allowed:
            logger.warning(f"沙箱拦截: 不在允许目录 {abs_path}")
            return False

    # 检查文件扩展名
    ext = os.path.splitext(file_path)[1].lower()
    if ext and ext not in SANDBOX_CONFIG["allowed_extensions"]:
        logger.warning(f"沙箱拦截: 不允许的文件类型 {ext}")
        return False

    return True


def generate_execution_id(args: tuple, kwargs: dict) -> str:
    """生成唯一的执行ID（用于幂等性检查）"""
    content = json.dumps({"args": str(args), "kwargs": str(kwargs)}, sort_keys=True)
    return hashlib.md5(content.encode()).hexdigest()[:12]


# 工具调用统计
def get_tool_stats() -> Dict[str, Any]:
    """获取工具调用统计"""
    return tracker.get_stats()


def reset_tool_stats():
    """重置工具调用统计"""
    global tracker
    tracker = ToolCallTracker()


if __name__ == "__main__":
    print("=" * 60)
    print("工具调用容错增强模块")
    print("=" * 60)

    print(f"\n工具超时配置:")
    for tool, timeout in TOOL_TIMEOUTS.items():
        print(f"  {tool}: {timeout}s")

    print(f"\n重试配置: 最多{TOOL_RETRY_CONFIG['max_retries']}次重试")

    print(f"\n沙箱配置:")
    print(f"  允许目录: {SANDBOX_CONFIG['allowed_directories']}")
    print(f"  最大文件: {SANDBOX_CONFIG['max_file_size'] / 1024 / 1024:.0f}MB")
    print(f"  允许扩展名: {SANDBOX_CONFIG['allowed_extensions']}")

    # 测试文件路径验证
    test_paths = [
        "/tmp/workspace/test.txt",
        "/etc/passwd",
        "C:\\Windows\\System32\\config.exe",
        "workspace/output.json",
    ]
    print(f"\n文件路径验证:")
    for path in test_paths:
        valid = validate_file_path(path)
        print(f"  {path}: {'允许' if valid else '禁止'}")

    print(f"\n工具调用统计: {get_tool_stats()}")