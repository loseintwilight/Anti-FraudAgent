"""
Agent 长期记忆管理器
- 用户画像持久化：角色、检测历史、风险偏好
- 记忆追加更新（不覆盖旧数据）
- 短期记忆窗口管理（10 轮对话）
- 长期记忆跨会话持久化
"""
from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from app.llm.memory.user_profile import UserProfile

logger = logging.getLogger(__name__)

# 长期记忆存储目录
LONG_TERM_MEMORY_DIR = Path(__file__).resolve().parent.parent.parent.parent / "user_profiles"
LONG_TERM_MEMORY_DIR.mkdir(parents=True, exist_ok=True)


class MemoryManager:
    """记忆管理器：统一管理短期和长期记忆"""

    SHORT_TERM_WINDOW = 10  # 短期记忆窗口（轮数）

    def __init__(self):
        self._profiles: Dict[str, UserProfile] = {}
        self._load_all_profiles()

    def _profile_path(self, user_id: str) -> Path:
        """用户画像文件路径"""
        safe_id = user_id.replace("/", "_").replace("\\", "_")
        return LONG_TERM_MEMORY_DIR / f"{safe_id}.json"

    def _load_all_profiles(self):
        """加载所有用户画像"""
        for f in LONG_TERM_MEMORY_DIR.glob("*.json"):
            try:
                with open(f, "r", encoding="utf-8") as fh:
                    data = json.load(fh)
                    profile = UserProfile.from_dict(data)
                    self._profiles[profile.user_id] = profile
            except Exception:
                pass
        logger.info(f"加载了 {len(self._profiles)} 个用户画像")

    def get_profile(self, user_id: str) -> UserProfile:
        """获取用户画像（不存在则创建）"""
        if user_id not in self._profiles:
            profile_path = self._profile_path(user_id)
            if profile_path.exists():
                try:
                    with open(profile_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        self._profiles[user_id] = UserProfile.from_dict(data)
                        return self._profiles[user_id]
                except Exception:
                    pass
            self._profiles[user_id] = UserProfile(user_id)
            self._save_profile(user_id)
        return self._profiles[user_id]

    def _save_profile(self, user_id: str):
        """保存用户画像到文件"""
        if user_id not in self._profiles:
            return
        profile_path = self._profile_path(user_id)
        try:
            with open(profile_path, "w", encoding="utf-8") as f:
                json.dump(self._profiles[user_id].to_dict(), f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存用户画像失败: {e}")

    def update_profile(self, user_id: str, **kwargs) -> UserProfile:
        """更新用户画像（追加模式，不覆盖已有数据）"""
        profile = self.get_profile(user_id)

        for key, value in kwargs.items():
            if hasattr(profile, key):
                current = getattr(profile, key)
                if isinstance(current, list) and isinstance(value, list):
                    current.extend(value)
                elif isinstance(current, dict) and isinstance(value, dict):
                    current.update(value)
                else:
                    setattr(profile, key, value)

        profile.updated_at = datetime.now().isoformat()
        self._save_profile(user_id)
        return profile

    def add_detection_record(
        self,
        user_id: str,
        fraud_type: str,
        risk_level: str,
        risk_score: float,
        summary: str = "",
    ) -> UserProfile:
        """添加检测记录（追加，不覆盖历史）"""
        profile = self.get_profile(user_id)

        record = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "type": fraud_type,
            "risk_level": risk_level,
            "risk_score": risk_score,
            "summary": summary[:100],
        }

        profile.detection_history.append(record)
        profile.total_detections += 1

        if risk_level == "high":
            profile.high_risk_count += 1
        elif risk_level == "critical":
            profile.critical_risk_count += 1

        if fraud_type not in profile.risk_interactions:
            profile.risk_interactions[fraud_type] = 0
        profile.risk_interactions[fraud_type] += 1

        total_risks = profile.high_risk_count + profile.critical_risk_count
        if profile.total_detections > 0:
            profile.risk_preference = min(1.0, total_risks / profile.total_detections)

        profile.updated_at = datetime.now().isoformat()
        self._save_profile(user_id)

        logger.info(
            f"添加检测记录: user={user_id}, type={fraud_type}, "
            f"level={risk_level}, total={profile.total_detections}"
        )
        return profile

    def get_risk_summary(self, user_id: str) -> Dict[str, Any]:
        """获取用户风险摘要"""
        profile = self.get_profile(user_id)
        return {
            "user_id": user_id,
            "fraud_role": profile.fraud_role,
            "total_detections": profile.total_detections,
            "high_risk_count": profile.high_risk_count,
            "critical_risk_count": profile.critical_risk_count,
            "risk_preference": profile.risk_preference,
            "top_fraud_types": sorted(
                profile.risk_interactions.items(),
                key=lambda x: x[1], reverse=True
            )[:5],
            "recent_detections": profile.detection_history[-5:],
            "has_guardian": bool(profile.guardian_contact),
        }

    def bind_guardian(self, user_id: str, phone: str, name: str = "") -> None:
        """绑定监护人信息"""
        profile = self.get_profile(user_id)
        profile.guardian_contact = phone
        profile.guardian_name = name
        profile.updated_at = datetime.now().isoformat()
        self._save_profile(user_id)
        logger.info(f"绑定监护人: user={user_id}, guardian={name}, phone={phone}")

    def get_stats(self) -> Dict[str, Any]:
        """获取记忆系统统计"""
        total_detections = sum(p.total_detections for p in self._profiles.values())
        total_high_risk = sum(p.high_risk_count for p in self._profiles.values())
        total_critical = sum(p.critical_risk_count for p in self._profiles.values())
        return {
            "user_count": len(self._profiles),
            "total_detections": total_detections,
            "total_high_risk": total_high_risk,
            "total_critical_risk": total_critical,
            "guardian_bound_count": sum(
                1 for p in self._profiles.values() if p.guardian_contact
            ),
        }


# 全局实例
memory_manager = MemoryManager()