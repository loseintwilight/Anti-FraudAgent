"""
用户画像计算模块
定义 UserProfile dataclass，支持多维度加权评估
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from app.api.schemas import UserBehavior
from app.risk_engine.rules import accountant, elderly, student, worker

logger = logging.getLogger(__name__)

# 人群分组年龄阈值
AGE_BOUNDARIES = {
    "student": (6, 22),       # 学生年龄范围
    "young_worker": (22, 35),  # 年轻工作者
    "middle_worker": (35, 50), # 中年工作者
    "elderly": (50, 150),      # 老年人
}


def _detect_occupation(behavior: UserBehavior) -> str:
    """
    根据行为和年龄推断职业分组
    优先使用用户提供的职业信息，若无则按年龄推断
    """
    if behavior.occupation and behavior.occupation != "unknown":
        return behavior.occupation

    age = behavior.age
    if 6 <= age < 22:
        return "student"
    elif 22 <= age < 50:
        return "worker"
    elif age >= 50:
        return "elderly"
    return "unknown"


@dataclass
class UserProfile:
    """
    用户画像数据类
    存储用户在各维度的特征数据，供风险评分引擎使用
    """
    user_id: str = ""
    age: int = 0
    gender: str = "unknown"
    occupation: str = "unknown"
    education: str = "unknown"
    province: str = "unknown"
    city: str = "unknown"

    # 通话维度特征
    call_abnormal_score: float = 0.0          # 通话异常评分
    unknown_call_frequency: float = 0.0       # 陌生通话频率

    # 短信维度特征
    sms_abnormal_score: float = 0.0           # 短信异常评分
    sms_link_density: float = 0.0             # 含链接短信密度

    # 交易维度特征
    transaction_abnormal_score: float = 0.0   # 交易异常评分
    large_transfer_count: int = 0             # 大额转账次数
    night_trade_ratio: float = 0.0            # 夜间交易比例
    new_account_trade_ratio: float = 0.0      # 新账户交易比例

    # 设备与网络维度
    app_abnormal_score: float = 0.0           # 应用使用异常评分
    network_risk_score: float = 0.0           # 网络风险评分
    device_risk_score: float = 0.0            # 设备风险评分

    # 综合维度
    account_risk_score: float = 0.0           # 账户风险评分
    reported_risk: float = 0.0                # 举报风险

    # 原始行为数据（引用）
    behavior: Optional[UserBehavior] = None

    # 维度权重（根据不同人群动态调整）
    dimension_weights: Dict[str, float] = field(default_factory=lambda: {
        "call": 0.15,
        "sms": 0.10,
        "transaction": 0.30,
        "app": 0.10,
        "network": 0.15,
        "device": 0.05,
        "account": 0.10,
        "reported": 0.05,
    })

    def to_dict(self) -> Dict:
        """将画像转为字典"""
        return {
            "user_id": self.user_id,
            "age": self.age,
            "gender": self.gender,
            "occupation": self.occupation,
            "education": self.education,
            "province": self.province,
            "city": self.city,
            "dimension_weights": self.dimension_weights,
            "scores": {
                "call_abnormal_score": self.call_abnormal_score,
                "sms_abnormal_score": self.sms_abnormal_score,
                "transaction_abnormal_score": self.transaction_abnormal_score,
                "app_abnormal_score": self.app_abnormal_score,
                "network_risk_score": self.network_risk_score,
                "device_risk_score": self.device_risk_score,
                "account_risk_score": self.account_risk_score,
                "reported_risk": self.reported_risk,
            },
        }

    def summary(self) -> str:
        """生成画像摘要文本"""
        parts = [
            f"用户{self.user_id}",
            f"年龄{self.age}岁",
            f"职业:{self.occupation}",
            f"所在:{self.province}",
            f"通话异常:{self.call_abnormal_score:.1f}",
            f"交易异常:{self.transaction_abnormal_score:.1f}",
            f"设备风险:{self.device_risk_score:.1f}",
        ]
        return " | ".join(parts)

    def build(self, behavior: UserBehavior, user_id: str) -> UserProfile:
        """
        根据用户行为数据构建完整的用户画像
        返回填充完成的 UserProfile 实例
        """
        logger.info(f"开始构建用户画像: user_id={user_id}")

        # 基本信息
        self.user_id = user_id
        self.age = behavior.age
        self.gender = behavior.gender
        self.education = behavior.education
        self.province = behavior.province
        self.city = behavior.city
        self.behavior = behavior

        # 检测职业/人群
        self.occupation = _detect_occupation(behavior)

        # 根据人群加载差异化权重
        self._load_weights_by_occupation()

        # ========== 各维度评分计算 ==========

        # 1. 通话维度
        self.call_abnormal_score = self._calc_call_score(behavior)
        self.unknown_call_frequency = behavior.unknown_call_ratio

        # 2. 短信维度
        self.sms_abnormal_score = self._calc_sms_score(behavior)
        self.sms_link_density = behavior.sms_with_link_ratio

        # 3. 交易维度
        self.transaction_abnormal_score = self._calc_transaction_score(behavior)
        self.large_transfer_count = behavior.transaction_count_7d
        self.night_trade_ratio = (
            behavior.night_transaction_count / max(behavior.transaction_count_7d, 1)
        )
        self.new_account_trade_ratio = (
            behavior.transaction_to_new_accounts / max(behavior.transaction_count_7d, 1)
        )

        # 4. 应用维度
        self.app_abnormal_score = self._calc_app_score(behavior)

        # 5. 网络维度
        self.network_risk_score = self._calc_network_score(behavior)

        # 6. 设备维度
        self.device_risk_score = self._calc_device_score(behavior)

        # 7. 账户维度
        self.account_risk_score = self._calc_account_score(behavior)

        # 8. 举报维度
        self.reported_risk = self._calc_reported_score(behavior)

        logger.info(f"用户画像构建完成: {self.summary()}")
        return self

    def _load_weights_by_occupation(self) -> None:
        """根据职业加载差异化维度权重"""
        occupation = self.occupation
        if occupation == "student":
            self.dimension_weights = student.WEIGHTS.copy()
        elif occupation == "elderly":
            self.dimension_weights = elderly.WEIGHTS.copy()
        elif occupation == "worker":
            self.dimension_weights = worker.WEIGHTS.copy()
        elif occupation == "accountant":
            self.dimension_weights = accountant.WEIGHTS.copy()
        else:
            # 默认权重
            self.dimension_weights = {
                "call": 0.15,
                "sms": 0.10,
                "transaction": 0.30,
                "app": 0.10,
                "network": 0.15,
                "device": 0.05,
                "account": 0.10,
                "reported": 0.05,
            }

    @staticmethod
    def _calc_call_score(behavior: UserBehavior) -> float:
        """计算通话行为异常评分 (0-100)"""
        score = 0.0

        # 陌生号码通话比例过高
        if behavior.unknown_call_ratio > 0.7:
            score += 40.0
        elif behavior.unknown_call_ratio > 0.4:
            score += 20.0

        # 通话时长异常（过长）
        if behavior.call_duration_minutes > 300:
            score += 30.0
        elif behavior.call_duration_minutes > 120:
            score += 15.0

        # 去电过多（疑似骚扰）
        if behavior.call_count_outgoing > 100:
            score += 20.0
        elif behavior.call_count_outgoing > 50:
            score += 10.0

        # 来电过多
        if behavior.call_count_incoming > 200:
            score += 10.0

        return min(score, 100.0)

    @staticmethod
    def _calc_sms_score(behavior: UserBehavior) -> float:
        """计算短信行为异常评分 (0-100)"""
        score = 0.0

        # 含链接短信比例过高
        if behavior.sms_with_link_ratio > 0.8:
            score += 50.0
        elif behavior.sms_with_link_ratio > 0.5:
            score += 30.0

        # 收到短信数量异常
        if behavior.sms_count_received > 100:
            score += 30.0
        elif behavior.sms_count_received > 50:
            score += 15.0

        # 发送短信数量异常
        if behavior.sms_count_sent > 50:
            score += 20.0

        return min(score, 100.0)

    @staticmethod
    def _calc_transaction_score(behavior: UserBehavior) -> float:
        """计算交易行为异常评分 (0-100)"""
        score = 0.0

        # 近7天总金额异常
        if behavior.total_transaction_amount_7d > 100000:
            score += 30.0
        elif behavior.total_transaction_amount_7d > 50000:
            score += 15.0

        # 单笔最大金额异常
        if behavior.recent_transaction_amount > 50000:
            score += 20.0
        elif behavior.recent_transaction_amount > 10000:
            score += 10.0

        # 向新账户转账次数多
        if behavior.transaction_to_new_accounts > 5:
            score += 25.0
        elif behavior.transaction_to_new_accounts > 2:
            score += 12.0

        # 夜间交易次数多
        if behavior.night_transaction_count > 3:
            score += 15.0
        elif behavior.night_transaction_count > 1:
            score += 8.0

        # 交易频率异常
        if behavior.transaction_count_7d > 30:
            score += 10.0

        return min(score, 100.0)

    @staticmethod
    def _calc_app_score(behavior: UserBehavior) -> float:
        """计算应用使用异常评分 (0-100)"""
        score = 0.0

        # 近7天新安装应用过多
        if behavior.recently_installed_apps > 15:
            score += 35.0
        elif behavior.recently_installed_apps > 8:
            score += 20.0

        # 金融类应用数量异常（过多或过少都需关注）
        if behavior.financial_app_count > 15:
            score += 25.0
        elif behavior.financial_app_count > 8:
            score += 12.0

        # 安装应用总数异常
        if behavior.installed_apps_count > 100:
            score += 20.0
        elif behavior.installed_apps_count > 60:
            score += 10.0

        # 使用时长异常
        if behavior.app_usage_minutes > 600:
            score += 20.0

        return min(score, 100.0)

    @staticmethod
    def _calc_network_score(behavior: UserBehavior) -> float:
        """计算网络行为风险评分 (0-100)"""
        score = 0.0

        # 访问可疑站点
        if behavior.visited_suspicious_sites > 10:
            score += 35.0
        elif behavior.visited_suspicious_sites > 3:
            score += 20.0

        # 点击不明链接
        if behavior.clicked_unknown_links > 5:
            score += 30.0
        elif behavior.clicked_unknown_links > 1:
            score += 15.0

        # 使用VPN/代理
        if behavior.vpn_or_proxy_used:
            score += 20.0

        # 公共WiFi
        if behavior.public_wifi_connected:
            score += 15.0

        return min(score, 100.0)

    @staticmethod
    def _calc_device_score(behavior: UserBehavior) -> float:
        """计算设备风险评分 (0-100)"""
        score = 0.0

        if behavior.device_rooted:
            score += 60.0

        # 没有实名认证
        if not behavior.has_verified_realname:
            score += 40.0

        return min(score, 100.0)

    @staticmethod
    def _calc_account_score(behavior: UserBehavior) -> float:
        """计算账户维度风险评分 (0-100)"""
        score = 0.0

        # 新注册账户
        if behavior.account_age_days < 7:
            score += 50.0
        elif behavior.account_age_days < 30:
            score += 30.0
        elif behavior.account_age_days < 90:
            score += 15.0

        # 未实名认证
        if not behavior.has_verified_realname:
            score += 40.0

        return min(score, 100.0)

    @staticmethod
    def _calc_reported_score(behavior: UserBehavior) -> float:
        """计算举报风险评分 (0-100)"""
        score = 0.0

        if behavior.reported_count > 5:
            score += 60.0
        elif behavior.reported_count > 2:
            score += 40.0
        elif behavior.reported_count > 0:
            score += 20.0

        # 拨打反诈热线（可能是受害者）
        if behavior.fraud_hotline_called:
            score += 20.0

        return min(score, 100.0)
