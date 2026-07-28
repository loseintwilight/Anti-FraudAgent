"""
对话上下文管理模块
维护多轮对话历史，支持会话的创建、读取、持久化
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from ..config import settings
from ..models.schemas import Message, UserProfile, UserRole, RiskLevel
from ..utils.logger import logger


class ConversationContext:
    """
    单次会话的上下文

    功能说明：
    - 维护对话消息列表
    - 跟踪用户画像（随对话动态更新）
    - 记录风险检测结果
    """

    def __init__(self, session_id: str, user_id: str):
        self.session_id: str = session_id
        self.user_id: str = user_id
        self.messages: List[Message] = []
        self.user_profile: UserProfile = UserProfile(user_id=user_id)
        self.created_at: datetime = datetime.now()
        self.updated_at: datetime = datetime.now()
        self.risk_history: List[dict] = []  # 风险检测历史

    def add_message(self, role: str, content: str):
        """
        添加一条对话消息

        Args:
            role: 角色 (user/assistant)
            content: 消息内容
        """
        message = Message(
            role=role,
            content=content,
            timestamp=datetime.now().timestamp()
        )
        self.messages.append(message)
        self.updated_at = datetime.now()

        # 更新用户对话轮次
        if role == "user":
            self.user_profile.conversation_turns += 1
            self.user_profile.query_history.append(content)

    def get_recent_messages(self, max_turns: Optional[int] = None) -> List[Dict[str, str]]:
        """
        获取最近 N 轮对话（用于 API 请求）

        Args:
            max_turns: 最大轮次（每轮包含 user+assistant 两条），默认使用配置值

        Returns:
            格式化的消息列表 [{"role": "...", "content": "..."}, ...]
        """
        if max_turns is None:
            max_turns = settings.MAX_CONVERSATION_TURNS

        # 取最近 N 轮（每轮2条消息）
        max_messages = max_turns * 2
        recent = self.messages[-max_messages:]

        return [
            {"role": msg.role, "content": msg.content}
            for msg in recent
        ]

    def add_risk_record(self, fraud_type: str, risk_level: RiskLevel, confidence: float):
        """记录一次风险检测结果"""
        self.risk_history.append({
            "fraud_type": fraud_type,
            "risk_level": risk_level.value,
            "confidence": confidence,
            "timestamp": datetime.now().isoformat(),
        })
        # 更新用户画像风险分
        score_map = {
            RiskLevel.LOW: 5,
            RiskLevel.MEDIUM: 20,
            RiskLevel.HIGH: 50,
            RiskLevel.EXTREME: 80,
        }
        self.user_profile.add_risk_source(fraud_type, score_map.get(risk_level, 0))
        self.user_profile.risk_level = risk_level

    def to_dict(self) -> dict:
        """序列化到字典（用于持久化）"""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "messages": [
                {"role": m.role, "content": m.content, "timestamp": m.timestamp}
                for m in self.messages
            ],
            "user_profile": {
                "age_group": self.user_profile.age_group,
                "occupation_tag": self.user_profile.occupation_tag,
                "role": self.user_profile.role.value,
                "risk_score": self.user_profile.risk_score,
                "risk_level": self.user_profile.risk_level.value,
                "conversation_turns": self.user_profile.conversation_turns,
            },
            "risk_history": self.risk_history,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ConversationContext":
        """从字典反序列化"""
        ctx = cls(session_id=data["session_id"], user_id=data["user_id"])
        ctx.created_at = datetime.fromisoformat(data["created_at"])
        ctx.updated_at = datetime.fromisoformat(data["updated_at"])
        ctx.messages = [
            Message(role=m["role"], content=m["content"], timestamp=m.get("timestamp"))
            for m in data.get("messages", [])
        ]
        profile = data.get("user_profile", {})
        ctx.user_profile = UserProfile(
            user_id=data["user_id"],
            age_group=profile.get("age_group", "unknown"),
            occupation_tag=profile.get("occupation_tag", "unknown"),
            role=UserRole(profile.get("role", "unknown")),
            risk_score=profile.get("risk_score", 0),
            risk_level=RiskLevel(profile.get("risk_level", "low")),
            conversation_turns=profile.get("conversation_turns", 0),
        )
        ctx.risk_history = data.get("risk_history", [])
        return ctx


class ContextManager:
    """
    对话上下文管理器（全局单例）

    功能说明：
    - 管理所有活跃会话
    - 支持会话的创建、查找、删除
    - 支持持久化到文件系统
    """

    def __init__(self):
        self._contexts: Dict[str, ConversationContext] = {}
        self._storage_path = Path(settings.CONTEXT_STORAGE_PATH)
        self._storage_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"对话上下文管理器初始化完成，存储路径: {self._storage_path}")

    def get_or_create(self, session_id: str, user_id: str) -> ConversationContext:
        """
        获取已有会话或创建新会话

        Args:
            session_id: 会话 ID
            user_id: 用户 ID

        Returns:
            ConversationContext 实例
        """
        if session_id in self._contexts:
            return self._contexts[session_id]

        # 尝试从文件恢复
        restored = self._load_from_file(session_id)
        if restored:
            self._contexts[session_id] = restored
            logger.info(f"从文件恢复会话: {session_id}")
            return restored

        ctx = ConversationContext(session_id=session_id, user_id=user_id)
        self._contexts[session_id] = ctx
        logger.info(f"创建新会话: session_id={session_id}, user_id={user_id}")
        return ctx

    def get(self, session_id: str) -> Optional[ConversationContext]:
        """获取指定会话"""
        return self._contexts.get(session_id)

    def remove(self, session_id: str):
        """删除会话（同时删除持久化文件）"""
        self._contexts.pop(session_id, None)
        file_path = self._storage_path / f"{session_id}.json"
        if file_path.exists():
            file_path.unlink()
            logger.info(f"删除会话文件: {session_id}")

    def persist(self, session_id: str):
        """持久化指定会话到文件"""
        ctx = self._contexts.get(session_id)
        if not ctx:
            return
        file_path = self._storage_path / f"{session_id}.json"
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(ctx.to_dict(), f, ensure_ascii=False, indent=2)
            logger.debug(f"会话持久化成功: {session_id}")
        except Exception as e:
            logger.error(f"会话持久化失败: session_id={session_id}, error={e}")

    def persist_all(self):
        """持久化所有活跃会话"""
        for session_id in list(self._contexts.keys()):
            self.persist(session_id)

    def _load_from_file(self, session_id: str) -> Optional[ConversationContext]:
        """从文件加载会话"""
        file_path = self._storage_path / f"{session_id}.json"
        if not file_path.exists():
            return None
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return ConversationContext.from_dict(data)
        except Exception as e:
            logger.warning(f"加载会话文件失败: {session_id}, error={e}")
            return None

    def create_session_id(self) -> str:
        """生成唯一会话 ID"""
        return f"session-{uuid.uuid4().hex[:12]}"


# 全局单例
context_manager = ContextManager()