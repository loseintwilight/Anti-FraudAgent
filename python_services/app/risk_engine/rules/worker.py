"""
上班族人群差异化风险规则
上班族群体特点：有一定经济能力、易受投资/贷款/冒充客服诈骗、工作忙防范松懈
"""

from __future__ import annotations

from typing import Any, Dict, List

# 上班族人群维度权重（交易和网络权重最高）
WEIGHTS: Dict[str, float] = {
    "call": 0.10,          # 通话风险适中
    "sms": 0.10,           # 短信风险适中
    "transaction": 0.30,   # 交易频繁、金额大，风险最高
    "app": 0.10,           # 应用使用
    "network": 0.20,       # 网络行为活跃
    "device": 0.05,        # 设备风险
    "account": 0.10,       # 账户安全
    "reported": 0.05,      # 举报记录
}

# 上班族重点关注的关键词
KEYWORDS: List[str] = [
    "投资", "理财", "股票", "基金", "期货",
    "高收益", "稳赚不赔", "内部消息", "涨停板",
    "贷款", "低息", "无抵押", "快速放款",
    "冒充客服", "退款", "理赔", "双倍退款",
    "注销账户", "影响征信", "信用修复",
    "刷流水", "保证金", "解冻费",
]

# 上班族风险提示语
RISK_TIPS: List[str] = [
    "不要轻信'高收益、零风险'的投资理财广告",
    "凡是自称电商客服主动退款、要求先转账的都是诈骗",
    "贷款请选择正规金融机构，不要先交保证金",
    "任何声称可以'洗白征信'的都是诈骗",
]


def get_worker_rule_context() -> Dict[str, Any]:
    """获取上班族人群的完整规则上下文"""
    return {
        "group": "worker",
        "group_name": "上班族",
        "weights": WEIGHTS,
        "keywords": KEYWORDS,
        "risk_tips": RISK_TIPS,
    }
