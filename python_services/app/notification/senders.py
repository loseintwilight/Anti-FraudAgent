"""
通知发送器：SMS / Email 双通道
"""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def send_sms(phone: str, content: str):
    """发送短信通知（模拟实现）"""
    logger.info(f"[SMS] 发送短信到 {phone}: {content[:50]}...")
    # 实际项目中使用阿里云短信/腾讯云短信SDK


def send_email(email: str, content: str):
    """发送邮件通知（模拟实现）"""
    logger.info(f"[EMAIL] 发送邮件到 {email}: {content[:50]}...")
    # 实际项目中使用SMTP发送