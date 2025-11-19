#!/usr/bin/env python3
"""
清理异常的章节编号
删除测试章节和编号异常的章节，重新分配连续编号
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.core.chapter_engine.chapter_database import ChapterOutlineDatabase


def clean_abnormal_chapter_numbers():
    """清理异常的章节编号"""
    print("=" * 70)
    print("🧹 清理异常的章节编号")
    print("=" * 70)
    
    # 初始化数据库
    chapter_db = ChapterOutlineDatabase()
    
    # 获取所有章节大纲
    chapters = chapter_db.get_chapters_by_plot('plot_5c4cc022')
    print(f"📊 获取到 {len(chapters)} 个章节大纲")
    
    # 找出异常的章节编号（大于20的）
    abnormal_chapters = []
    normal_chapters = []
    
    for chapter in chapters:
        if chapter.chapter_number > 20:
            abnormal_chapters.append(chapter)
        else:
            normal_chapters.append(chapter)
    
    print(f"\\n📋 章节分类:")
    print(f"  正常章节 (1-20): {len(normal_chapters)} 个")
    print(f"  异常章节 (>20): {len(abnormal_chapters)} 个")
    
    if abnormal_chapters:
        print(f"\\n🔍 异常章节详情:")
        print("-" * 50)
        for chapter in abnormal_chapters:
            print(f"  第{chapter.chapter_number}章: {chapter.title} (ID: {chapter.id})")
        
        print(f"\\n❓ 是否要删除这些异常章节? (y/n): ", end="")
        choice = input().lower()
        
        if choice == 'y':
            print(f"\\n🗑️ 开始删除异常章节:")
            print("-" * 50)
            
            deleted_count = 0
            for chapter in abnormal_chapters:
                try:
                    success = chapter_db.delete_chapter_outline(chapter.id)
                    if success:
                        print(f"  ✅ 删除第{chapter.chapter_number}章: {chapter.title}")
                        deleted_count += 1
                    else:
                        print(f"  ❌ 删除失败第{chapter.chapter_number}章: {chapter.title}")
                except Exception as e:
                    print(f"  ❌ 删除第{chapter.chapter_number}章失败: {e}")
            
            print(f"\\n🎉 删除完成! 共删除了 {deleted_count} 个异常章节")
            
            # 验证删除结果
            print(f"\\n🔍 验证删除结果:")
            print("-" * 50)
            
            remaining_chapters = chapter_db.get_chapters_by_plot('plot_5c4cc022')
            remaining_numbers = [c.chapter_number for c in remaining_chapters if c.chapter_number]
            
            print(f"  剩余章节数量: {len(remaining_chapters)}")
            print(f"  剩余章节编号: {sorted(remaining_numbers)}")
            
            # 测试下一个章节编号
            next_number = chapter_db.get_next_chapter_number('plot_5c4cc022')
            print(f"  下一个章节编号: {next_number}")
            
        else:
            print("\\n⏭️ 跳过删除操作")
    else:
        print("\\n✅ 没有发现异常章节")
    
    print("\\n" + "=" * 70)
    print("🎉 章节编号清理完成")
    print("=" * 70)


if __name__ == "__main__":
    clean_abnormal_chapter_numbers()
