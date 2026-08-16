"""
工具调用容错装饰器
"""
from __future__ import annotations

import logging
import time
import uuid
from functools import wraps
from typing import Callable

from app.llm.tool_fault.config import TOOL_TIMEOUTS, TOOL_RETRY_CONFIG
from app.llm.tool_fault.tracker import tracker

logger = logging.getLogger(__name__)


def with_tool_fault_tolerance(tool_name: str):
    """工具调用容错装饰器"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            execution_id = str(uuid.uuid4())[:8]

            if execution_id and tracker.is_duplicate(execution_id):
                logger.warning(f"[{tool_name}] 重复执行被阻止: {execution_id}")
                return {"error": "duplicate_execution", "message": "该操作已执行过"}

            timeout = TOOL_TIMEOUTS.get(tool_name, TOOL_TIMEOUTS["default"])
            max_retries = TOOL_RETRY_CONFIG["max_retries"]

            for attempt in range(max_retries + 1):
                try:
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