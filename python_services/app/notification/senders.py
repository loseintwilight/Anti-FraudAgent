"""
通知发送器
- 站内消息：真实落盘（notifications/internal_messages.json），可按用户查询
- 外部通道（SMS / Email / Phone）：可插拔 sender 接口 + 环境变量配置项。
  未注册外部 sender 或开关未配置时，如实标注 channel=internal，
  不伪装成已发送短信 / 已拨打电话
"""
from __future__ import annotations

import json
import logging
import os
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)

# 站内消息落盘目录（运行时创建）
NOTIFICATIONS_DIR = Path(__file__).resolve().parent.parent.parent / "notifications"
NOTIFICATIONS_DIR.mkdir(parents=True, exist_ok=True)
INTERNAL_MESSAGES_FILE = NOTIFICATIONS_DIR / "internal_messages.json"

_write_lock = threading.Lock()


# ===================== 可插拔外部 sender 接口 =====================

ExternalSender = Callable[[str, str], Any]

_sms_sender: Optional[ExternalSender] = None
_email_sender: Optional[ExternalSender] = None
_phone_sender: Optional[ExternalSender] = None


def register_sms_sender(func: Optional[ExternalSender]) -> None:
    """注入真实短信网关；None 表示卸载 / 未配置"""
    global _sms_sender
    _sms_sender = func


def register_email_sender(func: Optional[ExternalSender]) -> None:
    """注入真实邮件网关；None 表示卸载 / 未配置"""
    global _email_sender
    _email_sender = func


def register_phone_sender(func: Optional[ExternalSender]) -> None:
    """注入真实电话 / 语音网关；None 表示卸载 / 未配置"""
    global _phone_sender
    _phone_sender = func


# 外部通道开关（未配置则一律降级为站内消息）
SMS_PROVIDER = os.getenv("GUARDIAN_SMS_PROVIDER", "").strip()
EMAIL_PROVIDER = os.getenv("GUARDIAN_EMAIL_PROVIDER", "").strip()
PHONE_PROVIDER = os.getenv("GUARDIAN_PHONE_PROVIDER", "").strip()


def get_channel_status() -> Dict[str, Any]:
    """返回各通道的真实配置状态（用于核验，不伪装已接通）"""
    return {
        "sms": {
            "provider": SMS_PROVIDER,
            "sender_registered": _sms_sender is not None,
            "available": bool(SMS_PROVIDER) and _sms_sender is not None,
        },
        "email": {
            "provider": EMAIL_PROVIDER,
            "sender_registered": _email_sender is not None,
            "available": bool(EMAIL_PROVIDER) and _email_sender is not None,
        },
        "phone": {
            "provider": PHONE_PROVIDER,
            "sender_registered": _phone_sender is not None,
            "available": bool(PHONE_PROVIDER) and _phone_sender is not None,
        },
        "internal": {"available": True, "file": str(INTERNAL_MESSAGES_FILE)},
    }


# ===================== 站内消息：真实落盘 =====================

def _read_internal_messages() -> List[Dict[str, Any]]:
    if not INTERNAL_MESSAGES_FILE.exists():
        return []
    try:
        with open(INTERNAL_MESSAGES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, IOError) as e:
        logger.warning(f"读取站内消息失败: {e}")
        return []


def _append_internal_message(record: Dict[str, Any]) -> None:
    with _write_lock:
        data = _read_internal_messages()
        data.append(record)
        with open(INTERNAL_MESSAGES_FILE, "w", encoding="utf-8") as f:
            json.dump(data[-5000:], f, ensure_ascii=False, indent=2)


def send_internal_message(
    user_id: str,
    content: str,
    meta: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """站内消息：真实落盘到 notifications/internal_messages.json（预警事件持久化）"""
    record = {
        "user_id": user_id,
        "channel": "internal",
        "delivered_via": "internal_message",
        "content": content,
        "meta": meta or {},
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    try:
        _append_internal_message(record)
        logger.info(f"站内消息已落盘: user={user_id}, channel=internal")
    except Exception as e:
        logger.error(f"站内消息落盘失败: {e}")
        record["persist_error"] = str(e)
        return {"sent": False, "channel": "internal", "reason": str(e), "record": record}
    return {"sent": True, "channel": "internal", "record": record}


def list_internal_messages(
    user_id: Optional[str] = None,
    limit: int = 50,
) -> List[Dict[str, Any]]:
    """查询站内消息 / 预警事件（真实读盘，最新在前）"""
    data = _read_internal_messages()
    if user_id:
        data = [r for r in data if r.get("user_id") == user_id]
    return list(reversed(data[-max(1, limit):]))


# ===================== 外部通道 =====================

def _dispatch_external(kind: str, contact: str, content: str) -> Dict[str, Any]:
    """调用已注册的外部网关；未配置则如实返回 channel=internal，不伪装已发送。"""
    status = get_channel_status()[kind]
    if not status["available"]:
        logger.info(
            f"外部 {kind} 通道未配置（provider={status['provider']!r}, "
            f"sender_registered={status['sender_registered']}），按 channel=internal 处理"
        )
        return {
            "sent": False,
            "channel": "internal",
            "delivered_via": "internal_message",
            "reason": f"外部 {kind} 通道未配置",
        }
    sender = {"sms": _sms_sender, "email": _email_sender, "phone": _phone_sender}[kind]
    try:
        sender(contact, content)
        logger.info(f"外部 {kind} 通道发送成功: {contact}")
        return {"sent": True, "channel": kind, "delivered_via": kind}
    except Exception as e:
        logger.warning(f"外部 {kind} 通道发送失败，由站内消息兜底: {e}")
        return {
            "sent": False,
            "channel": "internal",
            "delivered_via": "internal_message",
            "reason": f"外部 {kind} 发送失败: {e}",
        }


def send_sms(phone: str, content: str, **_: Any) -> Dict[str, Any]:
    """发送短信：仅在外部网关已配置并注册时真实发送，否则如实标注 internal。"""
    if not phone:
        return {"sent": False, "channel": "internal", "reason": "未提供手机号"}
    return _dispatch_external("sms", phone, content)


def send_email(email: str, content: str, **_: Any) -> Dict[str, Any]:
    """发送邮件：仅在外部网关已配置并注册时真实发送，否则如实标注 internal。"""
    if not email:
        return {"sent": False, "channel": "internal", "reason": "未提供邮箱"}
    return _dispatch_external("email", email, content)


def send_phone(phone: str, content: str, **_: Any) -> Dict[str, Any]:
    """电话 / 语音通道（可插拔）：未配置时如实标注 internal。"""
    if not phone:
        return {"sent": False, "channel": "internal", "reason": "未提供电话号码"}
    return _dispatch_external("phone", phone, content)
