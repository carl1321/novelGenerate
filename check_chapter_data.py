#!/usr/bin/env python3
"""
查询数据库中的章节数据，检查幕次值
"""
import os
import sys
import json

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 设置环境变量
os.environ.setdefault('DATABASE_URL', 'postgresql://postgres:password@localhost:5432/novel_generate')

try:
    from backend.app.core.chapter_engine.chapter_database import ChapterOutlineDatabase
    
    # 创建数据库实例
    chapter_db = ChapterOutlineDatabase()
    
    print("=== 查询章节大纲数据 ===")
    
    # 查询所有章节大纲
    chapters = chapter_db.get_all_chapter_outlines()
    
    if chapters:
        print(f"找到 {len(chapters)} 个章节大纲:")
        for chapter in chapters[:10]:  # 只显示前10个
            print(f"章节{chapter.chapter_number}: {chapter.title}")
            print(f"  幕次: {chapter.act_belonging}")
            print(f"  功能: {chapter.plot_function}")
            print(f"  状态: {chapter.status}")
            print("---")
    else:
        print("没有找到章节大纲数据")
    
    # 查询特定剧情大纲的章节
    print("\n=== 查询特定剧情大纲的章节 ===")
    
    # 先获取一个剧情大纲ID
    from backend.app.core.plot_engine.plot_database import PlotOutlineDatabase
    plot_db = PlotOutlineDatabase()
    plots = plot_db.get_all_plot_outlines()
    
    if plots:
        plot_id = plots[0].id
        print(f"使用剧情大纲ID: {plot_id}")
        
        chapters = chapter_db.get_chapter_outlines_by_plot(plot_id)
        if chapters:
            print(f"该剧情大纲下有 {len(chapters)} 个章节:")
            for chapter in chapters:
                print(f"章节{chapter.chapter_number}: {chapter.title}")
                print(f"  幕次: {chapter.act_belonging}")
                print(f"  功能: {chapter.plot_function}")
                print("---")
        else:
            print("该剧情大纲下没有章节")
    else:
        print("没有找到剧情大纲数据")
        
except ImportError as e:
    print(f"导入模块失败: {e}")
    print("请确保在正确的环境中运行此脚本")
except Exception as e:
    print(f"查询失败: {e}")
