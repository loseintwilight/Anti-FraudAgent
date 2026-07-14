"""
诈骗类型分类器
基于关键词匹配 + 简单规则判断诈骗类型

支持的诈骗类型:
  1. 刷单返利
  2. 虚假投资
  3. 冒充公检法
  4. 杀猪盘
  5. 冒充客服
  6. 虚假贷款
  7. 未知（无法匹配时）
"""

from __future__ import annotations

import logging
import re
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


# 各类诈骗的关键词规则
# 每个类别包含: 关键词列表、权重、类别标签、建议
FRAUD_PATTERNS = [
    {
        "type": "刷单返利",
        "keywords": [
            "刷单", "刷信誉", "刷流水", "兼职刷单",
            "日结", "月入过万", "足不出户", "轻松赚钱",
            "打字员", "点赞员", "试玩员", "手工活",
            "任务佣金", "先垫付", "做完返还",
        ],
        "weight": 1.0,
        "suggestion": "切勿参与任何形式的刷单兼职，所有要求垫付资金的兼职都是诈骗。",
    },
    {
        "type": "虚假投资",
        "keywords": [
            "高收益", "稳赚不赔", "保本保息", "内部消息",
            "涨停板", "原始股", "数字货币", "虚拟货币",
            "区块链投资", "外汇投资", "黄金投资",
            "导师带单", "喊单", "跟着做单",
            "投资返利", "分红", "资金盘",
        ],
        "weight": 1.0,
        "suggestion": "投资理财请选择正规金融机构，切勿轻信'高收益、零风险'的虚假宣传。",
    },
    {
        "type": "冒充公检法",
        "keywords": [
            "安全账户", "资金清查", "洗钱", "涉案",
            "通缉令", "逮捕令", "法院传票",
            "公安局", "检察院", "税务局", "经侦",
            "配合调查", "保密案件", "不要告诉任何人",
            "视频笔录", "远程办案", "资金转移",
        ],
        "weight": 1.2,  # 冒充公检法危害大，权重偏高
        "suggestion": "公检法机关不会通过电话办案，更不会要求转账到'安全账户'，请立即挂断并拨打 96110 核实。",
    },
    {
        "type": "杀猪盘",
        "keywords": [
            "网恋", "交友", "女朋友", "男朋友",
            "带赚钱", "带我投资", "未来规划",
            "奔现", "见面礼", "彩礼",
            "博彩", "彩票", "投注", "内幕",
            "下载APP", "充值通道", "提现失败",
        ],
        "weight": 1.0,
        "suggestion": "网络交友需谨慎，任何以'带你赚钱'为名的网恋对象都要提高警惕。",
    },
    {
        "type": "冒充客服",
        "keywords": [
            "退款", "理赔", "双倍退款", "质量问题退款",
            "注销账户", "注销会员", "取消业务",
            "影响征信", "信用修复", "征信异常",
            "备用金", "理赔金", "验证金",
            "屏幕共享", "远程协助", "下载会议软件",
        ],
        "weight": 1.0,
        "suggestion": "接到自称客服退款电话，请通过官方平台核实，切勿开启屏幕共享功能。",
    },
    {
        "type": "虚假贷款",
        "keywords": [
            "低息贷款", "无抵押", "不看征信", "秒到账",
            "快速放款", "黑户可贷", "网贷",
            "手续费", "保证金", "解冻费", "验资费",
            "刷流水", "包装费", "会员费",
        ],
        "weight": 1.0,
        "suggestion": "贷款请选择正规金融机构，任何放款前要求缴纳费用的都是诈骗。",
    },
]


