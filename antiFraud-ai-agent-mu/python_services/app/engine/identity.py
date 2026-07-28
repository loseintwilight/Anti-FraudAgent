"""
用户身份智能识别引擎 — 对应升级方案 Section 3.1.1

功能说明：
- 根据用户提问内容、语气、关键词、自述身份等信息，动态判断用户角色类型
- 身份判断随对话轮次动态更新，每轮对话结束后更新用户画像
- 每次对话后更新评估，确保长期使用的准确性
"""

import re
from typing import Dict, List, Optional

from ..models.schemas import UserProfile, UserRole
from ..utils.logger import logger


class IdentityEngine:
    """
    用户身份智能识别引擎

    通过多维度特征匹配来判断用户角色：
    1. 自述身份关键词（如"我今年60岁""我是会计"）
    2. 语气特征（如口语化程度、词汇复杂度）
    3. 问题类型关键词（如"养老金""游戏皮肤""公司转账"）
    4. 对话历史累积判断
    """

    # 角色特征关键词映射
    _ROLE_PATTERNS: Dict[UserRole, List[str]] = {
        UserRole.ELDERLY: [
            "退休", "养老金", "养老", "老伙计", "我今年", "60", "70", "80",
            "老同志", "老年人", "保健品", "养生", "免费体检",
            "儿子", "女儿", "孙子", "孙女", "老伴",
        ],
        UserRole.YOUTH: [
            "刷单", "兼职", "投资", "理财", "贷款", "网贷",
            "杀猪盘", "网恋", "虚拟货币", "炒股",
            "信用卡", "花呗", "借呗", "额度",
            "征信", "逾期", "裸聊", "跑分",
        ],
        UserRole.CHILD: [
            "游戏皮肤", "免费皮肤", "氪金", "王者荣耀", "吃鸡",
            "和平精英", "原神", "蛋仔派对", "我的世界",
            "作业", "老师", "同学", "家长",
            "零花钱", "小学生", "初中生",
        ],
        UserRole.ACCOUNTANT: [
            "会计", "财务", "出纳", "对公账户", "公司转账",
            "老板让我转账", "领导要求转账", "审批", "发票",
            "税务", "对账", "报销", "公司账户",
        ],
        UserRole.WORKER: [
            "找工作", "招聘", "面试", "入职", "押金",
            "培训费", "兼职", "日结", "工资",
            "老板", "工头", "劳务", "合同",
            "外卖", "快递", "网约车",
        ],
    }

    # 自述身份正则（如"我是XX"、"我今年XX岁"）
    _SELF_IDENTITY_PATTERNS: Dict[UserRole, List[str]] = {
        UserRole.ELDERLY: [
            r"我今年.*[6-8]\d岁", r"我退休", r"我是老年人",
            r"我[6-8]\d岁了", r"我年龄大了",
        ],
        UserRole.YOUTH: [
            r"我是大学生", r"我刚毕业", r"我在上班",
            r"我[2-3]\d岁", r"我今年.*[2-3]\d岁",
        ],
        UserRole.CHILD: [
            r"我是小学生", r"我是初中生", r"我[1-1][0-5]岁",
            r"我今年.*1[0-5]岁", r"我还是个孩子",
        ],
        UserRole.ACCOUNTANT: [
            r"我是会计", r"我是财务", r"我是出纳",
            r"我是做财务的", r"我在财务部",
        ],
        UserRole.WORKER: [
            r"我是打工的", r"我是自由职业", r"我在找工作",
            r"我是做.*的",  # 模糊匹配：我是做XX的
        ],
    }

    # 各角色对应的风险关注点
    _ROLE_RISK_FOCUS: Dict[UserRole, List[str]] = {
        UserRole.ELDERLY: ["冒充公检法诈骗", "保健品诈骗", "冒充熟人诈骗", "中奖诈骗"],
        UserRole.YOUTH: ["刷单返利诈骗", "杀猪盘诈骗", "网络贷款诈骗", "征信修复诈骗"],
        UserRole.CHILD: ["游戏诈骗", "中奖诈骗", "冒充熟人诈骗"],
        UserRole.ACCOUNTANT: ["冒充熟人领导诈骗", "虚假财税诈骗"],
        UserRole.WORKER: ["虚假招聘诈骗", "冒充客服诈骗", "网络贷款诈骗"],
    }

    def __init__(self):
        self._confidence_history: Dict[str, Dict[UserRole, float]] = {}
        logger.info("用户身份识别引擎初始化完成")

    def identify(self, user_id: str, query: str, history: List[str]) -> UserRole:
        """
        识别用户身份角色

        Args:
            user_id: 用户唯一标识
            query: 当前用户输入
            history: 历史输入列表

        Returns:
            识别到的用户角色
        """
        # 初始化该用户的置信度记录
        if user_id not in self._confidence_history:
            self._confidence_history[user_id] = {
                role: 0.0 for role in UserRole
            }

        # 累计所有输入
        all_queries = history + [query]
        current_scores = self._confidence_history[user_id]

        # 多维度评分
        for query_text in all_queries:
            scores = self._score_single_query(query_text)
            for role, score in scores.items():
                current_scores[role] = current_scores.get(role, 0.0) + score

        # 取最高分角色
        best_role = max(current_scores, key=current_scores.get)
        best_score = current_scores[best_role]

        # 如果最高分仍为0，返回 unknown
        if best_score <= 0:
            return UserRole.UNKNOWN

        # 检查是否有多角色混淆（分数接近的情况）
        sorted_roles = sorted(current_scores.items(), key=lambda x: x[1], reverse=True)
        if len(sorted_roles) >= 2:
            top_score = sorted_roles[0][1]
            second_score = sorted_roles[1][1]
            # 如果前两名分数差距小于20%，认为角色不明确
            if top_score > 0 and second_score / top_score > 0.8:
                logger.info(
                    f"用户角色不明确 (top={sorted_roles[0][0].value}:{top_score:.1f}, "
                    f"second={sorted_roles[1][0].value}:{second_score:.1f})"
                )
                return UserRole.UNKNOWN

        logger.info(
            f"用户身份识别结果: user_id={user_id}, "
            f"role={best_role.value}, score={best_score:.1f}"
        )
        return best_role

    def _score_single_query(self, query: str) -> Dict[UserRole, float]:
        """
        对单条输入进行角色评分

        Args:
            query: 用户输入

        Returns:
            各角色得分
        """
        scores = {role: 0.0 for role in UserRole}

        # 1. 自述身份匹配（权重最高，命中即大幅度加分）
        for role, patterns in self._SELF_IDENTITY_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, query):
                    scores[role] += 5.0
                    logger.debug(f"自述身份匹配: role={role.value}, pattern={pattern}")

        # 2. 关键词匹配
        for role, keywords in self._ROLE_PATTERNS.items():
            for kw in keywords:
                if kw in query:
                    scores[role] += 1.0

        # 3. 语气特征分析
        tone_score = self._analyze_tone(query)
        for role, delta in tone_score.items():
            scores[role] = scores.get(role, 0.0) + delta

        return scores

    def _analyze_tone(self, query: str) -> Dict[UserRole, float]:
        """
        分析语气特征

        Args:
            query: 用户输入

        Returns:
            各角色语气得分
        """
        scores = {role: 0.0 for role in UserRole}

        # 老年人语气特征：简洁、口语化、使用"吧""嘛""啊"等语气词
        elderly_tone = len(re.findall(r"[吧嘛啊唉哟]", query))
        if elderly_tone > 0:
            scores[UserRole.ELDERLY] += elderly_tone * 0.5

        # 青年语气特征：使用网络用语、表情符号等
        youth_tone = len(re.findall(r"[哈笑晕哭裂开]", query))
        if youth_tone > 0:
            scores[UserRole.YOUTH] += youth_tone * 0.3

        # 少儿语气特征：简单短句、使用"吗""呢""呀"等疑问语气
        child_tone = len(re.findall(r"[吗呢呀哇]", query))
        if child_tone > 0 and len(query) < 20:
            scores[UserRole.CHILD] += child_tone * 0.5

        # 财会人员语气特征：专业术语、正式表达
        accountant_tone = len(re.findall(r"[审核审批流程制度合规]", query))
        if accountant_tone > 0:
            scores[UserRole.ACCOUNTANT] += accountant_tone * 0.3

        return scores

    def get_risk_focus(self, role: UserRole) -> List[str]:
        """
        获取指定角色重点关注的风险类型

        Args:
            role: 用户角色

        Returns:
            重点关注的风险类型列表
        """
        return self._ROLE_RISK_FOCUS.get(role, [])

    def update_profile_from_role(self, profile: UserProfile, role: UserRole):
        """
        根据识别到的角色更新用户画像

        Args:
            profile: 用户画像对象
            role: 识别到的角色
        """
        if role == UserRole.UNKNOWN:
            return

        profile.role = role

        role_meta = {
            UserRole.ELDERLY: {"age_group": "老年", "occupation_tag": "退休"},
            UserRole.YOUTH: {"age_group": "青年", "occupation_tag": "学生/在职"},
            UserRole.CHILD: {"age_group": "少儿", "occupation_tag": "学生"},
            UserRole.ACCOUNTANT: {"age_group": "中年", "occupation_tag": "财会"},
            UserRole.WORKER: {"age_group": "中年", "occupation_tag": "自由职业/务工"},
        }

        meta = role_meta.get(role, {})
        profile.age_group = meta.get("age_group", profile.age_group)
        profile.occupation_tag = meta.get("occupation_tag", profile.occupation_tag)

        logger.info(f"用户画像已更新: role={role.value}, age_group={profile.age_group}")


# 全局单例
identity_engine = IdentityEngine()