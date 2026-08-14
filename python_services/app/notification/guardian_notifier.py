"""
监护人通知器
当系统检测到儿童/老年用户触发高风险时，自动通知绑定监护人
- 风险触发 → 绑定查询 → SMS/Email 推送 → 3 次重试 → 日志记录
"""
from __future__ import annotations

import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.notification.models import GuardianBinding
from app.notification.senders import send_sms, send_email

logger = logging.getLogger(__name__)

# 需要通知的风险等级
NOTIFY_RISK_LEVELS = {"high", "critical"}

# 需要通知的角色
NOTIFY_FRAUD_ROLES = {"elderly", "child", "student"}

# 通知文件存储目录
NOTIFICATION_DIR = Path(__file__).resolve().parent.parent.parent / "notification_data"
NOTIFICATION_DIR.mkdir(parents=True, exist_ok=True)


class GuardianNotifier:
    """监护人通知器"""

    MAX_RETRIES = 3
    RETRY_BACKOFF = [2, 5, 10]  # 重试间隔（秒）

    def __init__(self):
        self._bindings: Dict[str, GuardianBinding] = {}
        self._notification_log: List[Dict[str, Any]] = []
        self._load_bindings()
        self._load_notification_log()

    def _load_bindings(self):
        """加载监护人绑定信息"""
        binding_file = NOTIFICATION_DIR / "guardian_bindings.json"
        if binding_file.exists():
            try:
                with open(binding_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for user_id, info in data.items():
                        self._bindings[user_id] = GuardianBinding(
                            user_id=user_id,
                            guardian_phone=info.get("guardian_phone", ""),
                            guardian_email=info.get("guardian_email", ""),
                            guardian_name=info.get("guardian_name", ""),
                            relation=info.get("relation", ""),
                        )
                logger.info(f"加载了 {len(self._bindings)} 条监护人绑定")
            except Exception as e:
                logger.warning(f"加载监护人绑定失败: {e}")

    def _save_bindings(self):
        """保存监护人绑定信息"""
        binding_file = NOTIFICATION_DIR / "guardian_bindings.json"
        data = {}
        for user_id, binding in self._bindings.items():
            data[user_id] = {
                "guardian_phone": binding.guardian_phone,
                "guardian_email": binding.guardian_email,
                "guardian_name": binding.guardian_name,
                "relation": binding.relation,
                "bound_at": binding.bound_at,
            }
        with open(binding_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _load_notification_log(self):
        """加载通知日志"""
        log_file = NOTIFICATION_DIR / "notification_log.json"
        if log_file.exists():
            try:
                with open(log_file, "r", encoding="utf-8") as f:
                    self._notification_log = json.load(f)
            except Exception:
                self._notification_log = []

    def _save_notification_log(self):
        """保存通知日志"""
        log_file = NOTIFICATION_DIR / "notification_log.json"
        with open(log_file, "w", encoding="utf-8") as f:
            json.dump(self._notification_log[-1000:], f, ensure_ascii=False, indent=2)

    def bind_guardian(self, user_id: str, guardian_phone: str = "",
                      guardian_email: str = "", guardian_name: str = "",
                      relation: str = "") -> bool:
        """绑定监护人"""
        if not guardian_phone and not guardian_email:
            logger.warning(f"绑定监护人失败: 缺少联系方式")
            return False

        self._bindings[user_id] = GuardianBinding(
            user_id=user_id,
            guardian_phone=guardian_phone,
            guardian_email=guardian_email,
            guardian_name=guardian_name,
            relation=relation,
        )
        self._save_bindings()
        logger.info(f"监护人绑定成功: user={user_id}, guardian={guardian_name}, phone={guardian_phone}")
        return True

    def get_guardian(self, user_id: str) -> Optional[GuardianBinding]:
        """获取用户绑定的监护人"""
        return self._bindings.get(user_id)

    def should_notify(self, risk_level: str, fraud_role: str) -> bool:
        """判断是否需要通知监护人"""
        if risk_level not in NOTIFY_RISK_LEVELS:
            return False
        if fraud_role not in NOTIFY_FRAUD_ROLES:
            return False
        return True

    def notify(
        self,
        user_id: str,
        risk_level: str,
        fraud_type: str,
        fraud_role: str,
        risk_score: float = 0,
        report_summary: str = "",
    ) -> Dict[str, Any]:
        """发送监护人通知"""
        if not self.should_notify(risk_level, fraud_role):
            return {
                "notified": False,
                "reason": f"不需要通知: risk_level={risk_level}, fraud_role={fraud_role}",
            }

        guardian = self.get_guardian(user_id)
        if not guardian:
            logger.warning(f"用户 {user_id} 未绑定监护人，跳过通知")
            return {
                "notified": False,
                "reason": "用户未绑定监护人",
            }

        notification_content = self._build_notification_content(
            guardian_name=guardian.guardian_name,
            relation=guardian.relation,
            fraud_type=fraud_type,
            risk_level=risk_level,
            risk_score=risk_score,
            report_summary=report_summary,
        )

        start_time = time.time()
        notified = False
        last_error = ""

        for attempt in range(self.MAX_RETRIES + 1):
            try:
                if guardian.guardian_phone:
                    send_sms(guardian.guardian_phone, notification_content)
                if guardian.guardian_email:
                    send_email(guardian.guardian_email, notification_content)
                notified = True
                break
            except Exception as e:
                last_error = str(e)
                logger.warning(f"通知发送失败 (尝试 {attempt+1}/{self.MAX_RETRIES+1}): {last_error}")
                if attempt < self.MAX_RETRIES:
                    sleep_time = self.RETRY_BACKOFF[attempt]
                    logger.info(f"重试等待 {sleep_time}s...")
                    time.sleep(sleep_time)

        latency = (time.time() - start_time) * 1000
        record = {
            "user_id": user_id,
            "guardian_name": guardian.guardian_name,
            "guardian_phone": guardian.guardian_phone,
            "fraud_type": fraud_type,
            "risk_level": risk_level,
            "risk_score": risk_score,
            "notified": notified,
            "error": last_error if not notified else "",
            "latency_ms": round(latency, 2),
            "timestamp": datetime.now().isoformat(),
        }
        self._notification_log.append(record)
        self._save_notification_log()

        if notified:
            logger.info(
                f"监护人通知成功: user={user_id}, guardian={guardian.guardian_name}, "
                f"type={fraud_type}, latency={latency:.0f}ms"
            )
        else:
            logger.error(f"监护人通知失败: user={user_id}, error={last_error}")

        return {
            "notified": notified,
            "guardian_name": guardian.guardian_name,
            "latency_ms": latency,
            "error": last_error if not notified else "",
        }

    def _build_notification_content(
        self,
        guardian_name: str,
        relation: str,
        fraud_type: str,
        risk_level: str,
        risk_score: float,
        report_summary: str,
    ) -> str:
        """构建通知内容"""
        relation_text = relation or "亲属"
        level_text = {"high": "高", "critical": "极高"}.get(risk_level, risk_level)
        score_text = f"{risk_score:.0f}分" if risk_score > 0 else ""

        content = (
            f"【反诈预警】{guardian_name}您好，"
            f"您的{relation_text}可能正在遭遇{fraud_type}诈骗（{level_text}风险{score_text}）。"
            f"请尽快联系确认情况，如有疑问请拨打96110。"
        )
        if report_summary:
            content += f" 详情: {report_summary[:100]}"

        return content

    def get_notification_stats(self) -> Dict[str, Any]:
        """获取通知统计"""
        total = len(self._notification_log)
        if total == 0:
            return {"total": 0, "success": 0, "failed": 0, "success_rate": 0}

        success = sum(1 for r in self._notification_log if r.get("notified", False))
        latencies = [r.get("latency_ms", 0) for r in self._notification_log if r.get("notified")]

        return {
            "total": total,
            "success": success,
            "failed": total - success,
            "success_rate": success / total if total > 0 else 0,
            "avg_latency_ms": sum(latencies) / len(latencies) if latencies else 0,
            "max_latency_ms": max(latencies) if latencies else 0,
            "bindings_count": len(self._bindings),
        }

    def get_recent_notifications(self, limit: int = 20) -> List[Dict[str, Any]]:
        """获取最近的通知记录"""
        return self._notification_log[-limit:]


# 全局实例
notifier = GuardianNotifier()