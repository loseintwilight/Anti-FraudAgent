"""
Pydantic 请求/响应模型定义
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ===================== 风险评分相关模型 =====================

class UserBehavior(BaseModel):
    """用户行为数据"""
    age: int = Field(..., ge=0, le=150, description="用户年龄")
    gender: str = Field(default="unknown", description="性别：male/female/unknown")
    occupation: str = Field(default="unknown", description="职业：student/elderly/worker/accountant/unknown")
    education: str = Field(default="unknown", description="教育程度")
    province: str = Field(default="unknown", description="所在省份")
    city: str = Field(default="unknown", description="所在城市")

    # 通话与短信行为
    call_duration_minutes: float = Field(default=0.0, description="近期通话总时长（分钟）")
    call_count_outgoing: int = Field(default=0, description="去电次数")
    call_count_incoming: int = Field(default=0, description="来电次数")
    unknown_call_ratio: float = Field(default=0.0, ge=0.0, le=1.0, description="陌生号码通话比例")
    sms_count_received: int = Field(default=0, description="收到的短信数量")
    sms_count_sent: int = Field(default=0, description="发送的短信数量")
    sms_with_link_ratio: float = Field(default=0.0, ge=0.0, le=1.0, description="含链接短信比例")

    # 转账与交易行为
    recent_transaction_amount: float = Field(default=0.0, description="近期单笔最大转账金额（元）")
    total_transaction_amount_7d: float = Field(default=0.0, description="近7天总转账金额（元）")
    transaction_count_7d: int = Field(default=0, description="近7天转账次数")
    transaction_to_new_accounts: int = Field(default=0, description="向新账户转账次数")
    night_transaction_count: int = Field(default=0, description="夜间（0-6点）交易次数")

    # 应用使用行为
    app_usage_minutes: float = Field(default=0.0, description="日均应用使用时长（分钟）")
    installed_apps_count: int = Field(default=0, description="已安装应用数量")
    recently_installed_apps: int = Field(default=0, description="近7天新安装应用数量")
    financial_app_count: int = Field(default=0, description="金融类应用数量")

    # 网络行为
    visited_suspicious_sites: int = Field(default=0, description="访问可疑站点次数")
    clicked_unknown_links: int = Field(default=0, description="点击不明链接次数")
    vpn_or_proxy_used: bool = Field(default=False, description="是否使用VPN/代理")
    public_wifi_connected: bool = Field(default=False, description="是否连接公共WiFi")

    # 其他
    account_age_days: int = Field(default=0, description="账户注册天数")
    has_verified_realname: bool = Field(default=False, description="是否实名认证")
    device_rooted: bool = Field(default=False, description="设备是否已Root/越狱")
    reported_count: int = Field(default=0, description="被举报次数")
    fraud_hotline_called: bool = Field(default=False, description="是否拨打过反诈热线")


class RiskRequest(BaseModel):
    """风险评分请求"""
    user_id: str = Field(..., description="用户ID")
    behavior: UserBehavior = Field(..., description="用户行为数据")


class RiskSource(BaseModel):
    """风险来源项"""
    dimension: str = Field(..., description="风险维度名称")
    score: float = Field(..., description="该维度得分（0-100）")
    weight: float = Field(..., description="该维度权重")
    detail: str = Field(default="", description="详细描述")


class RiskResponse(BaseModel):
    """风险评分响应"""
    user_id: str = Field(..., description="用户ID")
    risk_level: str = Field(..., description="风险等级：low/mid/high/critical")
    risk_score: float = Field(..., description="综合风险评分（0-100）")
    risk_sources: List[RiskSource] = Field(default_factory=list, description="风险来源明细")
    profile_summary: str = Field(default="", description="用户画像摘要")
    timestamp: str = Field(..., description="评估时间戳")


# ===================== 报告生成相关模型 =====================

class ReportRequest(BaseModel):
    """报告生成请求"""
    user_id: str = Field(..., description="用户ID")
    risk_level: str = Field(..., description="风险等级")
    risk_score: float = Field(..., description="风险评分")
    profile_summary: str = Field(default="", description="用户画像摘要")
    risk_sources: List[Dict[str, Any]] = Field(default_factory=list, description="风险来源")
    fraud_type: Optional[str] = Field(default=None, description="诈骗类型")
    persuasion_text: Optional[str] = Field(default=None, description="劝阻话术")
    output_format: str = Field(default="png", description="输出格式：png/jpg")


class ReportResponse(BaseModel):
    """报告生成响应"""
    user_id: str = Field(..., description="用户ID")
    image_base64: str = Field(..., description="Base64 编码的图片")
    format: str = Field(default="png", description="图片格式")
    message: str = Field(default="success", description="状态信息")


# ===================== 诈骗分类相关模型 =====================

class FraudClassifyRequest(BaseModel):
    """诈骗分类请求"""
    text: str = Field(..., description="待分类的文本内容（聊天记录、短信等）")
    user_age: Optional[int] = Field(default=None, description="用户年龄（可选，辅助判断）")


class FraudClassifyResponse(BaseModel):
    """诈骗分类响应"""
    fraud_type: str = Field(..., description="诈骗类型：刷单返利/虚假投资/冒充公检法/杀猪盘/冒充客服/虚假贷款/未知")
    confidence: float = Field(..., ge=0.0, le=1.0, description="置信度")
    matched_keywords: List[str] = Field(default_factory=list, description="匹配到的关键词")
    suggestion: str = Field(default="", description="建议")


class PersuasionRequest(BaseModel):
    """劝导话术请求"""
    fraud_type: str = Field(..., description="诈骗类型")
    age_group: str = Field(default="middle", description="年龄组：young/middle/elderly")
    user_name: str = Field(default="", description="用户称呼")


class PersuasionResponse(BaseModel):
    """劝导话术响应"""
    text: str = Field(..., description="劝导话术文本")
    fraud_type: str = Field(..., description="对应的诈骗类型")
    age_group: str = Field(..., description="对应的年龄组")


# ===================== 健康检查 =====================

class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str = Field(default="ok", description="服务状态")
    version: str = Field(default="1.0.0", description="服务版本")
