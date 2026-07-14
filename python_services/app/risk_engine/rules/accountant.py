"""
会计/财务人群差异化风险规则
会计群体特点：掌握公司资金、易受冒充老板/财务诈骗、单笔转账金额大
"""

from __future__ import annotations

from typing import Any, Dict, List

# 会计/财务人群维度权重（交易行为权重极高）
WEIGHTS: Dict[str, float] = {
    "call": 0.10,          # 通话风险
    "sms": 0.05,           # 短信风险较低
    "transaction": 0.45,   # 交易风险极高（大额转账）
    "app": 0.05,           # 应用使用
    "network": 0.15,       # 网络行为（钓鱼邮件等）
    "device": 0.05,        # 设备风险
    "account": 0.10,       # 账户安全
    "reported": 0.05,      # 举报记录
}

# 会计重点关注的关键词
KEYWORDS: List[str] = [
    "老板", "转账", "汇款", "对公账户",
    "紧急", "机密", "不要声张", "财务审批",
    "税务稽查", "审计", "年检",
    "QQ群", "微信群", "公司内部群",
    "发票", "电子发票", "税务链接",
    "U盾", "网银", "对账",
]

# 会计群体风险提示语
RISK_TIPS: List[str] = [
    "收到老板通过QQ/微信要求转账的消息，务必电话或当面确认",
    "公司财务转账必须严格执行审批流程",
    "不要点击来历不明的'税务'链接或附件",
    "财务人员应定期参加反诈培训，提高防范意识",
]


def get_accountant_rule_context() -> Dict[str, Any]:
    """获取会计人群的完整规则上下文"""
    return {
        "group": "accountant",
        "group_name": "会计/财务",
        "weights": WEIGHTS,
        "keywords": KEYWORDS,
        "risk_tips": RISK_TIPS,
    }
