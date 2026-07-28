"""
AI 反诈智能体 — Python 辅助服务入口

启动方式：
    python main.py

或使用 uvicorn：
    uvicorn app.main:app --host 0.0.0.0 --port 8501 --reload
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .api.routes import router
from .config import settings
from .utils.logger import logger

# 创建 FastAPI 应用
app = FastAPI(
    title=settings.SERVICE_NAME,
    version=settings.SERVICE_VERSION,
    description="AI 反诈智能体辅助服务 — 提供对话、风险评估、劝导话术、报告生成等功能",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS 跨域配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(router)


@app.on_event("startup")
async def startup():
    """服务启动时的初始化"""
    settings.ensure_dirs()
    logger.info(f"{settings.SERVICE_NAME} v{settings.SERVICE_VERSION} 启动成功")
    logger.info(f"文档地址: http://localhost:{settings.SERVICE_PORT}/docs")


@app.on_event("shutdown")
async def shutdown():
    """服务关闭时的清理"""
    from .core.context import context_manager
    context_manager.persist_all()
    from .core.deepseek import deepseek_client
    await deepseek_client.close()
    logger.info("服务已关闭，所有会话已持久化")


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全局异常处理"""
    logger.error(f"全局异常: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "服务器内部错误，请稍后重试", "detail": str(exc)},
    )


def main():
    """启动入口"""
    uvicorn.run(
        "app.main:app",
        host=settings.SERVICE_HOST,
        port=settings.SERVICE_PORT,
        reload=settings.DEBUG,
        log_level="info",
    )


if __name__ == "__main__":
    main()