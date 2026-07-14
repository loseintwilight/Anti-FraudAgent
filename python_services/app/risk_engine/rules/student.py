"""
学生人群差异化风险规则
学生群体特点：社会经验不足、易受刷单/游戏诈骗、零花钱有限
"""

from __future__ import annotations

from typing import Any, Dict, List

# 学生人群维度权重（交易和短信权重更高）
WEIGHTS: Dict[str, float] = {
    "call": 0.10,          # 学生通话相对少
    "sms": 0.15,           # 短信/社交较多
    "transaction": 0.25,   # 交易额通常不大，但易被骗
    "app": 0.15,           # 应用使用活跃
    "network": 0.15,       # 网络行为活跃
    "device": 0.05,        # 设备风险
    "account": 0.10,       # 账户安全
    "reported": 0.05,      # 举报记录
}

# 学生重点关注的关键词
KEYWORDS: List[str] = [
    "刷单", "兼职", "日结", "打字员", "游戏代练",
    "充值返利", "免费领取", "扫码", "红包群",
    "学生贷", "校园贷", "零门槛", "信用贷",
]

# 学生人群风险提示语
RISK_TIPS: List[str] = [
    "学生朋友要提高警惕，不要轻信'轻松赚钱'的兼职广告",
    "凡是要求先付款的兼职都是诈骗",
    "不要向任何人透露银行卡验证码",
    "游戏交易请走官方平台，勿私下转账",
]


def get_student_rule_context() -> Dict[str, Any]:
    """获取学生人群的完整规则上下文"""
    return {
        "group": "student",
        "group_name": "学生",
        "weights": WEIGHTS,
        "keywords": KEYWORDS,
        "risk_tips": RISK_TIPS,
    }
