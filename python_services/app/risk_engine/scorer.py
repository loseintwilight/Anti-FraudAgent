"""
风险评分引擎
实现四级风险判定（低<20, 中20-50, 高50-80, 极高>=80），标注风险来源项
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Tuple

from app.risk_engine.profile import UserProfile

logger = logging.getLogger(__name__)


# 四级风险阈值
THRESHOLDS = [
    ("low", 0, 20, "低风险"),           # 0 <= score < 20
    ("mid", 20, 50, "中风险"),           # 20 <= score < 50
    ("high", 50, 80, "高风险"),          # 50 <= score < 80
    ("critical", 80, 101, "极高风险"),   # 80 <= score <= 100
]

# 维度中文名映射
DIMENSION_NAMES_CN = {
    "call": "通话行为",
    "sms": "短信行为",
    "transaction": "交易行为",
    "app": "应用使用",
    "network": "网络行为",
    "device": "设备安全",
    "account": "账户安全",
    "reported": "举报记录",
}

# 各维度在 UserProfile 中对应的属性名
DIMENSION_ATTR_MAP = {
    "call": "call_abnormal_score",
    "sms": "sms_abnormal_score",
    "transaction": "transaction_abnormal_score",
    "app": "app_abnormal_score",
    "network": "network_risk_score",
    "device": "device_risk_score",
    "account": "account_risk_score",
    "reported": "reported_risk",
}


class RiskScorer:
    """
    风险评分引擎
    根据用户画像计算综合风险评分，进行四级风险判定
    """

    def evaluate(self, profile: UserProfile) -> Dict[str, Any]:
        """
        执行风险评估
        返回包含总分、等级、来源项、画像摘要的字典
        """
        logger.info(f"开始评估用户风险: user_id={profile.user_id}")

        total_score, sources = self._compute_weighted_score(profile)
        risk_level = self._determine_level(total_score)
        profile_summary = profile.summary()

        result = {
            "total_score": round(total_score, 2),
            "risk_level": risk_level,
            "sources": sources,
            "profile_summary": profile_summary,
        }

        logger.info(
            f"评估完成: 总分={total_score:.2f}, 等级={risk_level}, "
            f"来源项数={len(sources)}"
        )
        return result

    def _compute_weighted_score(
        self, profile: UserProfile
    ) -> Tuple[float, List[Dict[str, Any]]]:
        """
        计算加权总分
        返回 (总分, 风险来源明细列表)
        """
        weights = profile.dimension_weights
        total_score = 0.0
        sources: List[Dict[str, Any]] = []

        for dim_key, weight in weights.items():
            attr_name = DIMENSION_ATTR_MAP.get(dim_key)
            if attr_name is None:
                continue

            # 获取该维度评分
            dim_score = getattr(profile, attr_name, 0.0)

            # 加权贡献
            contribution = dim_score * weight
            total_score += contribution

            # 只有当该维度得分 > 0 时才记录为风险来源
            if dim_score > 0:
                sources.append({
                    "dimension": DIMENSION_NAMES_CN.get(dim_key, dim_key),
                    "score": round(dim_score, 2),
                    "weight": weight,
                    "contribution": round(contribution, 2),
                    "detail": self._generate_detail(dim_key, dim_score, profile),
                })

        # 按贡献降序排列
        sources.sort(key=lambda x: x["contribution"], reverse=True)

        return total_score, sources

    def _determine_level(self, score: float) -> str:
        """根据分数确定风险等级"""
        for level_name, lower, upper, _ in THRESHOLDS:
            if lower <= score < upper:
                return level_name
        # 兜底（100分时）
        return "critical"

    @staticmethod
    def _generate_detail(dim_key: str, score: float, profile: UserProfile) -> str:
        """生成维度风险详情描述"""
        behavior = profile.behavior
        if behavior is None:
            return f"{DIMENSION_NAMES_CN.get(dim_key, dim_key)}得分{score:.1f}"

        if dim_key == "call":
            return (
                f"陌生通话占比{behavior.unknown_call_ratio:.0%}, "
                f"近期待通话{behavior.call_duration_minutes:.0f}分钟, "
                f"得分{score:.1f}"
            )
        elif dim_key == "sms":
            return (
                f"含链接短信占比{behavior.sms_with_link_ratio:.0%}, "
                f"收到{behavior.sms_count_received}条, "
                f"得分{score:.1f}"
            )
        elif dim_key == "transaction":
            return (
                f"近7天转账{behavior.total_transaction_amount_7d:.0f}元共{behavior.transaction_count_7d}次, "
                f"新账户转账{behavior.transaction_to_new_accounts}次, "
                f"夜间交易{behavior.night_transaction_count}次, "
                f"得分{score:.1f}"
            )
        elif dim_key == "app":
            return (
                f"新安装应用{behavior.recently_installed_apps}个, "
                f"金融类{behavior.financial_app_count}个, "
                f"得分{score:.1f}"
            )
        elif dim_key == "network":
            return (
                f"访问可疑站点{behavior.visited_suspicious_sites}次, "
                f"点击不明链接{behavior.clicked_unknown_links}次, "
                f"{'使用VPN' if behavior.vpn_or_proxy_used else ''}"
                f"{'连接公共WiFi' if behavior.public_wifi_connected else ''}, "
                f"得分{score:.1f}"
            )
        elif dim_key == "device":
            return (
                f"{'设备已Root; ' if behavior.device_rooted else ''}"
                f"{'未实名认证; ' if not behavior.has_verified_realname else ''}"
                f"得分{score:.1f}"
            )
        elif dim_key == "account":
            return (
                f"账户注册{behavior.account_age_days}天, "
                f"{'已实名' if behavior.has_verified_realname else '未实名'}, "
                f"得分{score:.1f}"
            )
        elif dim_key == "reported":
            return (
                f"被举报{behavior.reported_count}次, "
                f"{'已拨打反诈热线' if behavior.fraud_hotline_called else ''}, "
                f"得分{score:.1f}"
            )
        return f"{DIMENSION_NAMES_CN.get(dim_key, dim_key)}得分{score:.1f}"
