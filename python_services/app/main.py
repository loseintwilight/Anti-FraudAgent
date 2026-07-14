"""
FastAPI 应用入口
使用 uvicorn 启动 AI 辅助反诈微服务
"""

from __future__ import annotations

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import router

# 创建 FastAPI 实例
app = FastAPI(
    title="Anti-Fraud AI Service",
    description="AI 辅助反诈微服务 - 风险评分、诈骗分类、劝导话术、报告生成",
    version="1.0.0",
)

# CORS 配置，允许跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册所有 API 路由
app.include_router(router, prefix="/api/v1")


@app.get("/", tags=["Root"])
async def root() -> dict:
    """根路径，返回服务基本信息"""
    return {
        "service": "Anti-Fraud AI Service",
        "version": "1.0.0",
        "docs": "/docs",
    }


def start() -> None:
    """启动 uvicorn 服务器"""
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8501,
        reload=True,
        log_level="info",
    )


if __name__ == "__main__":
    start()
