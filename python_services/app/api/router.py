"""
API 路由注册
挂载所有 API 端点，包括风险评分、AI 对话、视觉分析、RAG、诈骗分类等
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict, AsyncGenerator

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.api.schemas import (
    ChatReportRequest,
    ChatReportResponse,
    ChatRequest,
    ChatResponse,
    FraudClassifyRequest,
    FraudClassifyResponse,
    HealthResponse,
    LLMStatsResponse,
    PersuasionRequest,
    PersuasionResponse,
    RAGSearchRequest,
    RAGSearchResponse,
    RAGSearchResult,
    ReportItem,
    ReportRequest,
    ReportResponse,
    RiskRequest,
    RiskResponse,
    VisionRequest,
    VisionResponse,
)
from app.nlp.fraud_classifier import FraudClassifier
from app.nlp.persuasion import PersuasionGenerator
from app.report.image_generator import ImageReportGenerator
from app.risk_engine.profile import UserProfile
from app.risk_engine.scorer import RiskScorer

logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter()

# 懒加载单例
_profile_builder: UserProfile | None = None
_scorer: RiskScorer | None = None
_classifier: FraudClassifier | None = None
_persuasion_gen: PersuasionGenerator | None = None
_report_gen: ImageReportGenerator | None = None
_chat_agent: Any = None
_rag_agent: Any = None
_vision_analyzer: Any = None


def _get_profile_builder() -> UserProfile:
    global _profile_builder
    if _profile_builder is None:
        _profile_builder = UserProfile()
    return _profile_builder


def _get_scorer() -> RiskScorer:
    global _scorer
    if _scorer is None:
        _scorer = RiskScorer()
    return _scorer


def _get_classifier() -> FraudClassifier:
    global _classifier
    if _classifier is None:
        _classifier = FraudClassifier()
    return _classifier


def _get_persuasion_gen() -> PersuasionGenerator:
    global _persuasion_gen
    if _persuasion_gen is None:
        _persuasion_gen = PersuasionGenerator()
    return _persuasion_gen


def _get_report_gen() -> ImageReportGenerator:
    global _report_gen
    if _report_gen is None:
        _report_gen = ImageReportGenerator()
    return _report_gen


def _get_chat_agent():
    """获取或创建 ChatAgent 实例"""
    global _chat_agent
    if _chat_agent is None:
        from app.llm.chat_agent import ChatAgent
        _chat_agent = ChatAgent()
    return _chat_agent


def _get_rag_agent():
    """获取或创建 RAGAgent 实例"""
    global _rag_agent
    if _rag_agent is None:
        from app.llm.rag_agent import RAGAgent
        _rag_agent = RAGAgent()
    return _rag_agent


def _get_vision_analyzer():
    """获取或创建 VisionAnalyzer 实例"""
    global _vision_analyzer
    if _vision_analyzer is None:
        from app.llm.vision import VisionAnalyzer
        _vision_analyzer = VisionAnalyzer()
    return _vision_analyzer


# ===================== 健康检查 =====================

@router.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check() -> HealthResponse:
    """健康检查端点"""
    return HealthResponse(status="ok", version="1.0.0")


# ===================== 风险评分 =====================

@router.post("/risk/score", response_model=RiskResponse, tags=["Risk Engine"])
async def compute_risk_score(request: RiskRequest) -> RiskResponse:
    """
    计算用户风险评分
    - 根据用户行为数据构建画像
    - 执行多维度加权评分
    - 返回四级风险等级及风险来源明细
    """
    try:
        profile_builder = _get_profile_builder()
        scorer = _get_scorer()

        profile = profile_builder.build(request.behavior, request.user_id)
        score_result = scorer.evaluate(profile)

        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        return RiskResponse(
            user_id=request.user_id,
            risk_level=score_result["risk_level"],
            risk_score=score_result["total_score"],
            risk_sources=score_result["sources"],
            profile_summary=score_result["profile_summary"],
            timestamp=timestamp,
        )
    except Exception as e:
        logger.exception("风险评分计算失败")
        raise HTTPException(status_code=500, detail=f"风险评分计算失败: {str(e)}")


# ===================== 诈骗分类 =====================

@router.post("/nlp/classify", response_model=FraudClassifyResponse, tags=["NLP"])
async def classify_fraud(request: FraudClassifyRequest) -> FraudClassifyResponse:
    """诈骗类型分类"""
    try:
        classifier = _get_classifier()
        result = classifier.classify(request.text, age=request.user_age)
        return FraudClassifyResponse(**result)
    except Exception as e:
        logger.exception("诈骗分类失败")
        raise HTTPException(status_code=500, detail=f"诈骗分类失败: {str(e)}")


# ===================== 劝导话术生成 =====================

@router.post("/nlp/persuade", response_model=PersuasionResponse, tags=["NLP"])
async def generate_persuasion(request: PersuasionRequest) -> PersuasionResponse:
    """生成劝导话术"""
    try:
        gen = _get_persuasion_gen()
        text = gen.generate(
            fraud_type=request.fraud_type,
            age_group=request.age_group,
            user_name=request.user_name,
        )
        return PersuasionResponse(
            text=text,
            fraud_type=request.fraud_type,
            age_group=request.age_group,
        )
    except Exception as e:
        logger.exception("劝导话术生成失败")
        raise HTTPException(status_code=500, detail=f"劝导话术生成失败: {str(e)}")


# ===================== 报告生成 =====================

@router.post("/report/generate", response_model=ReportResponse, tags=["Report"])
async def generate_report(request: ReportRequest) -> ReportResponse:
    """生成风险报告图片"""
    try:
        gen = _get_report_gen()
        result = gen.generate(
            user_id=request.user_id,
            risk_level=request.risk_level,
            risk_score=request.risk_score,
            profile_summary=request.profile_summary,
            risk_sources=request.risk_sources,
            fraud_type=request.fraud_type,
            persuasion_text=request.persuasion_text,
            output_format=request.output_format,
        )
        return ReportResponse(
            user_id=request.user_id,
            image_base64=result["image_base64"],
            format=result["format"],
            message="success",
        )
    except Exception as e:
        logger.exception("报告生成失败")
        raise HTTPException(status_code=500, detail=f"报告生成失败: {str(e)}")


# ===================== 爬虫触发 =====================

@router.post("/crawler/trigger", tags=["Crawler"])
async def trigger_crawl(source: str = "all") -> Dict[str, Any]:
    """手动触发爬虫任务"""
    try:
        from app.crawler.engine import CrawlerEngine

        engine = CrawlerEngine()
        results = engine.crawl(source=source)
        return {"status": "completed", "results": results}
    except Exception as e:
        logger.exception("爬虫触发失败")
        raise HTTPException(status_code=500, detail=f"爬虫触发失败: {str(e)}")


# ===================== AI 对话（基于 LangChain）=====================

@router.post("/ai/chat", response_model=ChatResponse, tags=["AI Chat"])
async def ai_chat(request: ChatRequest) -> ChatResponse:
    """
    AI 智能对话
    - 基于 LangChain + DashScope 实现
    - 支持三种模式：闲聊、咨询、反诈预警
    - 自动保持对话历史
    """
    try:
        agent = _get_chat_agent()
        response = agent.chat(
            message=request.message,
            conversation_id=request.conversation_id,
        )
        return ChatResponse(
            success=True,
            response=response,
            conversation_id=request.conversation_id,
        )
    except Exception as e:
        logger.exception("AI 对话失败")
        raise HTTPException(status_code=500, detail=f"AI 对话失败: {str(e)}")


@router.post("/ai/chat/stream", tags=["AI Chat"])
async def ai_chat_stream(request: ChatRequest):
    """
    AI 流式对话（SSE）
    - 基于 Server-Sent Events 实现流式输出
    """
    agent = _get_chat_agent()

    async def event_generator():
        async for chunk in agent.chat_stream(
            message=request.message,
            conversation_id=request.conversation_id,
        ):
            yield f"data: {chunk}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
    )


@router.post("/ai/chat/tools", response_model=ChatResponse, tags=["AI Chat"])
async def ai_chat_with_tools(request: ChatRequest) -> ChatResponse:
    """
    带工具调用的 AI 对话
    - 支持文件操作、PDF 生成、网页搜索、网页抓取等工具
    """
    try:
        agent = _get_chat_agent()
        response = agent.chat_with_tools(
            message=request.message,
            conversation_id=request.conversation_id,
        )
        return ChatResponse(
            success=True,
            response=response,
            conversation_id=request.conversation_id,
        )
    except Exception as e:
        logger.exception("AI 工具对话失败")
        raise HTTPException(status_code=500, detail=f"AI 工具对话失败: {str(e)}")


@router.post("/ai/chat/report", response_model=ChatReportResponse, tags=["AI Chat"])
async def ai_chat_with_report(request: ChatReportRequest) -> ChatReportResponse:
    """
    对话并生成反诈报告
    - 返回 AI 回复和结构化的反诈报告
    """
    try:
        agent = _get_chat_agent()
        result = agent.chat_with_report(
            message=request.message,
            conversation_id=request.conversation_id,
            user_name=request.user_name,
        )
        return ChatReportResponse(
            success=True,
            response=result["response"],
            report=ReportItem(
                title=result["report"]["title"],
                suggestions=result["report"]["suggestions"],
            ),
        )
    except Exception as e:
        logger.exception("对话报告生成失败")
        raise HTTPException(status_code=500, detail=f"对话报告生成失败: {str(e)}")


@router.post("/ai/clear", tags=["AI Chat"])
async def ai_clear_memory(conversation_id: str = "default") -> Dict[str, Any]:
    """清除指定对话的历史记录"""
    try:
        agent = _get_chat_agent()
        agent.clear_memory(conversation_id)
        return {"success": True, "message": f"对话 {conversation_id} 历史已清除"}
    except Exception as e:
        logger.exception("清除对话历史失败")
        raise HTTPException(status_code=500, detail=f"清除对话历史失败: {str(e)}")


# ===================== 视觉分析（基于 LangChain）=====================

@router.post("/ai/vision/analyze", response_model=VisionResponse, tags=["AI Vision"])
async def analyze_image(request: VisionRequest) -> VisionResponse:
    """
    图片分析
    - 使用 qwen-vl-max 多模态模型分析图片
    - 支持 OCR 文字识别、场景描述、诈骗类型判断
    """
    try:
        analyzer = _get_vision_analyzer()
        result = analyzer.analyze_image(
            image_base64=request.image_base64,
            prompt=request.prompt,
        )
        return VisionResponse(**result)
    except Exception as e:
        logger.exception("图片分析失败")
        raise HTTPException(status_code=500, detail=f"图片分析失败: {str(e)}")


# ===================== RAG 检索（基于 LangChain）=====================

@router.post("/ai/rag/search", response_model=RAGSearchResponse, tags=["AI RAG"])
async def rag_search(request: RAGSearchRequest) -> RAGSearchResponse:
    """
    RAG 知识检索
    - 基于 LangChain + ChromaDB 向量检索
    - 返回与查询最相关的文档
    """
    try:
        agent = _get_rag_agent()
        results = agent.search(query=request.query, k=request.k)
        return RAGSearchResponse(
            success=True,
            results=[RAGSearchResult(**r) for r in results],
            total=len(results),
        )
    except Exception as e:
        logger.exception("RAG 检索失败")
        raise HTTPException(status_code=500, detail=f"RAG 检索失败: {str(e)}")


@router.post("/ai/rag/chat", response_model=ChatResponse, tags=["AI RAG"])
async def rag_chat(request: ChatRequest) -> ChatResponse:
    """
    基于 RAG 的智能对话
    - 结合知识检索和 LLM 生成回答
    - 适用于需要查阅反诈知识库的场景
    """
    try:
        agent = _get_rag_agent()
        response = agent.chat_with_rag(
            message=request.message,
            conversation_id=request.conversation_id,
        )
        return ChatResponse(
            success=True,
            response=response,
            conversation_id=request.conversation_id,
        )
    except Exception as e:
        logger.exception("RAG 对话失败")
        raise HTTPException(status_code=500, detail=f"RAG 对话失败: {str(e)}")


@router.get("/ai/rag/stats", tags=["AI RAG"])
async def rag_stats() -> Dict[str, Any]:
    """获取 RAG 向量存储统计信息"""
    try:
        agent = _get_rag_agent()
        return {"success": True, "data": agent.get_stats()}
    except Exception as e:
        logger.exception("获取 RAG 统计失败")
        raise HTTPException(status_code=500, detail=str(e))


# ===================== LLM 统计 =====================

@router.get("/ai/stats", response_model=LLMStatsResponse, tags=["AI System"])
async def llm_stats() -> LLMStatsResponse:
    """获取 LLM 模块统计信息"""
    try:
        from app.llm.tools import get_all_tools

        chat_agent = _get_chat_agent()
        rag_agent = _get_rag_agent()
        tools = [t.name for t in get_all_tools()]

        return LLMStatsResponse(
            success=True,
            chat_agent=chat_agent.get_stats(),
            rag_agent=rag_agent.get_stats(),
            tools=tools,
        )
    except Exception as e:
        logger.exception("获取 LLM 统计失败")
        raise HTTPException(status_code=500, detail=str(e))