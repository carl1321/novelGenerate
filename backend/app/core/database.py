"""
数据库连接和初始化
"""
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from neo4j import GraphDatabase
import redis
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
import asyncio

from app.core.config import settings

# PostgreSQL数据库配置
engine = create_async_engine(
    settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_recycle=300
)

SessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()

# Neo4j图数据库配置
neo4j_driver = GraphDatabase.driver(
    settings.NEO4J_URI,
    auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
)

# Redis缓存配置
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """获取数据库会话"""
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


def get_neo4j_session():
    """获取Neo4j会话"""
    return neo4j_driver.session()


def get_redis():
    """获取Redis客户端"""
    return redis_client


async def init_database():
    """初始化数据库"""
    # 创建所有表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # 初始化Neo4j约束和索引
    with get_neo4j_session() as session:
        # 创建节点约束
        constraints = [
            "CREATE CONSTRAINT character_id IF NOT EXISTS FOR (c:Character) REQUIRE c.id IS UNIQUE",
            "CREATE CONSTRAINT location_id IF NOT EXISTS FOR (l:Location) REQUIRE l.id IS UNIQUE",
            "CREATE CONSTRAINT organization_id IF NOT EXISTS FOR (o:Organization) REQUIRE o.id IS UNIQUE",
            "CREATE CONSTRAINT artifact_id IF NOT EXISTS FOR (a:Artifact) REQUIRE a.id IS UNIQUE",
            "CREATE CONSTRAINT technique_id IF NOT EXISTS FOR (t:Technique) REQUIRE t.id IS UNIQUE",
        ]
        
        for constraint in constraints:
            try:
                session.run(constraint)
            except Exception as e:
                print(f"Constraint creation warning: {e}")
        
        # 创建索引
        indexes = [
            "CREATE INDEX character_name IF NOT EXISTS FOR (c:Character) ON (c.name)",
            "CREATE INDEX location_name IF NOT EXISTS FOR (l:Location) ON (l.name)",
            "CREATE INDEX organization_name IF NOT EXISTS FOR (o:Organization) ON (o.name)",
        ]
        
        for index in indexes:
            try:
                session.run(index)
            except Exception as e:
                print(f"Index creation warning: {e}")


async def close_database():
    """关闭数据库连接"""
    await engine.dispose()
    neo4j_driver.close()
    redis_client.close()
