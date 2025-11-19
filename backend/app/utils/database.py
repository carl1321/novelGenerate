"""
数据库连接工具模块
"""
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Dict, Any
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

def get_database_connection() -> Dict[str, Any]:
    """
    获取数据库连接配置
    
    Returns:
        数据库连接参数字典
    """
    # 从DATABASE_URL解析连接参数
    from urllib.parse import urlparse
    parsed_url = urlparse(settings.DATABASE_URL)
    
    return {
        'host': parsed_url.hostname or 'localhost',
        'port': parsed_url.port or 5432,
        'user': parsed_url.username or 'novel_user',
        'password': parsed_url.password or 'novel_password',
        'dbname': parsed_url.path.lstrip('/') or 'novel_generate'
    }

def get_database_url() -> str:
    """
    获取数据库连接URL
    
    Returns:
        数据库连接字符串
    """
    return settings.DATABASE_URL

def create_connection():
    """
    创建数据库连接
    
    Returns:
        psycopg2连接对象
    """
    try:
        return psycopg2.connect(
            settings.DATABASE_URL,
            cursor_factory=RealDictCursor
        )
    except Exception as e:
        logger.error(f"数据库连接失败: {e}")
        raise

def test_connection() -> bool:
    """
    测试数据库连接
    
    Returns:
        连接是否成功
    """
    try:
        conn = create_connection()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"数据库连接测试失败: {e}")
        return False
