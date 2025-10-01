#!/usr/bin/env python3
"""
数据库初始化和管理脚本
用于创建和管理PostgreSQL中的世界观数据表
"""
import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import argparse
import logging

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self):
        self.connection_string = settings.DATABASE_URL
        
    def get_connection(self):
        """获取数据库连接"""
        return psycopg2.connect(self.connection_string)
    
    def get_connection_without_db(self):
        """获取不指定数据库的连接（用于创建数据库）"""
        # 解析连接字符串
        import urllib.parse
        parsed = urllib.parse.urlparse(self.connection_string)
        
        # 移除数据库名
        base_connection = f"postgresql://{parsed.username}:{parsed.password}@{parsed.hostname}:{parsed.port}/postgres"
        
        return psycopg2.connect(base_connection)
    
    def create_database(self):
        """创建数据库"""
        try:
            # 连接到默认的postgres数据库
            with self.get_connection_without_db() as conn:
                conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
                with conn.cursor() as cursor:
                    # 解析数据库名
                    import urllib.parse
                    parsed = urllib.parse.urlparse(self.connection_string)
                    db_name = parsed.path[1:]  # 移除开头的 '/'
                    
                    # 检查数据库是否存在
                    cursor.execute("""
                        SELECT 1 FROM pg_database WHERE datname = %s
                    """, (db_name,))
                    
                    if cursor.fetchone():
                        logger.info(f"数据库 '{db_name}' 已存在")
                        return True
                    
                    # 创建数据库
                    cursor.execute(f'CREATE DATABASE "{db_name}"')
                    logger.info(f"成功创建数据库: {db_name}")
                    return True
                    
        except Exception as e:
            logger.error(f"创建数据库失败: {e}")
            return False
    
    def init_tables(self):
        """初始化表结构"""
        try:
            # 读取SQL文件
            sql_file = os.path.join(os.path.dirname(__file__), "init_worldview_tables.sql")
            
            if not os.path.exists(sql_file):
                logger.error(f"SQL文件不存在: {sql_file}")
                return False
            
            with open(sql_file, 'r', encoding='utf-8') as f:
                sql_content = f.read()
            
            # 执行SQL
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(sql_content)
                    conn.commit()
                    
            logger.info("成功初始化数据库表结构")
            return True
            
        except Exception as e:
            logger.error(f"初始化表结构失败: {e}")
            return False
    
    def check_tables(self):
        """检查表是否存在"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT table_name 
                        FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name IN ('worldviews', 'power_systems', 'geographies', 'societies', 'history_cultures')
                        ORDER BY table_name
                    """)
                    
                    tables = [row[0] for row in cursor.fetchall()]
                    
                    logger.info(f"已存在的表: {tables}")
                    
                    expected_tables = ['worldviews', 'power_systems', 'geographies', 'societies', 'history_cultures']
                    missing_tables = set(expected_tables) - set(tables)
                    
                    if missing_tables:
                        logger.warning(f"缺失的表: {missing_tables}")
                        return False
                    
                    return True
                    
        except Exception as e:
            logger.error(f"检查表结构失败: {e}")
            return False
    
    def drop_tables(self):
        """删除所有表（谨慎使用）"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    # 按依赖关系顺序删除表
                    tables = [
                        'worldview_metadata',
                        'history_cultures', 
                        'societies',
                        'geographies',
                        'power_systems',
                        'worldviews'
                    ]
                    
                    for table in tables:
                        cursor.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
                        logger.info(f"删除表: {table}")
                    
                    conn.commit()
                    logger.info("成功删除所有表")
                    return True
                    
        except Exception as e:
            logger.error(f"删除表失败: {e}")
            return False
    
    def test_connection(self):
        """测试数据库连接"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT version()")
                    version = cursor.fetchone()[0]
                    logger.info(f"数据库连接成功: {version}")
                    return True
                    
        except Exception as e:
            logger.error(f"数据库连接失败: {e}")
            return False
    
    def get_stats(self):
        """获取数据库统计信息"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    # 获取表统计
                    cursor.execute("""
                        SELECT 
                            schemaname,
                            tablename,
                            n_tup_ins as inserts,
                            n_tup_upd as updates,
                            n_tup_del as deletes,
                            n_live_tup as live_tuples
                        FROM pg_stat_user_tables 
                        WHERE schemaname = 'public'
                        ORDER BY tablename
                    """)
                    
                    stats = cursor.fetchall()
                    
                    logger.info("数据库统计信息:")
                    for stat in stats:
                        logger.info(f"  表 {stat[1]}: 插入={stat[2]}, 更新={stat[3]}, 删除={stat[4]}, 当前行数={stat[5]}")
                    
                    return True
                    
        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="数据库管理工具")
    parser.add_argument("action", choices=[
        "create_db", "init_tables", "check_tables", "drop_tables", 
        "test_connection", "get_stats", "full_init"
    ], help="要执行的操作")
    
    args = parser.parse_args()
    
    db_manager = DatabaseManager()
    
    if args.action == "create_db":
        success = db_manager.create_database()
        sys.exit(0 if success else 1)
        
    elif args.action == "init_tables":
        success = db_manager.init_tables()
        sys.exit(0 if success else 1)
        
    elif args.action == "check_tables":
        success = db_manager.check_tables()
        sys.exit(0 if success else 1)
        
    elif args.action == "drop_tables":
        confirm = input("确定要删除所有表吗？这将删除所有数据！(yes/no): ")
        if confirm.lower() == 'yes':
            success = db_manager.drop_tables()
            sys.exit(0 if success else 1)
        else:
            logger.info("操作已取消")
            sys.exit(0)
        
    elif args.action == "test_connection":
        success = db_manager.test_connection()
        sys.exit(0 if success else 1)
        
    elif args.action == "get_stats":
        success = db_manager.get_stats()
        sys.exit(0 if success else 1)
        
    elif args.action == "full_init":
        logger.info("开始完整初始化...")
        
        # 1. 测试连接
        if not db_manager.test_connection():
            logger.error("数据库连接失败，请检查配置")
            sys.exit(1)
        
        # 2. 创建数据库
        if not db_manager.create_database():
            logger.error("创建数据库失败")
            sys.exit(1)
        
        # 3. 初始化表结构
        if not db_manager.init_tables():
            logger.error("初始化表结构失败")
            sys.exit(1)
        
        # 4. 检查表结构
        if not db_manager.check_tables():
            logger.error("表结构检查失败")
            sys.exit(1)
        
        logger.info("完整初始化成功！")
        sys.exit(0)


if __name__ == "__main__":
    main()