class FraudClassifier:
    """
    诈骗类型分类器
    基于关键词匹配+规则判断，支持多类型识别和年龄辅助
    """

    def classify(self, text: str, age: Optional[int] = None) -> Dict[str, Any]:
        """
        对输入文本进行诈骗类型分类

        参数:
            text: 待分类文本（聊天记录、短信、通话内容等）
            age: 用户年龄（可选，用于辅助判断）

        返回:
            {
                "fraud_type": 诈骗类型,
                "confidence": 置信度 (0-1),
                "matched_keywords": 匹配到的关键词,
                "suggestion": 建议
            }
        """
        logger.info(f"开始诈骗分类: 文本长度={len(text)}, age={age}")

        if not text or not text.strip():
            return {
                "fraud_type": "未知",
                "confidence": 0.0,
                "matched_keywords": [],
                "suggestion": "无法分析空文本",
            }

        text_lower = text.lower()

        # 各类型匹配情况
        match_results: List[Tuple[str, float, List[str], str]] = []

        for pattern in FRAUD_PATTERNS:
            matched_kws = self._match_keywords(text_lower, pattern["keywords"])
            if matched_kws:
                # 基础置信度 = 匹配关键词数 / 总关键词数 * 权重
                base_confidence = len(matched_kws) / max(len(pattern["keywords"]), 1)
                confidence = min(base_confidence * pattern["weight"], 1.0)
                match_results.append(
                    (pattern["type"], confidence, matched_kws, pattern["suggestion"])
                )

        if not match_results:
            # 未匹配到任何诈骗类型
            suggestion = "未检测到明显的诈骗特征，但仍需保持警惕。"
            # 如果文本中包含一些通用的可疑词汇
            suspicious_general = self._check_general_suspicious(text_lower)
            if suspicious_general:
                suggestion = "文本中包含可疑元素，请提高警惕。"
                return {
                    "fraud_type": "可疑",
                    "confidence": 0.3,
                    "matched_keywords": suspicious_general,
                    "suggestion": suggestion,
                }
            return {
                "fraud_type": "未知",
                "confidence": 0.0,
                "matched_keywords": [],
                "suggestion": suggestion,
            }

        # 按置信度排序，取最高分
        match_results.sort(key=lambda x: x[1], reverse=True)
        best_match = match_results[0]

        # 年龄辅助调整
        fraud_type = best_match[0]
        confidence = best_match[1]

        if age is not None:
            confidence = self._age_adjust(age, fraud_type, confidence)

        result = {
            "fraud_type": fraud_type,
            "confidence": round(confidence, 4),
            "matched_keywords": best_match[2],
            "suggestion": best_match[3],
        }

        logger.info(
            f"分类结果: type={fraud_type}, "
            f"confidence={confidence:.4f}, "
            f"keywords={best_match[2]}"
        )
        return result

    @staticmethod
    def _match_keywords(text: str, keywords: List[str]) -> List[str]:
        """
        匹配文本中是否包含指定关键词
        返回匹配到的关键词列表
        """
        matched = []
        for kw in keywords:
            # 使用正则进行模糊匹配，提高匹配率
            if re.search(re.escape(kw), text):
                matched.append(kw)
        return matched

    @staticmethod
    def _check_general_suspicious(text: str) -> List[str]:
        """检查通用的可疑词汇"""
        suspicious_words = [
            "转账", "汇款", "验证码", "银行卡",
            "身份证", "密码", "账号", "扫码",
            "链接", "点击", "下载", "安装",
        ]
        return [w for w in suspicious_words if w in text]

    @staticmethod
    def _age_adjust(age: int, fraud_type: str, confidence: float) -> float:
        """
        根据年龄对置信度进行调整
        不同年龄段易受不同诈骗类型影响
        """
        # 学生更易受刷单诈骗
        if fraud_type == "刷单返利" and 6 <= age <= 22:
            confidence = min(confidence + 0.1, 1.0)
        # 老年人更易受冒充公检法诈骗
        elif fraud_type == "冒充公检法" and age >= 50:
            confidence = min(confidence + 0.15, 1.0)
        # 上班族更易受投资/贷款诈骗
        elif fraud_type in ("虚假投资", "虚假贷款") and 22 <= age <= 50:
            confidence = min(confidence + 0.1, 1.0)
        return confidence
