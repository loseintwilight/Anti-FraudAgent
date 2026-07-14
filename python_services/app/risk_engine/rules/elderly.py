"""
老年人人群差异化风险规则
老年人群体特点：防范意识弱、易信保健品/养老诈骗、对新技术不熟悉
"""

from __future__ import annotations

from typing import Any, Dict, List

# 老年人人群维度权重（通话和网络权重更高，因老年人更易受电话/网络诈骗）
WEIGHTS: Dict[str, float] = {
    "call": 0.25,          # 电话诈骗是老年人主要风险来源
    "sms": 0.05,           # 短信使用较少
    "transaction": 0.25,   # 大额转账风险高
    "app": 0.05,           # 应用使用较少
    "network": 0.20,       # 网络诈骗也需重视
    "device": 0.05,        # 设备风险
    "account": 0.10,       # 账户安全
    "reported": 0.05,      # 举报记录
}

# 老年人重点关注的关键词
KEYWORDS: List[str] = [
    "保健品", "特效药", "神医", "免费体检",
    "养老项目", "以房养老", "养老保险",
    "收藏品", "艺术品投资", "高回报理财",
    "中奖", "幸运用户", "免费领",
    "孙子", "孙女", "出事", "急需用钱",
    "安全账户", "资金转移", "洗钱",
]

# 老年人群体风险提示语
RISK_TIPS: List[str] = [
    "接到陌生电话提到'安全账户'，一定是诈骗，请立即挂断",
    "不要轻信保健品推销，看病要去正规医院",
    "任何自称公检法要求转账的都是诈骗",
    "投资养老项目前一定要和子女商量",
]


def get_elderly_rule_context() -> Dict[str, Any]:
    """获取老年人群体的完整规则上下文"""
    return {
        "group": "elderly",
        "group_name": "老年人",
        "weights": WEIGHTS,
        "keywords": KEYWORDS,
        "risk_tips": RISK_TIPS,
    }
