"""
剧情大纲数据库操作类
"""
import json
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
from app.core.config import settings
from .plot_models import PlotOutline, PlotStatus


class PlotOutlineDatabase:
    """剧情大纲数据库操作类"""
    
    def __init__(self):
        self.connection_string = settings.DATABASE_URL
    
    def get_connection(self):
        """获取数据库连接"""
        return psycopg2.connect(
            self.connection_string,
            cursor_factory=RealDictCursor
        )
    
    def save_plot_outline(self, plot_outline: PlotOutline) -> bool:
        """保存剧情大纲到数据库"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    # 准备数据
                    plot_data = {
                        'id': plot_outline.id,
                        'title': plot_outline.title,
                        'worldview_id': plot_outline.worldview_id,
                        'story_summary': plot_outline.story_summary,
                        'core_conflict': plot_outline.core_conflict,
                        'story_tone': plot_outline.story_tone,
                        'narrative_structure': plot_outline.narrative_structure,
                        'theme': plot_outline.theme,
                        'protagonist_name': plot_outline.protagonist_name,
                        'protagonist_background': plot_outline.protagonist_background,
                        'protagonist_personality': plot_outline.protagonist_personality,
                        'protagonist_goals': plot_outline.protagonist_goals,
                        'core_concept': plot_outline.core_concept,
                        'world_description': plot_outline.world_description,
                        'geography_setting': plot_outline.geography_setting,
                        'target_word_count': plot_outline.target_word_count,
                        'estimated_chapters': plot_outline.estimated_chapters,
                        'status': plot_outline.status.value if hasattr(plot_outline.status, 'value') else str(plot_outline.status),
                        'created_at': plot_outline.created_at,
                        'updated_at': plot_outline.updated_at,
                        'created_by': plot_outline.created_by
                    }
                    
                    # 插入剧情大纲主表
                    query = """
                        INSERT INTO plot_outlines (
                            id, title, worldview_id, story_summary, core_conflict, 
                            story_tone, narrative_structure, theme, protagonist_name, 
                            protagonist_background, protagonist_personality, protagonist_goals,
                            core_concept, world_description, geography_setting,
                            target_word_count, estimated_chapters, status, 
                            created_at, updated_at, created_by
                        ) VALUES (
                            %(id)s, %(title)s, %(worldview_id)s, %(story_summary)s, %(core_conflict)s, 
                            %(story_tone)s, %(narrative_structure)s, %(theme)s, %(protagonist_name)s, 
                            %(protagonist_background)s, %(protagonist_personality)s, %(protagonist_goals)s,
                            %(core_concept)s, %(world_description)s, %(geography_setting)s,
                            %(target_word_count)s, %(estimated_chapters)s, %(status)s, 
                            %(created_at)s, %(updated_at)s, %(created_by)s
                        ) ON CONFLICT (id) DO UPDATE SET
                            title = EXCLUDED.title,
                            story_summary = EXCLUDED.story_summary,
                            core_conflict = EXCLUDED.core_conflict,
                            story_tone = EXCLUDED.story_tone,
                            narrative_structure = EXCLUDED.narrative_structure,
                            theme = EXCLUDED.theme,
                            protagonist_name = EXCLUDED.protagonist_name,
                            protagonist_background = EXCLUDED.protagonist_background,
                            protagonist_personality = EXCLUDED.protagonist_personality,
                            protagonist_goals = EXCLUDED.protagonist_goals,
                            core_concept = EXCLUDED.core_concept,
                            world_description = EXCLUDED.world_description,
                            geography_setting = EXCLUDED.geography_setting,
                            target_word_count = EXCLUDED.target_word_count,
                            estimated_chapters = EXCLUDED.estimated_chapters,
                            status = EXCLUDED.status,
                            updated_at = EXCLUDED.updated_at
                    """
                    
                    cursor.execute(query, plot_data)
                    
                    # 保存幕次信息
                    self._save_acts(cursor, plot_outline)
                    
                    conn.commit()
                    print(f"✅ 剧情大纲已保存到数据库: {plot_outline.id}")
                    return True
            
        except Exception as e:
            print(f"❌ 保存剧情大纲失败: {e}")
            return False
    
    def _save_acts(self, cursor, plot_outline: PlotOutline):
        """保存幕次信息"""
        try:
            # 先删除现有的幕次
            cursor.execute(
                "DELETE FROM acts WHERE plot_outline_id = %s", 
                (plot_outline.id,)
            )
            
            # 插入新的幕次
            for act in plot_outline.acts:
                act_data = {
                    'id': f"{plot_outline.id}_act_{act.act_number}",
                    'plot_outline_id': plot_outline.id,
                    'act_number': act.act_number,
                    'act_name': act.act_name,
                    'core_mission': act.core_mission,
                    'daily_events': act.daily_events,
                    'conflict_events': act.conflict_events,
                    'special_events': act.special_events,
                    'major_events': act.major_events,
                    'stage_result': act.stage_result
                }
                
                cursor.execute("""
                    INSERT INTO acts (
                        id, plot_outline_id, act_number, act_name, core_mission,
                        daily_events, conflict_events, special_events, major_events, stage_result
                    ) VALUES (
                        %(id)s, %(plot_outline_id)s, %(act_number)s, %(act_name)s, %(core_mission)s,
                        %(daily_events)s, %(conflict_events)s, %(special_events)s, %(major_events)s, %(stage_result)s
                    )
                """, act_data)
                
        except Exception as e:
            print(f"❌ 保存幕次信息失败: {e}")
    
    def get_plot_outline(self, plot_id: str) -> Optional[PlotOutline]:
        """获取剧情大纲"""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    query = """
                        SELECT * FROM plot_outlines WHERE id = %s
                    """
                    
                    cursor.execute(query, (plot_id,))
                    row = cursor.fetchone()
                    
                    if row:
                        return self._row_to_plot_outline(dict(row))
                    return None
                    
        except Exception as e:
            print(f"❌ 获取剧情大纲失败: {e}")
            return None
    
    def get_plot_outlines_by_worldview(self, worldview_id: str = None, status: str = None, limit: int = 20, offset: int = 0) -> List[PlotOutline]:
        """根据条件获取剧情大纲列表"""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    # 构建查询条件
                    conditions = []
                    params = []
                    
                    if worldview_id:
                        conditions.append("worldview_id = %s")
                        params.append(worldview_id)
                    
                    if status:
                        conditions.append("status = %s")
                        params.append(status)
                    
                    where_clause = ""
                    if conditions:
                        where_clause = "WHERE " + " AND ".join(conditions)
                    
                    query = f"""
                        SELECT * FROM plot_outlines 
                        {where_clause}
                        ORDER BY created_at DESC
                        LIMIT %s OFFSET %s
                    """
                    
                    params.extend([limit, offset])
                    cursor.execute(query, params)
                    rows = cursor.fetchall()
                    
                    # 转换为PlotOutline对象
                    plot_outlines = []
                    for row in rows:
                        try:
                            plot_outline = self._row_to_plot_outline(dict(row))
                            plot_outlines.append(plot_outline)
                        except Exception as e:
                            print(f"❌ 转换剧情大纲失败: {e}")
                            continue
                    
                    return plot_outlines
                    
        except Exception as e:
            print(f"❌ 获取剧情大纲列表失败: {e}")
            return []
    
    def update_plot_outline_status(self, plot_id: str, status: PlotStatus) -> bool:
        """更新剧情大纲状态"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    query = """
                        UPDATE plot_outlines 
                        SET status = %s, updated_at = CURRENT_TIMESTAMP 
                        WHERE id = %s
                    """
                    
                    status_value = status.value if hasattr(status, 'value') else str(status)
                    cursor.execute(query, (status_value, plot_id))
                    conn.commit()
                    
                    print(f"✅ 剧情大纲状态已更新: {plot_id} -> {status_value}")
                    return True
                    
        except Exception as e:
            print(f"❌ 更新剧情大纲状态失败: {e}")
            return False
    
    def delete_plot_outline(self, plot_id: str) -> bool:
        """删除剧情大纲（检查是否有关联的章节大纲）"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    # 1. 检查是否有关联的章节大纲
                    cursor.execute("""
                        SELECT COUNT(*) FROM chapter_outlines 
                        WHERE plot_outline_id = %s
                    """, (plot_id,))
                    
                    result = cursor.fetchone()
                    chapter_count = result['count'] if result else 0
                    if chapter_count > 0:
                        print(f"❌ 无法删除剧情大纲 {plot_id}：存在 {chapter_count} 个关联的章节大纲")
                        return False
                    
                    # 2. 如果没有关联的章节大纲，则删除剧情大纲
                    query = "DELETE FROM plot_outlines WHERE id = %s"
                    cursor.execute(query, (plot_id,))
                    conn.commit()
                    
                    print(f"✅ 剧情大纲已删除: {plot_id}")
                    return True
                    
        except Exception as e:
            print(f"❌ 删除剧情大纲失败: {e}")
            return False
    
    def _row_to_plot_outline(self, row: Dict[str, Any]) -> PlotOutline:
        """将数据库记录转换为PlotOutline对象"""
        try:
            # 获取幕次信息
            acts = self._get_acts_by_plot_id(row['id'])
            
            return PlotOutline(
                id=row['id'],
                title=row['title'],
                worldview_id=row['worldview_id'],
                story_summary=row['story_summary'],
                core_conflict=row['core_conflict'],
                story_tone=row['story_tone'],
                narrative_structure=row['narrative_structure'],
                theme=row['theme'],
                protagonist_name=row['protagonist_name'],
                protagonist_background=row['protagonist_background'],
                protagonist_personality=row['protagonist_personality'],
                protagonist_goals=row['protagonist_goals'],
                core_concept=row['core_concept'],
                world_description=row['world_description'],
                geography_setting=row['geography_setting'],
                acts=acts,
                target_word_count=row['target_word_count'],
                estimated_chapters=row['estimated_chapters'],
                status=row['status'],
                created_at=row['created_at'],
                updated_at=row['updated_at'],
                created_by=row['created_by']
            )
        except Exception as e:
            print(f"❌ 转换PlotOutline失败: {e}")
            print(f"   记录数据: {row}")
            raise
    
    def _get_acts_by_plot_id(self, plot_id: str) -> List[Dict[str, Any]]:
        """获取剧情大纲的幕次信息"""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    query = """
                        SELECT * FROM acts WHERE plot_outline_id = %s ORDER BY act_number
                    """
                    cursor.execute(query, (plot_id,))
                    rows = cursor.fetchall()
                    
                    acts = []
                    for row in rows:
                        act_data = {
                            'act_number': row['act_number'],
                            'act_name': row['act_name'],
                            'core_mission': row['core_mission'],
                            'daily_events': row['daily_events'],
                            'conflict_events': row['conflict_events'],
                            'special_events': row['special_events'],
                            'major_events': row['major_events'],
                            'stage_result': row['stage_result']
                        }
                        acts.append(act_data)
                    
                    return acts
                    
        except Exception as e:
            print(f"❌ 获取幕次信息失败: {e}")
            return []
