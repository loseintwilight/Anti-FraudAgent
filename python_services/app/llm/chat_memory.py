"""
对话记忆管理
基于文件存储对话历史，替代 Spring AI 的 FileBasedChatMemory
"""

import json
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage

logger = logging.getLogger(__name__)

# 默认记忆存储目录
DEFAULT_MEMORY_DIR = Path(__file__).resolve().parent.parent.parent / "chat_memory"


class FileChatMemory:
    """
    文件式对话记忆
    将对话历史持久化到 JSON 文件
    """

    def __init__(self, memory_dir: str = str(DEFAULT_MEMORY_DIR)):
        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self._cache: Dict[str, List[Dict]] = {}

    def _get_file_path(self, conversation_id: str) -> Path:
        """获取对话记忆文件路径"""
        safe_id = conversation_id.replace("/", "_").replace("\\", "_")
        return self.memory_dir / f"{safe_id}.json"

    def add_message(
        self,
        conversation_id: str,
        message: BaseMessage,
    ) -> None:
        """添加一条消息到对话历史"""
        messages = self.get_messages(conversation_id)

        msg_dict = {
            "type": self._get_message_type(message),
            "content": message.content,
        }
        messages.append(msg_dict)

        self._save_messages(conversation_id, messages)

    def add_messages(
        self,
        conversation_id: str,
        messages: List[BaseMessage],
    ) -> None:
        """批量添加消息"""
        for msg in messages:
            self.add_message(conversation_id, msg)

    def get_messages(
        self,
        conversation_id: str,
        limit: int = 50,
    ) -> List[Dict]:
        """获取对话历史"""
        file_path = self._get_file_path(conversation_id)
        if file_path.exists():
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    all_messages = json.load(f)
                return all_messages[-limit:] if len(all_messages) > limit else all_messages
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"读取对话记忆失败: {e}")
                return []
        return []

    def get_langchain_messages(
        self,
        conversation_id: str,
        limit: int = 50,
    ) -> List[BaseMessage]:
        """获取 LangChain 格式的消息列表"""
        messages = self.get_messages(conversation_id, limit)
        result: List[BaseMessage] = []
        for msg in messages:
            role = msg.get("type", "human")
            content = msg.get("content", "")
            if role == "human":
                result.append(HumanMessage(content=content))
            elif role == "ai":
                result.append(AIMessage(content=content))
            elif role == "system":
                result.append(SystemMessage(content=content))
        return result

    def clear(self, conversation_id: str) -> None:
        """清除指定对话的历史"""
        file_path = self._get_file_path(conversation_id)
        if file_path.exists():
            file_path.unlink()
        self._cache.pop(conversation_id, None)

    def _save_messages(self, conversation_id: str, messages: List[Dict]) -> None:
        """保存消息到文件"""
        file_path = self._get_file_path(conversation_id)
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(messages, f, ensure_ascii=False, indent=2)
        except IOError as e:
            logger.error(f"保存对话记忆失败: {e}")

    @staticmethod
    def _get_message_type(message: BaseMessage) -> str:
        """获取消息类型标识"""
        if isinstance(message, HumanMessage):
            return "human"
        if isinstance(message, AIMessage):
            return "ai"
        if isinstance(message, SystemMessage):
            return "system"
        return "human"

    def get_stats(self) -> Dict:
        """获取记忆统计信息"""
        files = list(self.memory_dir.glob("*.json"))
        total_messages = 0
        for f in files:
            try:
                with open(f, "r", encoding="utf-8") as fh:
                    msgs = json.load(fh)
                    total_messages += len(msgs)
            except Exception:
                pass
        return {
            "conversation_count": len(files),
            "total_messages": total_messages,
            "memory_dir": str(self.memory_dir),
        }