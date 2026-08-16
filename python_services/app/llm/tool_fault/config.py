"""
工具调用容错配置
"""
from __future__ import annotations

import hashlib
import json
import os
from typing import Any, Dict

# 工具超时配置（秒）
TOOL_TIMEOUTS: Dict[str, int] = {
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
TOOL_RETRY_CONFIG: Dict[str, Any] = {
    "max_retries": 1,
    "backoff_base": 1.0,
    "backoff_multiplier": 2.0,
}

# 文件操作沙箱配置
SANDBOX_CONFIG: Dict[str, Any] = {
    "allowed_directories": [
        os.path.join(os.path.dirname(__file__), "..", "..", "workspace"),
    ],
    "max_file_size": 10 * 1024 * 1024,  # 10MB
    "forbidden_paths": [
        "/etc", "/root", "/var", "C:\\Windows", "C:\\Program Files",
        "/sys", "/proc", "/dev",
    ],
    "allowed_extensions": [".txt", ".json", ".csv", ".md", ".log", ".html", ".pdf"],
}


def generate_execution_id(args: tuple, kwargs: dict) -> str:
    """生成唯一的执行ID（用于幂等性检查）"""
    content = json.dumps({"args": str(args), "kwargs": str(kwargs)}, sort_keys=True)
    return hashlib.md5(content.encode()).hexdigest()[:12]


def validate_file_path(file_path: str) -> bool:
    """沙箱文件路径验证"""
    abs_path = os.path.abspath(file_path)

    for forbidden in SANDBOX_CONFIG["forbidden_paths"]:
        if abs_path.startswith(forbidden):
            return False

    if SANDBOX_CONFIG["allowed_directories"]:
        allowed = any(
            abs_path.startswith(os.path.abspath(d))
            for d in SANDBOX_CONFIG["allowed_directories"]
        )
        if not allowed:
            return False

    ext = os.path.splitext(file_path)[1].lower()
    if ext and ext not in SANDBOX_CONFIG["allowed_extensions"]:
        return False

    return True