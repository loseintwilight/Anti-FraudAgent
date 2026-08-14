"""
监护人通知数据模型
"""
from __future__ import annotations

from datetime import datetime


class GuardianBinding:
    """监护人绑定信息"""

    def __init__(self, user_id: str, guardian_phone: str = "", guardian_email: str = "",
                 guardian_name: str = "", relation: str = ""):
        self.user_id = user_id
        self.guardian_phone = guardian_phone
        self.guardian_email = guardian_email
        self.guardian_name = guardian_name
        self.relation = relation
        self.bound_at = datetime.now().isoformat()


class NotificationRecord:
    """通知记录"""

    def __init__(self, user_id: str, risk_level: str, fraud_type: str,
                 guardian_contact: str, channel: str = "sms"):
        self.user_id = user_id
        self.risk_level = risk_level
        self.fraud_type = fraud_type
        self.guardian_contact = guardian_contact
        self.channel = channel
        self.created_at = datetime.now().isoformat()
        self.status = "pending"
        self.retry_count = 0
        self.last_error = ""