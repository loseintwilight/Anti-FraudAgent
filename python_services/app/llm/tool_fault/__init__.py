"""
工具调用容错增强模块
- 为每类工具设置独立超时和重试策略
- 幂等性保证（execution_id 检查）
- 文件操作沙箱化
- 失败日志记录
"""
from app.llm.tool_fault.config import (
    TOOL_TIMEOUTS,
    TOOL_RETRY_CONFIG,
    SANDBOX_CONFIG,
    generate_execution_id,
    validate_file_path,
)
from app.llm.tool_fault.tracker import ToolCallTracker, tracker
from app.llm.tool_fault.decorator import with_tool_fault_tolerance

__all__ = [
    "TOOL_TIMEOUTS",
    "TOOL_RETRY_CONFIG",
    "SANDBOX_CONFIG",
    "generate_execution_id",
    "validate_file_path",
    "ToolCallTracker",
    "tracker",
    "with_tool_fault_tolerance",
]