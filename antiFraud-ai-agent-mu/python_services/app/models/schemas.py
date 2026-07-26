"""
数据模型定义
包含请求/响应结构体、用户画像、风险报告等核心数据结构
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class RiskLevel(str, Enum):
    """风险等级枚举"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EXTREME = "extreme"


class UserRole(str, Enum):
    """用户角色枚举"""
    ACCOUNTANT = "accountant"      # 财会人员
    WORKER = "worker"              # 自由职业者/务工人员
    ELDERLY = "elderly"            # 老年人
    YOUTH = "youth"                # 青年
    CHILD = "child"                # 少儿
    UNKNOWN = "unknown"            # 未识别


class SceneType(str, Enum):
    """对话场景类型"""
    CHAT = "chat"                  # 闲聊模式
    KNOWLEDGE = "knowledge"        # 咨询/科普模式
    RISK_DETECT = "risk_detect"    # 反诈预警模式


class IntentType(str, Enum):
    """意图类型"""
    GREETING = "greeting"          # 问候
    INQUIRY = "inquiry"            # 咨询
    REPORT = "report"              # 举报
    RISK_CHECK = "risk_check"      # 风险检测
    UNKNOWN = "unknown"            # 未知


@dataclass
class Message:
    """单条对话消息"""
    role: str                      # user / assistant / system
    content: str
    timestamp: Optional[float] = None


@dataclass
class UserProfile:
    """用户风险画像 — 对应升级方案 Section 3.1.1"""
    user_id: str
    age_group: str = "unknown"     # 学生/青年/中年/老年
    occupation_tag: str = "unknown"  # 财会/自由职业/务工/退休/学生
    role: UserRole = UserRole.UNKNOWN
    risk_score: float = 0.0
    risk_level: RiskLevel = RiskLevel.LOW
    risk_sources: Dict[str, float] = field(default_factory=dict)
    conversation_turns: int = 0
    query_history: List[str] = field(default_factory=list)

    def add_risk_source(self, source_name: str, score: float):
        """为风险项添加具体来源标注"""
        self.risk_sources[source_name] = self.risk_sources.get(source_name, 0) + score
        self.risk_score = sum(self.risk_sources.values())
        self._update_risk_level()

    def _update_risk_level(self):
        """根据累计风险分更新风险等级"""
        if self.risk_score >= 80:
            self.risk_level = RiskLevel.EXTREME
        elif self.risk_score >= 50:
            self.risk_level = RiskLevel.HIGH
        elif self.risk_score >= 20:
            self.risk_level = RiskLevel.MEDIUM
        else:
            self.risk_level = RiskLevel.LOW


@dataclass
class RiskItem:
    """风险项明细 — 对应升级方案 Section 3.2.1"""
    source: str                    # 风险来源（如"短信内容""聊天记录"）
    risk_type: str                 # 风险类型
    risk_score: float              # 单项风险分值
    explanation: str               # 风险说明


@dataclass
class FraudReport:
    """反诈风险报告 — 对应升级方案 Section 3.2.1"""
    report_id: str
    generated_at: str
    user_info: dict                # 用户脱敏信息

    # 必填内容
    risk_items: List[RiskItem]     # 风险项明细
    fraud_type: str                # 诈骗类型定性
    fraud_confidence: float        # 诈骗置信度 (0-1)
    loss_probability: str          # 被骗概率评估（低/中/高/极高）

    # 建议与指引
    prevention_tips: List[str]     # 针对性防骗建议
    transfer_warning: str          # 转账拦截提醒
    legal_guidance: str            # 报警维权指引
    persuasion_message: str = ""   # AI劝导话术

    # 附件信息
    raw_evidence: List[str] = field(default_factory=list)   # 原始证据
    analysis_steps: List[str] = field(default_factory=list)  # AI分析过程


@dataclass
class ChatRequest:
    """对话请求"""
    session_id: str
    user_id: str
    message: str
    stream: bool = False           # 是否流式输出


@dataclass
class ChatResponse:
    """对话响应"""
    session_id: str
    reply: str
    risk_level: Optional[RiskLevel] = None
    fraud_type: Optional[str] = None
    persuasion_message: Optional[str] = None
    role_detected: Optional[UserRole] = None
    from_knowledge_base: bool = False
    is_stream: bool = False