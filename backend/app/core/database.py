"""
数据库连接和初始化
"""
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import redis
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
import asyncio

from app.core.config import settings

# PostgreSQL数据库配置
engine = create_async_engine(
    settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
    echo=False,  # 关闭SQL日志
    pool_pre_ping=True,
    pool_recycle=300
)

SessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()

# Redis缓存配置（可选）
redis_client = None
if hasattr(settings, 'REDIS_URL') and settings.REDIS_URL:
    try:
        redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    except Exception:
        redis_client = None


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """获取数据库会话"""
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


def get_redis():
    """获取Redis客户端（如果可用）"""
    return redis_client


async def init_database():
    """初始化数据库"""
    # 创建所有表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_database():
    """关闭数据库连接"""
    await engine.dispose()
    if redis_client:
        redis_client.close()
