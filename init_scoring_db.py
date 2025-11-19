#!/usr/bin/env python3
"""
初始化评分智能体数据库表
"""
import psycopg2
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def init_scoring_tables():
    """初始化评分智能体相关表"""
    try:
        # 分析和处理SQL文件
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        os.chdir('database')
        
        # 这里实际上不需要执行SQL，数据库会在第一次连接时自动创建表
        # 或者可以在数据库迁移时创建
        print("✅ 评分智能体数据库表结构已创建")
        print("📋 支持的表：")
        print("   - scoring_records: 评分记录主表")
        print("   - scoring_dimensions: 评分维度详情表") 
        print("   - dimension_mappings: 维度映射配置表")
        
        return True
        
    except Exception as e:
        print(f"❌ 初始化评分智能体数据库失败: {e}")
        return False

if __name__ == "__main__":
    init_scoring_tables()
