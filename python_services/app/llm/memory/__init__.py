"""
Agent 长期记忆系统
- 用户画像持久化：角色、检测历史、风险偏好
- 记忆追加更新（不覆盖旧数据）
- 短期记忆窗口管理（10 轮对话）
"""
from app.llm.memory.user_profile import UserProfile
from app.llm.memory.manager import MemoryManager, memory_manager

__all__ = [
    "UserProfile",
    "MemoryManager",
    "memory_manager",
]