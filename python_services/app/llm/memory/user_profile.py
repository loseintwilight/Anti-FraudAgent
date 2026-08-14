"""
用户画像数据模型
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List


class UserProfile:
    """用户画像"""

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.fraud_role: str = "youth"  # elderly/child/youth/worker/accountant
        self.age_group: str = "middle"
        self.risk_preference: float = 0.5  # 风险偏好指数
        self.detection_history: List[Dict[str, Any]] = []
        self.guardian_contact: str = ""
        self.guardian_name: str = ""
        self.risk_interactions: Dict[str, int] = {}  # 诈骗类型 -> 交互次数
        self.created_at: str = datetime.now().isoformat()
        self.updated_at: str = datetime.now().isoformat()
        self.total_detections: int = 0
        self.high_risk_count: int = 0
        self.critical_risk_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "fraud_role": self.fraud_role,
            "age_group": self.age_group,
            "risk_preference": self.risk_preference,
            "detection_history": self.detection_history[-50:],
            "guardian_contact": self.guardian_contact,
            "guardian_name": self.guardian_name,
            "risk_interactions": self.risk_interactions,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "total_detections": self.total_detections,
            "high_risk_count": self.high_risk_count,
            "critical_risk_count": self.critical_risk_count,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UserProfile":
        profile = cls(data.get("user_id", ""))
        profile.fraud_role = data.get("fraud_role", "youth")
        profile.age_group = data.get("age_group", "middle")
        profile.risk_preference = data.get("risk_preference", 0.5)
        profile.detection_history = data.get("detection_history", [])
        profile.guardian_contact = data.get("guardian_contact", "")
        profile.guardian_name = data.get("guardian_name", "")
        profile.risk_interactions = data.get("risk_interactions", {})
        profile.created_at = data.get("created_at", "")
        profile.updated_at = data.get("updated_at", "")
        profile.total_detections = data.get("total_detections", 0)
        profile.high_risk_count = data.get("high_risk_count", 0)
        profile.critical_risk_count = data.get("critical_risk_count", 0)
        return profile