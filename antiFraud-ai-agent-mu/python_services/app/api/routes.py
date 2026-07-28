"""
FastAPI 路由定义

接口列表：
- POST /api/v1/chat         对话接口（支持流式和非流式）
- POST /api/v1/risk/assess  风险评估接口
- POST /api/v1/persuasion   劝导话术生成接口
- POST /api/v1/report       风险报告生成接口
- GET  /api/v1/health       健康检查
"""

import json
import traceback
import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import JSONResponse, StreamingResponse, PlainTextResponse
from pydantic import BaseModel, Field

from ..core.context import context_manager
from ..core.retriever import rag_retriever
from ..engine.dialogue import dialogue_engine
from ..engine.identity import identity_engine
from ..engine.persuasion import persuasion_engine
from ..engine.risk import risk_assessor
from ..models.schemas import (
    ChatRequest,
    ChatResponse,
    FraudReport,
    RiskItem,
    RiskLevel,
    UserRole,
)
from ..report.generator import report_generator
from ..utils.logger import logger

router = APIRouter(prefix="/api/v1")


def _get_loss_probability(risk_level: RiskLevel, confidence: float) -> str:
    """根据风险等级和置信度估算被骗概率"""
    if risk_level == RiskLevel.EXTREME:
        return "极高"
    elif risk_level == RiskLevel.HIGH:
        return "高"
    elif risk_level == RiskLevel.MEDIUM:
        return "中"
    else:
        return "低"


# ==================== 请求/响应模型 ====================

class ChatRequestModel(BaseModel):
    """对话请求模型"""
    session_id: str = Field(default="", description="会话ID，为空时自动创建")
    user_id: str = Field(default="anonymous", description="用户ID")
    message: str = Field(..., min_length=1, max_length=2000, description="用户输入")
    stream: bool = Field(default=False, description="是否流式输出")


class ChatResponseModel(BaseModel):
    """对话响应模型"""
    session_id: str
    reply: str
    risk_level: Optional[str] = None
    fraud_type: Optional[str] = None
    persuasion_message: Optional[str] = None
    role_detected: Optional[str] = None
    from_knowledge_base: bool = False


class AssessRequestModel(BaseModel):
    """风险评估请求模型"""
    text: str = Field(..., min_length=1, max_length=2000, description="待评估文本")
    user_role: str = Field(default="unknown", description="用户角色")


class AssessResponseModel(BaseModel):
    """风险评估响应模型"""
    risk_level: str
    fraud_type: str
    confidence: float
    risk_items: list


class PersuasionRequestModel(BaseModel):
    """劝导话术请求模型"""
    fraud_type: str = Field(..., description="诈骗类型")
    risk_level: str = Field(..., description="风险等级 (HIGH/EXTREME)")
    user_role: str = Field(default="youth", description="用户角色")


class PersuasionResponseModel(BaseModel):
    """劝导话术响应模型"""
    success: bool
    message: Optional[str] = None
    fraud_type: str
    risk_level: str
    user_role: str


class ReportRequestModel(BaseModel):
    """报告生成请求模型"""
    text: str = Field(..., min_length=1, max_length=5000, description="用户输入的原始文本")
    user_id: str = Field(default="anonymous", description="用户ID")
    user_role: str = Field(default="unknown", description="用户角色")


class ReportResponseModel(BaseModel):
    """报告生成响应模型"""
    report_id: str
    report: dict
    generated_at: str


# ==================== API 路由 ====================

