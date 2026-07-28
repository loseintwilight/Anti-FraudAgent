"""
风险评估模块 — 对应升级方案 Section 3.1

功能说明：
- 根据用户输入内容进行多维度风险评估
- 识别诈骗类型和风险等级
- 支持关键词匹配 + 规则引擎双重判断
"""

import re
from typing import Dict, List, Optional, Tuple

from ..core.retriever import rag_retriever
from ..knowledge.fraud_kb import fraud_kb
from ..models.schemas import RiskItem, RiskLevel
from ..utils.logger import logger


class RiskAssessor:
    """
    风险评估引擎

    根据用户输入内容进行多维度风险评估：
    1. 关键词匹配：识别诈骗类型关键词
    2. 风险行为检测：识别高风险行为（转账、提供验证码等）
    3. 紧急程度判断：根据时间、金额、语气等判断紧急程度
    """

    # 高风险行为关键词
    HIGH_RISK_ACTIONS: List[str] = [
        "转账", "汇款", "打款", "付钱", "交钱", "充值",
        "提供验证码", "告诉验证码", "输入验证码",
        "下载APP", "安装软件", "屏幕共享", "远程控制",
        "网贷", "贷款", "借钱", "套现",
    ]

    # 极高风险行为关键词
    EXTREME_RISK_ACTIONS: List[str] = [
        "已经转账", "已经汇款", "已经打款", "已经付了",
        "收到验证码", "发过去了", "已经给了",
        "输了密码", "已经付款", "刷了", "投了",
    ]

    # 紧急程度关键词
    URGENCY_KEYWORDS: List[str] = [
        "马上", "立刻", "赶紧", "快点", "急", "来不及",
        "最后期限", "今天内", "现在就要", "过期",
    ]

    def __init__(self):
        self.fraud_types = fraud_kb.get_fraud_types()
        logger.info("风险评估引擎初始化完成")

    def assess(self, query: str, user_role: str = "unknown") -> Tuple[RiskLevel, str, float, List[RiskItem]]:
        """
        对用户输入进行风险评估

        Args:
            query: 用户输入
            user_role: 用户角色

        Returns:
            (风险等级, 诈骗类型, 置信度, 风险项明细列表)
        """
        logger.info(f"风险评估开始: query={query[:50]}, role={user_role}")

        risk_items: List[RiskItem] = []
        total_score = 0.0
        fraud_type = "unknown"

        # 1. 诈骗类型识别
        detected_type = rag_retriever.get_fraud_type(query)
        if detected_type:
            fraud_type = detected_type
            risk_items.append(RiskItem(
                source="用户输入",
                risk_type=detected_type,
                risk_score=30.0,
                explanation=f"检测到用户描述疑似{detected_type}"
            ))
            total_score += 30.0

        # 2. 高风险行为检测
        for action in self.HIGH_RISK_ACTIONS:
            if action in query:
                risk_items.append(RiskItem(
                    source="用户输入",
                    risk_type="高风险行为",
                    risk_score=20.0,
                    explanation=f"检测到高风险行为: {action}"
                ))
                total_score += 20.0

        # 3. 极高风险行为检测（已经发生的行为）
        for action in self.EXTREME_RISK_ACTIONS:
            if action in query:
                risk_items.append(RiskItem(
                    source="用户输入",
                    risk_type="极高风险行为",
                    risk_score=50.0,
                    explanation=f"检测到极高风险行为: {action}（可能已发生损失）"
                ))
                total_score += 50.0

        # 4. 紧急程度检测
        for keyword in self.URGENCY_KEYWORDS:
            if keyword in query:
                risk_items.append(RiskItem(
                    source="用户输入",
                    risk_type="紧急程度",
                    risk_score=10.0,
                    explanation=f"检测到紧急关键词: {keyword}"
                ))
                total_score += 10.0
                break

        # 5. 金额相关检测
        money_pattern = re.findall(r"(\d+)[万万千]?[元块钱]", query)
        if money_pattern:
            amount = int(money_pattern[0])
            if amount >= 10000:
                risk_items.append(RiskItem(
                    source="用户输入",
                    risk_type="大额资金",
                    risk_score=25.0,
                    explanation=f"检测到大额资金: {amount}元"
                ))
                total_score += 25.0
            elif amount >= 1000:
                risk_items.append(RiskItem(
                    source="用户输入",
                    risk_type="资金风险",
                    risk_score=10.0,
                    explanation=f"涉及资金: {amount}元"
                ))
                total_score += 10.0

        # 综合判定风险等级
        risk_level = self._determine_risk_level(total_score)
        confidence = min(total_score / 100.0, 1.0)

        logger.info(
            f"风险评估完成: level={risk_level.value}, "
            f"fraud_type={fraud_type}, score={total_score:.1f}, "
            f"confidence={confidence:.2f}"
        )

        return risk_level, fraud_type, confidence, risk_items

    def _determine_risk_level(self, score: float) -> RiskLevel:
        """根据总分判定风险等级"""
        if score >= 80:
            return RiskLevel.EXTREME
        elif score >= 40:
            return RiskLevel.HIGH
        elif score >= 15:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW

    def get_prevention_tips(self, fraud_type: str) -> List[str]:
        """
        根据诈骗类型获取防范建议

        Args:
            fraud_type: 诈骗类型

        Returns:
            防范建议列表
        """
        tips_map: Dict[str, List[str]] = {
            "冒充公检法诈骗": [
                "公检法机关不会通过电话办案，更不会设立「安全账户」",
                "立即挂断电话，不要透露任何个人信息",
                "拨打110或96110核实对方身份",
                "不要向任何陌生账户转账",
            ],
            "刷单返利诈骗": [
                "所有「先垫资后返利」的兼职均为诈骗",
                "已经垫付的钱不要再追加，立刻止损",
                "正规兼职不会让你先交钱",
                "不要相信「轻松赚钱」的广告",
            ],
            "杀猪盘诈骗": [
                "网恋对象带你投资赚钱，100%是诈骗",
                "不要向陌生账户转账投资",
                "平台后台可以操控数据，显示盈利但无法提现",
                "立即停止与对方联系，并拉黑",
            ],
            "冒充客服诈骗": [
                "主动联系你退款的要警惕，直接在官方APP核实",
                "不要通过对方提供的链接或二维码操作",
                "索要验证码、银行卡号的全是诈骗",
                "不要开启屏幕共享或远程控制",
            ],
            "网络贷款诈骗": [
                "正规贷款不会提前收取任何费用",
                "放款前要求交保证金、解冻费的全是诈骗",
                "急需用钱请选择正规银行渠道",
                "不要轻信「无抵押秒到账」的广告",
            ],
            "冒充熟人领导诈骗": [
                "接到紧急转账要求，必须电话或当面核实",
                "不要仅凭QQ、微信消息转账",
                "严格执行公司财务审批制度",
                "涉及资金务必双重确认",
            ],
            "AI换脸诈骗": [
                "视频通话中看到熟人借钱要求转账的，也要通过其他方式核实",
                "AI可以伪造面部和声音，不要仅凭视频确认身份",
                "设置与亲友的「暗号」用于紧急情况核实",
            ],
            "游戏诈骗": [
                "没有免费的皮肤，说免费的都是骗人的",
                "不要给陌生人账号密码",
                "不要扫描陌生人发来的二维码",
                "交易请走官方渠道",
            ],
            "保健品诈骗": [
                "保健品不能治病，看病要去正规医院",
                "声称「能治百病」的均为诈骗",
                "不要轻信「免费体检」「养生讲座」",
                "购买药品请到正规药店",
            ],
            "征信修复诈骗": [
                "征信记录由中国人民银行统一管理，无法人工修复",
                "不良记录5年后自动消除，无需花钱处理",
                "声称可以「洗白征信」的全是诈骗",
            ],
            "跑分洗钱诈骗": [
                "跑分洗钱是违法犯罪行为，将面临刑事责任",
                "不要出租、出借银行卡和电话卡",
                "不要帮忙转账「走账」赚取提成",
                "发现此类行为请立即报警",
            ],
            "中奖诈骗": [
                "未参与的活动不会中奖",
                "要求先交税费、手续费才能领奖的全是诈骗",
                "天上不会掉馅饼，不要贪图小便宜",
            ],
        }

        return tips_map.get(fraud_type, [
            "不要向陌生账户转账",
            "不要提供验证码和银行卡号",
            "如有疑问拨打96110反诈专线咨询",
        ])

    def get_transfer_warning(self, risk_level: RiskLevel) -> str:
        """
        根据风险等级生成转账拦截提醒

        Args:
            risk_level: 风险等级

        Returns:
            转账拦截提醒文本
        """
        warnings = {
            RiskLevel.EXTREME: (
                "⚠️ 紧急警告：您可能正在遭受诈骗！请立即停止任何转账操作！"
                "不要提供验证码，不要点击链接，立即拨打110报警！"
            ),
            RiskLevel.HIGH: (
                "⚠️ 风险警告：您当前操作存在较高风险！"
                "请暂停转账，核实对方身份后再操作。"
                "如有疑问请拨打96110反诈专线咨询。"
            ),
            RiskLevel.MEDIUM: (
                "⚠️ 温馨提示：请注意保护个人信息，"
                "不要向陌生人转账或提供验证码。"
            ),
            RiskLevel.LOW: (
                "✅ 当前未检测到明显风险，但仍请注意保护个人信息安全。"
            ),
        }
        return warnings.get(risk_level, warnings[RiskLevel.LOW])


# 全局单例
risk_assessor = RiskAssessor()