#!/usr/bin/env python3
"""
修复章节大纲中的核心事件字段
将事件ID转换为事件标题
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.core.chapter_engine.chapter_database import ChapterOutlineDatabase
from app.core.event_generator.event_database import EventDatabase


def fix_chapter_core_events():
    """修复章节大纲中的核心事件字段"""
    print("=" * 70)
    print("🔧 修复章节大纲中的核心事件字段")
    print("=" * 70)
    
    # 初始化数据库
    chapter_db = ChapterOutlineDatabase()
    event_db = EventDatabase()
    
    # 获取所有章节大纲
    chapters = chapter_db.get_chapters_by_plot('plot_5c4cc022')
    print(f"📊 获取到 {len(chapters)} 个章节大纲")
    
    # 获取所有事件
    events = event_db.get_events_by_plot_outline('plot_5c4cc022')
    print(f"📊 获取到 {len(events)} 个事件")
    
    # 创建事件ID到标题的映射
    event_id_to_title = {}
    for event in events:
        event_id_to_title[event.id] = event.title
    
    print(f"📋 事件ID到标题的映射:")
    for event_id, title in event_id_to_title.items():
        print(f"  {event_id} -> {title}")
    
    print("\n🔍 检查需要修复的章节:")
    print("-" * 50)
    
    # 找出需要修复的章节
    chapters_to_fix = []
    for chapter in chapters:
        if chapter.core_event and chapter.core_event.startswith('event_'):
            chapters_to_fix.append(chapter)
            print(f"  第{chapter.chapter_number}章: {chapter.core_event}")
    
    print(f"\n📊 发现 {len(chapters_to_fix)} 个章节需要修复")
    
    if not chapters_to_fix:
        print("✅ 没有需要修复的章节")
        return
    
    print("\n🔧 开始修复章节核心事件字段:")
    print("-" * 50)
    
    # 修复章节
    fixed_count = 0
    for chapter in chapters_to_fix:
        old_core_event = chapter.core_event
        new_core_event = event_id_to_title.get(chapter.core_event, chapter.core_event)
        
        if old_core_event != new_core_event:
            print(f"修复第{chapter.chapter_number}章:")
            print(f"  原核心事件: {old_core_event}")
            print(f"  新核心事件: {new_core_event}")
            
            # 更新章节
            try:
                chapter.core_event = new_core_event
                chapter_db.update_chapter_outline(chapter.id, chapter)
                fixed_count += 1
                print(f"  ✅ 修复成功")
            except Exception as e:
                print(f"  ❌ 修复失败: {e}")
            print()
        else:
            print(f"第{chapter.chapter_number}章: 无需修复")
    
    print(f"🎉 修复完成! 共修复了 {fixed_count} 个章节")
    
    # 验证修复结果
    print("\n🔍 验证修复结果:")
    print("-" * 50)
    
    updated_chapters = chapter_db.get_chapters_by_plot('plot_5c4cc022')
    event_id_chapters = []
    for chapter in updated_chapters:
        if chapter.core_event and chapter.core_event.startswith('event_'):
            event_id_chapters.append(chapter)
    
    if event_id_chapters:
        print(f"❌ 仍有 {len(event_id_chapters)} 个章节的核心事件是事件ID格式:")
        for chapter in event_id_chapters:
            print(f"  第{chapter.chapter_number}章: {chapter.core_event}")
    else:
        print("✅ 所有章节的核心事件都已修复为事件标题格式")
    
    print("\n" + "=" * 70)
    print("🎉 章节核心事件字段修复完成")
    print("=" * 70)


if __name__ == "__main__":
    fix_chapter_core_events()
