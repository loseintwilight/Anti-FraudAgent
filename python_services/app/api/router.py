"""
API 路由注册
挂载所有 API 端点，包括风险评分、报告生成、诈骗分类、劝导话术、爬虫触发、健康检查
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict

from fastapi import APIRouter, HTTPException

from app.api.schemas import (
    FraudClassifyRequest,
    FraudClassifyResponse,
    HealthResponse,
    PersuasionRequest,
    PersuasionResponse,
    ReportRequest,
    ReportResponse,
    RiskRequest,
    RiskResponse,
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


def _get_profile_builder() -> UserProfile:
    """获取或创建 UserProfile 实例"""
    global _profile_builder
    if _profile_builder is None:
        _profile_builder = UserProfile()
    return _profile_builder


def _get_scorer() -> RiskScorer:
    """获取或创建 RiskScorer 实例"""
    global _scorer
    if _scorer is None:
        _scorer = RiskScorer()
    return _scorer


def _get_classifier() -> FraudClassifier:
    """获取或创建 FraudClassifier 实例"""
    global _classifier
    if _classifier is None:
        _classifier = FraudClassifier()
    return _classifier


def _get_persuasion_gen() -> PersuasionGenerator:
    """获取或创建 PersuasionGenerator 实例"""
    global _persuasion_gen
    if _persuasion_gen is None:
        _persuasion_gen = PersuasionGenerator()
    return _persuasion_gen


def _get_report_gen() -> ImageReportGenerator:
    """获取或创建 ImageReportGenerator 实例"""
    global _report_gen
    if _report_gen is None:
        _report_gen = ImageReportGenerator()
    return _report_gen


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

        # 构建用户画像
        profile = profile_builder.build(request.behavior, request.user_id)

        # 计算风险评分
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
    """
    诈骗类型分类
    - 基于关键词匹配 + 规则判断
    - 返回诈骗类型、置信度、匹配关键词
    """
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
    """
    生成劝导话术
    - 根据诈骗类型和年龄组，生成口语化劝阻话术
    """
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
    """
    生成风险报告图片
    - 使用 Pillow 生成包含风险信息的图片报告
    - 返回 Base64 编码的图片数据
    """
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
    """
    手动触发爬虫任务
    - source: 爬取来源，可选 mps_gov / news / all，默认 all
    """
    try:
        from app.crawler.engine import CrawlerEngine

        engine = CrawlerEngine()
        results = engine.crawl(source=source)
        return {"status": "completed", "results": results}
    except Exception as e:
        logger.exception("爬虫触发失败")
        raise HTTPException(status_code=500, detail=f"爬虫触发失败: {str(e)}")
