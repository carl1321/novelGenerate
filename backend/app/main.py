"""
小说生成智能体框架 - 主应用入口
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
import uvicorn
import logging
import os

from app.core.config import settings
from app.api import world, character, plot_outline, logic, scoring, evolution
from app.core.database import init_database

# 配置日志
logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper()),
    format=os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化数据库
    logger.info("正在初始化数据库...")
    await init_database()
    logger.info("数据库初始化完成")
    logger.debug(f"LLM提供商: {settings.LLM_PROVIDER}")
    logger.debug(f"API密钥已配置: {'是' if settings.ALIBABA_QWEN_API_KEY else '否'}")
    yield
    # 关闭时清理资源
    logger.info("应用正在关闭...")


# 创建FastAPI应用
app = FastAPI(
    title="小说生成智能体框架",
    description="基于AI的智能小说生成系统",
    version="1.0.0",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加安全中间件
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)

# 注册API路由
app.include_router(world.router, prefix="/api/v1/world", tags=["世界观"])
app.include_router(character.router, prefix="/api/v1/character", tags=["角色管理"])
app.include_router(plot_outline.router, prefix="/api/v1/plot", tags=["剧情生成"])
app.include_router(logic.router, prefix="/api/v1/logic", tags=["逻辑反思"])
app.include_router(scoring.router, prefix="/api/v1/scoring", tags=["评分系统"])
app.include_router(evolution.router, prefix="/api/v1/evolution", tags=["进化重写"])


@app.get("/")
async def root():
    """根路径健康检查"""
    return {
        "message": "小说生成智能体框架 API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import os
    log_level = os.getenv("LOG_LEVEL", "info").lower()
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level=log_level
    )
