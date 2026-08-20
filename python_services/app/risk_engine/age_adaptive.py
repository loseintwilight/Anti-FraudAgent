"""
年龄自适应调权模块
根据用户年龄段自动调整风险维度权重
- 老年用户 × 冒充公检法 → 置信度 × 1.3
- 青年用户 × 刷单返利 → 置信度 × 1.2
- 学生用户 × 游戏交易 → 置信度 × 1.25
"""
from __future__ import annotations

from typing import Dict

# 年龄分组
AGE_GROUPS = {
    "child": (0, 12),
    "student": (13, 22),
    "youth": (23, 35),
    "middle": (36, 50),
    "elderly": (51, 150),
}

# 诈骗类型 × 年龄组 → 权重调整系数
AGE_ADAPTIVE_BOOST: Dict[str, Dict[str, float]] = {
    "冒充公检法": {
        "elderly": 1.30,  # 老年人最易受冒充公检法诈骗
        "middle": 1.10,
        "youth": 1.00,
        "student": 0.95,
        "child": 0.90,
    },
    "刷单返利": {
        "youth": 1.20,   # 青年人最易受刷单诈骗
        "student": 1.15,
        "middle": 1.00,
        "elderly": 0.85,
        "child": 0.80,
    },
    "虚假投资": {
        "middle": 1.20,  # 中年人最易受投资诈骗
        "elderly": 1.15,
        "youth": 1.00,
        "student": 0.80,
        "child": 0.70,
    },
    "杀猪盘": {
        "youth": 1.20,
        "middle": 1.15,
        "elderly": 1.10,
        "student": 0.90,
        "child": 0.70,
    },
    "客服退款": {
        "youth": 1.20,
        "student": 1.15,
        "middle": 1.00,
        "elderly": 0.90,
        "child": 0.85,
    },
    "虚假贷款": {
        "youth": 1.20,
        "middle": 1.15,
        "elderly": 0.90,
        "student": 0.85,
        "child": 0.70,
    },
    "游戏交易": {
        "student": 1.25,  # 学生最易受游戏交易诈骗
        "child": 1.20,
        "youth": 1.00,
        "middle": 0.70,
        "elderly": 0.60,
    },
    "AI合成诈骗": {
        "elderly": 1.25,  # 老年人对AI技术认知不足
        "middle": 1.15,
        "youth": 1.10,
        "student": 1.00,
        "child": 0.95,
    },
    "default": {
        "elderly": 1.15,
        "middle": 1.05,
        "youth": 1.00,
        "student": 0.95,
        "child": 0.90,
    },
}


def get_age_group(age: int) -> str:
    """根据年龄获取年龄分组"""
    for group_name, (min_age, max_age) in AGE_GROUPS.items():
        if min_age <= age <= max_age:
            return group_name
    return "youth"


def get_adaptive_boost(fraud_type: str, age: int) -> float:
    """
    获取年龄自适应调权系数

    参数:
        fraud_type: 诈骗类型
        age: 用户年龄

    返回:
        调权系数 (1.0 为基准，>1.0 为提高置信度)
    """
    age_group = get_age_group(age)
    type_boosts = AGE_ADAPTIVE_BOOST.get(fraud_type, AGE_ADAPTIVE_BOOST["default"])
    return type_boosts.get(age_group, 1.0)


def apply_age_adaptive_boost(confidence: float, fraud_type: str, age: int) -> float:
    """
    应用年龄自适应调权
    返回调整后的置信度（上限 1.0）
    """
    boost = get_adaptive_boost(fraud_type, age)
    boosted = confidence * boost
    return min(boosted, 1.0)


def get_boost_detail(fraud_type: str, age: int) -> dict:
    """获取调权详情"""
    age_group = get_age_group(age)
    boost = get_adaptive_boost(fraud_type, age)
    return {
        "age": age,
        "age_group": age_group,
        "fraud_type": fraud_type,
        "boost_coefficient": boost,
        "applied": boost != 1.0,
    }