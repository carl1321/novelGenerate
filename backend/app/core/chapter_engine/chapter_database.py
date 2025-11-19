"""
章节大纲数据库操作类 - 与剧情大纲字段统一
"""
import json
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.core.chapter_engine.chapter_models_simplified import ChapterOutline, Scene
from app.core.config import settings


class ChapterOutlineDatabase:
    """章节大纲数据库操作类"""
    
    def __init__(self):
        self.connection_string = settings.DATABASE_URL
    
    def get_connection(self):
        """获取数据库连接"""
        return psycopg2.connect(self.connection_string)
    
    def get_next_chapter_number(self, plot_outline_id: str) -> int:
        """获取下一个可用的章节编号（基于连续编号）"""
        try:
            conn = self.get_connection()
            with conn.cursor() as cursor:
                # 获取所有章节编号，找到第一个缺失的编号
                cursor.execute("""
                    SELECT chapter_number
                    FROM chapter_outlines 
                    WHERE plot_outline_id = %s AND chapter_number IS NOT NULL
                    ORDER BY chapter_number
                """, (plot_outline_id,))
                
                existing_numbers = [row[0] for row in cursor.fetchall()]
                conn.close()
                
                # 找到第一个缺失的编号
                if not existing_numbers:
                    return 1
                
                # 从1开始查找第一个缺失的编号
                for i in range(1, max(existing_numbers) + 2):
                    if i not in existing_numbers:
                        return i
                
                # 如果没有缺失，返回下一个编号
                return max(existing_numbers) + 1
                
        except Exception as e:
            print(f"❌ 获取下一个章节编号失败: {e}")
            return 1
    
    def save_chapter_outline(self, chapter_outline: ChapterOutline) -> bool:
        """保存章节大纲到数据库"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    # 插入章节大纲主记录
                    cursor.execute("""
                        INSERT INTO chapter_outlines (
                            id, plot_outline_id, chapter_number, title,
                            act_belonging,
                            chapter_summary,
                            core_event,
                            status,
                            created_at, updated_at
                        ) VALUES (
                            %s, %s, %s, %s,
                            %s,
                            %s,
                            %s,
                            %s,
                            %s, %s
                        )
                        ON CONFLICT (plot_outline_id, chapter_number) DO UPDATE SET
                            title = EXCLUDED.title,
                            act_belonging = EXCLUDED.act_belonging,
                            chapter_summary = EXCLUDED.chapter_summary,
                            core_event = EXCLUDED.core_event,
                            status = EXCLUDED.status,
                            updated_at = CURRENT_TIMESTAMP
                    """, (
                        chapter_outline.id,
                        chapter_outline.plot_outline_id,
                        chapter_outline.chapter_number,
                        chapter_outline.title,
                        chapter_outline.act_belonging,
                        chapter_outline.chapter_summary,
                        chapter_outline.core_event,
                        chapter_outline.status.value if hasattr(chapter_outline.status, 'value') else str(chapter_outline.status),
                        chapter_outline.created_at,
                        chapter_outline.updated_at
                    ))
                    
                    # 保存场景信息
                    self._save_scenes(cursor, chapter_outline.id, chapter_outline.key_scenes)
                    
                    conn.commit()
                    print(f"✅ 章节大纲保存成功: {chapter_outline.id}")
                    return True
                    
        except Exception as e:
            print(f"❌ 保存章节大纲失败: {e}")
            return False
    
    def _save_scenes(self, cursor, chapter_outline_id: str, scenes: List[Scene]):
        """保存场景信息"""
        try:
            # 先删除现有场景
            cursor.execute("DELETE FROM scenes WHERE chapter_outline_id = %s", (chapter_outline_id,))
            
            # 插入新场景
            for i, scene in enumerate(scenes, 1):
                cursor.execute("""
                    INSERT INTO scenes (
                        id, chapter_outline_id, scene_number, title, description,
                        scene_title, scene_description, created_at
                    ) VALUES (
                        %s, %s, %s, %s, %s,
                        %s, %s, %s
                    )
                """, (
                    f"scene_{chapter_outline_id}_{i}",
                    chapter_outline_id,
                    i,  # 场景编号
                    scene.scene_title,  # 同时填充旧字段
                    scene.scene_description,  # 同时填充旧字段
                    scene.scene_title,  # 新字段
                    scene.scene_description,  # 新字段
                    datetime.now()
                ))
                
        except Exception as e:
            print(f"❌ 保存场景信息失败: {e}")
    
    def get_chapter_outline(self, chapter_id: str) -> Optional[ChapterOutline]:
        """获取单个章节大纲"""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute("""
                        SELECT * FROM chapter_outlines WHERE id = %s
                    """, (chapter_id,))
                    
                    row = cursor.fetchone()
                    if not row:
                        return None
                    
                    return self._row_to_chapter_outline(dict(row))
                    
        except Exception as e:
            print(f"❌ 获取章节大纲失败: {e}")
            return None
    
    def get_all_chapter_outlines(self, limit: int = 100, offset: int = 0) -> List[ChapterOutline]:
        """获取所有章节大纲列表"""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute("""
                        SELECT * FROM chapter_outlines 
                        ORDER BY plot_outline_id, chapter_number ASC
                        LIMIT %s OFFSET %s
                    """, (limit, offset))
                    
                    rows = cursor.fetchall()
                    chapters = []
                    
                    for row in rows:
                        try:
                            chapter = self._row_to_chapter_outline(dict(row))
                            chapters.append(chapter)
                        except Exception as e:
                            print(f"解析章节大纲失败: {e}")
                            continue
                    
                    return chapters
                    
        except Exception as e:
            print(f"获取所有章节大纲失败: {e}")
            return []

    def get_chapters_by_plot(self, plot_outline_id: str, limit: int = 50, offset: int = 0) -> List[ChapterOutline]:
        """根据剧情大纲获取章节大纲列表"""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute("""
                        SELECT * FROM chapter_outlines 
                        WHERE plot_outline_id = %s 
                        ORDER BY chapter_number ASC
                        LIMIT %s OFFSET %s
                    """, (plot_outline_id, limit, offset))
                    
                    rows = cursor.fetchall()
                    chapters = []
                    
                    for row in rows:
                        try:
                            chapter = self._row_to_chapter_outline(dict(row))
                            chapters.append(chapter)
                        except Exception as e:
                            print(f"❌ 转换章节大纲失败: {e}")
                            continue
                    
                    return chapters
                    
        except Exception as e:
            print(f"❌ 获取章节大纲列表失败: {e}")
            return []
    
    def get_chapter_outline_by_plot_and_number(self, plot_outline_id: str, chapter_number: int) -> Optional[ChapterOutline]:
        """根据剧情大纲ID和章节编号获取章节大纲"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM chapter_outlines 
                WHERE plot_outline_id = %s AND chapter_number = %s
            """, (plot_outline_id, chapter_number))
            
            row = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if row:
                return self._row_to_chapter_outline(row)
            return None
            
        except Exception as e:
            print(f"❌ 获取章节大纲失败: {e}")
            return None
    
    def _row_to_chapter_outline(self, row: Dict[str, Any]) -> ChapterOutline:
        """将数据库记录转换为ChapterOutline对象"""
        try:
            # 获取场景信息
            scenes = self._get_scenes_for_chapter(row['id'])
            
            return ChapterOutline(
                id=row['id'],
                plot_outline_id=row['plot_outline_id'],
                chapter_number=row['chapter_number'],
                title=row['title'],
                
                # 章节定位
                act_belonging=row['act_belonging'],
                
                # 章节内容
                chapter_summary=row['chapter_summary'],
                core_event=row.get('core_event') or '',
                key_scenes=scenes,
                
                # 元数据
                status=row['status'],
                
                created_at=row['created_at'],
                updated_at=row['updated_at']
            )
            
        except Exception as e:
            print(f"❌ 转换ChapterOutline失败: {e}")
            print(f"   记录数据: {row}")
            raise
    
    def _get_scenes_for_chapter(self, chapter_outline_id: str) -> List[Scene]:
        """获取章节的场景信息"""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute("""
                        SELECT * FROM scenes 
                        WHERE chapter_outline_id = %s 
                        ORDER BY scene_number ASC
                    """, (chapter_outline_id,))
                    
                    rows = cursor.fetchall()
                    scenes = []
                    
                    for row in rows:
                        try:
                            scene_data = dict(row)
                            
                            scene = Scene(
                                scene_title=scene_data.get('scene_title') or scene_data.get('title') or '',
                                scene_description=scene_data.get('scene_description') or scene_data.get('description') or '',
                                event_relation=scene_data.get('event_relation') or ''
                            )
                            scenes.append(scene)
                        except Exception as e:
                            print(f"❌ 转换场景失败: {e}")
                            continue
                    
                    return scenes
                    
        except Exception as e:
            print(f"❌ 获取场景信息失败: {e}")
            return []
    
    
    def update_chapter_outline(self, chapter_id: str, chapter_outline: ChapterOutline) -> bool:
        """更新章节大纲"""
        try:
            # 先删除现有记录，再插入新记录
            self.delete_chapter_outline(chapter_id)
            return self.save_chapter_outline(chapter_outline)
        except Exception as e:
            print(f"❌ 更新章节大纲失败: {e}")
            return False
    
    def delete_chapter_outline(self, chapter_id: str) -> bool:
        """删除章节大纲（检查是否有关联的详细剧情）"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    # 1. 检查是否有关联的详细剧情
                    print(f"🔍 开始检查章节大纲 {chapter_id} 的详细剧情")
                    cursor.execute("""
                        SELECT COUNT(*) FROM detailed_plots 
                        WHERE chapter_outline_id = %s
                    """, (chapter_id,))
                    
                    result = cursor.fetchone()
                    detailed_plot_count = result[0] if result else 0
                    print(f"🔍 检查章节大纲 {chapter_id} 的详细剧情数量: {detailed_plot_count}")
                    
                    # 额外检查：查询所有详细剧情
                    cursor.execute("SELECT id, chapter_outline_id FROM detailed_plots")
                    all_plots = cursor.fetchall()
                    print(f"🔍 数据库中所有详细剧情: {len(all_plots)}")
                    for plot in all_plots:
                        print(f"  - {plot[0]}: {plot[1]}")
                    
                    if detailed_plot_count > 0:
                        print(f"❌ 无法删除章节大纲 {chapter_id}：存在 {detailed_plot_count} 个关联的详细剧情")
                        return False
                    
                    # 2. 如果没有关联的详细剧情，则删除章节大纲
                    # 删除场景（外键约束会自动处理）
                    cursor.execute("DELETE FROM scenes WHERE chapter_outline_id = %s", (chapter_id,))
                    
                    # 删除章节大纲
                    cursor.execute("DELETE FROM chapter_outlines WHERE id = %s", (chapter_id,))
                    
                    conn.commit()
                    print(f"✅ 章节大纲删除成功: {chapter_id}")
                    return True
                    
        except Exception as e:
            print(f"❌ 删除章节大纲失败: {e}")
            return False
    
    def get_chapter_outline_stats(self, plot_outline_id: str) -> Dict[str, Any]:
        """获取章节大纲统计信息"""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    # 基本统计
                    cursor.execute("""
                        SELECT 
                            COUNT(*) as total_chapters,
                            AVG(estimated_word_count) as avg_word_count,
                            SUM(estimated_word_count) as total_word_count,
                            AVG(tension_level) as avg_tension_level
                        FROM chapter_outlines 
                        WHERE plot_outline_id = %s
                    """, (plot_outline_id,))
                    
                    stats = cursor.fetchone()
                    
                    # 按状态统计
                    cursor.execute("""
                        SELECT status, COUNT(*) as count
                        FROM chapter_outlines 
                        WHERE plot_outline_id = %s
                        GROUP BY status
                    """, (plot_outline_id,))
                    
                    status_stats = {row['status']: row['count'] for row in cursor.fetchall()}
                    
                    return {
                        'total_chapters': stats['total_chapters'] or 0,
                        'avg_word_count': float(stats['avg_word_count']) if stats['avg_word_count'] else 0,
                        'total_word_count': stats['total_word_count'] or 0,
                        'avg_tension_level': float(stats['avg_tension_level']) if stats['avg_tension_level'] else 0,
                        'status_distribution': status_stats
                    }
                    
        except Exception as e:
            print(f"❌ 获取统计信息失败: {e}")
            return {}