@router.post("/chat", summary="对话接口")
async def chat(request: Request, body: ChatRequestModel):
    """
    对话接口 — 支持流式和非流式两种模式

    流程：
    1. 自动创建或恢复会话
    2. 识别用户身份
    3. 判断是否反诈相关 → 知识库优先检索
    4. 风险评估 → 劝导话术生成
    5. 返回回答
    """
    # 自动创建 session_id
    session_id = body.session_id or context_manager.create_session_id()
    if not body.session_id:
        body.session_id = session_id

    logger.info(
        f"对话请求: session_id={body.session_id}, "
        f"user_id={body.user_id}, stream={body.stream}"
    )

    chat_request = ChatRequest(
        session_id=body.session_id,
        user_id=body.user_id,
        message=body.message,
        stream=body.stream,
    )

    try:
        if body.stream:
            # 流式输出
            async def generate():
                yield "data: " + json.dumps({"session_id": body.session_id}) + "\n\n"
                try:
                    async for chunk in dialogue_engine.process(chat_request):
                        yield "data: " + json.dumps({"content": chunk}) + "\n\n"
                except Exception as e:
                    error_msg = str(e)
                    logger.error(f"流式对话处理失败: {error_msg}")
                    yield "data: " + json.dumps({"error": error_msg}) + "\n\n"
                yield "data: [DONE]\n\n"

            return StreamingResponse(
                generate(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Accel-Buffering": "no",
                },
            )
        else:
            # 非流式输出
            response = await dialogue_engine.process(chat_request)
            return ChatResponseModel(
                session_id=response.session_id,
                reply=response.reply,
                risk_level=response.risk_level.value if response.risk_level else None,
                fraud_type=response.fraud_type,
                persuasion_message=response.persuasion_message,
                role_detected=response.role_detected.value if response.role_detected else None,
                from_knowledge_base=response.from_knowledge_base,
            )
    except RuntimeError as e:
        error_msg = str(e)
        logger.error(f"对话请求处理失败: {error_msg}")
        # 检查是否是 API Key 相关的错误
        if "API Key" in error_msg or "api_key" in error_msg.lower() or "余额" in error_msg:
            raise HTTPException(status_code=401, detail={"error": error_msg})
        raise HTTPException(status_code=500, detail={"error": error_msg})
    except Exception as e:
        error_msg = str(e)
        logger.error(f"对话请求未知错误: {error_msg}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail={"error": f"服务器内部错误: {error_msg}"})


@router.post("/risk/assess", summary="风险评估接口")
async def assess_risk(body: AssessRequestModel):
    """
    对用户输入进行风险评估

    返回风险等级、诈骗类型和风险项明细
    """
    risk_level, fraud_type, confidence, risk_items = risk_assessor.assess(
        body.text, body.user_role
    )

    return AssessResponseModel(
        risk_level=risk_level.value,
        fraud_type=fraud_type,
        confidence=confidence,
        risk_items=[
            {
                "source": item.source,
                "risk_type": item.risk_type,
                "risk_score": item.risk_score,
                "explanation": item.explanation,
            }
            for item in risk_items
        ],
    )


@router.post("/persuasion", summary="劝导话术生成接口")
async def generate_persuasion(body: PersuasionRequestModel):
    """
    根据诈骗类型、风险等级和用户角色生成劝导话术
    """
    message = persuasion_engine.generate(
        fraud_type=body.fraud_type,
        risk_level=body.risk_level,
        user_role=body.user_role,
    )

    return PersuasionResponseModel(
        success=message is not None,
        message=message,
        fraud_type=body.fraud_type,
        risk_level=body.risk_level,
        user_role=body.user_role,
    )


@router.post("/report", summary="风险报告生成接口")
async def generate_report(body: ReportRequestModel):
    """
    生成反诈风险诊断报告

    报告包含：
    - 风险项明细
    - 诈骗类型定性
    - 被骗概率评估
    - 防骗建议
    - 转账拦截提醒
    - 报警维权指引
    - AI劝导话术
    """
    report_id = f"report-{uuid.uuid4().hex[:12]}"

    # 风险评估
    risk_level, fraud_type, confidence, risk_items = risk_assessor.assess(
        body.text, body.user_role
    )

    # 劝导话术
    persuasion_message = persuasion_engine.generate(
        fraud_type=fraud_type,
        risk_level=risk_level.value,
        user_role=body.user_role,
    )

    # 防范建议
    tips = risk_assessor.get_prevention_tips(fraud_type)
    transfer_warning = risk_assessor.get_transfer_warning(risk_level)

    # 构建报告
    report = FraudReport(
        report_id=report_id,
        generated_at=datetime.now().isoformat(),
        user_info={
            "user_id": body.user_id,
            "role": body.user_role,
        },
        risk_items=risk_items,
        fraud_type=fraud_type,
        fraud_confidence=confidence,
        loss_probability=_get_loss_probability(risk_level, confidence),
        prevention_tips=tips,
        transfer_warning=transfer_warning,
        legal_guidance=(
            "1. 立即拨打110报警，联系银行申请紧急止付\n"
            "2. 保存聊天记录、转账凭证等所有证据\n"
            "3. 前往就近派出所做笔录，正式立案\n"
            "4. 修改相关账户密码，开启二次验证\n"
            "5. 如有疑问可拨打全国反诈专线96110咨询"
        ),
        persuasion_message=persuasion_message or "",
        analysis_steps=[
            "1. 反诈关键词匹配 — 识别诈骗类型",
            "2. 高风险行为检测 — 评估损失风险",
            "3. 紧急程度判定 — 评估紧急程度",
            "4. 资金风险分析 — 检测涉及金额",
            "5. 综合评定风险等级",
        ],
    )

    return ReportResponseModel(
        report_id=report_id,
        report={
            "report_id": report.report_id,
            "generated_at": report.generated_at,
            "user_info": report.user_info,
            "risk_items": [
                {
                    "source": item.source,
                    "risk_type": item.risk_type,
                    "risk_score": item.risk_score,
                    "explanation": item.explanation,
                }
                for item in report.risk_items
            ],
            "fraud_type": report.fraud_type,
            "fraud_confidence": report.fraud_confidence,
            "loss_probability": report.loss_probability,
            "prevention_tips": report.prevention_tips,
            "transfer_warning": report.transfer_warning,
            "legal_guidance": report.legal_guidance,
            "persuasion_message": report.persuasion_message,
            "analysis_steps": report.analysis_steps,
        },
        generated_at=report.generated_at,
    )


@router.get("/health", summary="健康检查")
async def health_check():
    """服务健康检查"""
    return {
        "status": "ok",
        "service": "AI反诈智能体-Python辅助服务",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
    }


@router.get("/fraud-types", summary="获取支持的诈骗类型列表")
async def get_fraud_types():
    """获取所有支持的诈骗类型"""
    return {
        "fraud_types": persuasion_engine.get_supported_types(),
        "count": len(persuasion_engine.get_supported_types()),
    }


@router.post("/session/clear", summary="清除会话历史")
async def clear_session(session_id: str = Query(..., description="会话ID")):
    """清除指定会话的上下文"""
    context_manager.remove(session_id)
    return {"success": True, "message": f"会话 {session_id} 已清除"}