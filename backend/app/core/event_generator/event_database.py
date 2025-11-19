"""
事件数据库操作
"""
import json
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor

from app.core.event_generator.event_models import Event, EventType, EventImportance, EventCategory, SimpleEvent
from app.core.event_generator.event_scoring_agent import EventScore
from app.core.config import settings


class EventDatabase:
    """事件数据库操作类"""
    
    def __init__(self):
        self.connection_string = settings.DATABASE_URL
    
    def get_connection(self):
        """获取数据库连接"""
        return psycopg2.connect(self.connection_string)
    
    def save_event(self, event: Event) -> bool:
        """保存事件到数据库（简化版）"""
        try:
            conn = self.get_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT insert_event(%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    event.id,
                    event.plot_outline_id,
                    event.title,
                    event.event_type.value if hasattr(event.event_type, 'value') else str(event.event_type),
                    event.description,
                    event.outcome,
                    event.chapter_number,
                    event.sequence_order
                ))
                
                result = cursor.fetchone()[0]
                conn.commit()
                conn.close()
                return result
        except Exception as e:
            print(f"保存事件失败: {e}")
            if 'conn' in locals():
                conn.rollback()
                conn.close()
            return False
    
    def get_event_by_id(self, event_id: str) -> Optional[Event]:
        """根据ID获取事件"""
        try:
            conn = self.get_connection()
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM get_event_by_id(%s)", (event_id,))
                row = cursor.fetchone()
                columns = [desc[0] for desc in cursor.description]
                conn.close()
                if row:
                    return self._row_to_event(row, columns)
                return None
        except Exception as e:
            print(f"获取事件失败: {e}")
            if 'conn' in locals():
                conn.close()
            return None
    
    def get_event(self, event_id: str) -> Optional[Event]:
        """根据ID获取事件（别名方法）"""
        return self.get_event_by_id(event_id)
    
    def update_event(self, event_id: str, event_data: dict) -> bool:
        """更新事件"""
        try:
            conn = self.get_connection()
            with conn.cursor() as cursor:
                # 构建更新SQL
                update_fields = []
                values = []
                
                for field, value in event_data.items():
                    if field in ['description', 'outcome']:
                        update_fields.append(f"{field} = %s")
                        values.append(value)
                
                # 添加更新时间
                update_fields.append("updated_at = CURRENT_TIMESTAMP")
                
                if not update_fields:
                    return False
                
                values.append(event_id)
                sql = f"""
                    UPDATE events 
                    SET {', '.join(update_fields)}
                    WHERE id = %s
                """
                
                cursor.execute(sql, values)
                conn.commit()
                
                return cursor.rowcount > 0
                
        except Exception as e:
            print(f"更新事件失败: {e}")
            return False
        finally:
            if 'conn' in locals():
                conn.close()
    
    def get_all_events(self) -> List[Event]:
        """获取所有事件列表"""
        try:
            conn = self.get_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM events 
                    ORDER BY created_at DESC
                """)
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                conn.close()
                return [self._row_to_event(row, columns) for row in rows]
        except Exception as e:
            print(f"获取所有事件列表失败: {e}")
            if 'conn' in locals():
                conn.close()
            return []

    def get_events_by_plot_outline(self, plot_outline_id: str, act_belonging: str = None) -> List[Event]:
        """根据剧情大纲ID获取事件列表，支持按幕次过滤，只显示最新版本"""
        try:
            conn = self.get_connection()
            with conn.cursor() as cursor:
                if act_belonging:
                    # 按幕次过滤事件，使用进化历史表的最新版本
                    cursor.execute("""
                        SELECT 
                            ewl.original_event_id as id,
                            COALESCE(ewl.current_title, ewl.original_title) as title,
                            COALESCE(ewl.current_event_type, ewl.original_event_type) as event_type,
                            COALESCE(ewl.current_description, ewl.original_description) as description,
                            COALESCE(ewl.current_outcome, ewl.original_outcome) as outcome,
                            ewl.plot_outline_id,
                            ewl.chapter_number,
                            ewl.sequence_order,
                            ewl.original_created_at as created_at,
                            COALESCE(ewl.evolution_created_at, ewl.original_updated_at) as updated_at,
                            ewl.current_evolution_id,
                            ewl.current_version,
                            ewl.evolution_reason,
                            ewl.score_id,
                            ewl.parent_version_id,
                            ewl.has_evolution
                        FROM events_with_latest_evolution ewl
                        JOIN events e ON ewl.original_event_id = e.id
                        WHERE ewl.plot_outline_id = %s
                        ORDER BY ewl.sequence_order, ewl.original_created_at
                    """, (plot_outline_id,))
                else:
                    # 获取所有事件的最新版本
                    cursor.execute("""
                        SELECT 
                            ewl.original_event_id as id,
                            COALESCE(ewl.current_title, ewl.original_title) as title,
                            COALESCE(ewl.current_event_type, ewl.original_event_type) as event_type,
                            COALESCE(ewl.current_description, ewl.original_description) as description,
                            COALESCE(ewl.current_outcome, ewl.original_outcome) as outcome,
                            ewl.plot_outline_id,
                            ewl.chapter_number,
                            ewl.sequence_order,
                            ewl.original_created_at as created_at,
                            COALESCE(ewl.evolution_created_at, ewl.original_updated_at) as updated_at,
                            ewl.current_evolution_id,
                            ewl.current_version,
                            ewl.evolution_reason,
                            ewl.score_id,
                            ewl.parent_version_id,
                            ewl.has_evolution
                        FROM events_with_latest_evolution ewl
                        WHERE ewl.plot_outline_id = %s
                        ORDER BY ewl.sequence_order, ewl.original_created_at
                    """, (plot_outline_id,))
                
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                conn.close()
                return [self._row_to_event_with_evolution(row, columns) for row in rows]
        except Exception as e:
            print(f"获取事件列表失败: {e}")
            if 'conn' in locals():
                conn.close()
            return []
    
    def get_events_by_chapter(self, chapter_number: int, plot_outline_id: str) -> List[Event]:
        """根据章节号获取事件列表"""
        try:
            conn = self.get_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM get_events_by_plot(%s)
                    WHERE chapter_number = %s
                    ORDER BY sequence_order
                """, (plot_outline_id, chapter_number))
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                conn.close()
                return [self._row_to_event(row, columns) for row in rows]
        except Exception as e:
            print(f"获取章节事件失败: {e}")
            if 'conn' in locals():
                conn.close()
            return []
    
    def delete_event(self, event_id: str) -> bool:
        """删除事件"""
        try:
            conn = self.get_connection()
            with conn.cursor() as cursor:
                cursor.execute("SELECT delete_event(%s)", (event_id,))
                result = cursor.fetchone()[0]
                conn.commit()
                conn.close()
                return result
        except Exception as e:
            print(f"删除事件失败: {e}")
            if 'conn' in locals():
                conn.rollback()
                conn.close()
            return False
    
    def delete_events_by_plot_outline(self, plot_outline_id: str) -> bool:
        """删除剧情大纲的所有事件"""
        try:
            conn = self.get_connection()
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM events WHERE plot_outline_id = %s", (plot_outline_id,))
                conn.commit()
                conn.close()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"删除剧情大纲事件失败: {e}")
            if 'conn' in locals():
                conn.rollback()
                conn.close()
            return False
    
    def _row_to_event(self, row: tuple, columns: list) -> Event:
        """将数据库行转换为Event对象（兼容旧方法）"""
        row_dict = dict(zip(columns, row))
        return self._row_to_event_from_dict(row_dict)
    
    def _row_to_event_with_evolution(self, row: tuple, columns: list) -> Event:
        """将数据库行转换为Event对象（支持进化版本）"""
        row_dict = dict(zip(columns, row))
        
        # 检查是否有进化版本（优先使用current_title，如果没有则使用original_title）
        if row_dict.get('has_evolution') and row_dict.get('current_evolution_id'):
            # 这是进化版本
            return self._row_to_evolution_event_from_dict(row_dict)
        else:
            # 这是原始版本，直接使用传入的数据（已经通过COALESCE处理了）
            return self._row_to_event_from_dict(row_dict)
    
    def _row_to_event_from_dict(self, row_dict: dict) -> Event:
        """将字典数据转换为Event对象"""
        # 处理可能为None的字段
        def safe_int(value, default=0):
            if value is None:
                return default
            try:
                return int(value)
            except (ValueError, TypeError):
                return default
        
        def safe_bool(value, default=True):
            if value is None:
                return default
            if isinstance(value, bool):
                return value
            if isinstance(value, str):
                return value.lower() in ('true', 't', '1', 'yes')
            return default
        
        def safe_datetime(value):
            if value is None:
                return None
            if isinstance(value, str):
                try:
                    from datetime import datetime
                    return datetime.fromisoformat(value.replace('Z', '+00:00'))
                except:
                    return None
            return value
        
        return Event(
            id=row_dict['id'],
            title=row_dict.get('title') or row_dict.get('original_title') or row_dict.get('current_title') or '未命名事件',
            event_type=row_dict.get('event_type') or row_dict.get('original_event_type') or row_dict.get('current_event_type') or '日常事件',
            description=row_dict.get('description') or row_dict.get('original_description') or row_dict.get('current_description') or '',
            outcome=row_dict.get('outcome') or row_dict.get('original_outcome') or row_dict.get('current_outcome') or '',
            # 版本管理字段
            version=safe_int(row_dict.get('version'), 1),
            is_current_version=safe_bool(row_dict.get('is_current_version'), True),
            importance=EventImportance.NORMAL,  # 默认重要性
            setting='',  # 简化版不包含地点
            participants=[],  # 简化版不包含参与者
            duration='',  # 简化版不包含持续时间
            plot_impact='',  # 简化版不包含剧情影响
            foreshadowing_elements=[],  # 简化版不包含伏笔元素
            dramatic_tension=5,  # 默认值
            emotional_impact=5,  # 默认值
            chapter_number=safe_int(row_dict.get('chapter_number')),
            sequence_order=safe_int(row_dict.get('sequence_order'), 0),
            plot_outline_id=row_dict['plot_outline_id'],
            created_at=safe_datetime(row_dict.get('created_at'))
        )
    
    # ==================== 事件评分相关方法 ====================
    
    def save_event_score(self, event_id: str, score: EventScore) -> bool:
        """保存事件评分结果"""
        try:
            conn = self.get_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO event_scores (
                        event_id, protagonist_involvement, plot_coherence, 
                        character_development, world_consistency, dramatic_tension,
                        emotional_impact, foreshadowing, overall_quality,
                        feedback, strengths, weaknesses
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    event_id,
                    score.protagonist_involvement,
                    score.plot_coherence,
                    5.0,  # character_development - 使用默认值
                    5.0,  # world_consistency - 使用默认值
                    score.dramatic_tension,
                    score.writing_quality,  # 将文笔质量存储到emotional_impact字段
                    5.0,  # foreshadowing - 使用默认值
                    score.overall_quality,
                    score.feedback,
                    score.strengths,
                    score.weaknesses
                ))
                
                score_id = cursor.fetchone()[0]
                conn.commit()
                conn.close()
                print(f"✅ 事件评分保存成功，评分ID: {score_id}")
                return True
        except Exception as e:
            print(f"❌ 保存事件评分失败: {e}")
            if 'conn' in locals():
                conn.rollback()
                conn.close()
            return False
    
    def get_event_score_by_id(self, score_id: int) -> Optional[EventScore]:
        """根据评分ID获取评分结果"""
        try:
            conn = self.get_connection()
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT * FROM event_scores WHERE id = %s
                """, (score_id,))
                
                row = cursor.fetchone()
                conn.close()
                
                if row:
                    return EventScore(
                        protagonist_involvement=float(row['protagonist_involvement']),
                        plot_coherence=float(row['plot_coherence']),
                        writing_quality=float(row.get('writing_quality', row.get('emotional_impact', 5.0))),
                        dramatic_tension=float(row['dramatic_tension']),
                        overall_quality=float(row['overall_quality']),
                        feedback=row['feedback'] or '',
                        strengths=row['strengths'] or [],
                        weaknesses=row['weaknesses'] or []
                    )
                return None
        except Exception as e:
            print(f"❌ 获取事件评分失败: {e}")
            if 'conn' in locals():
                conn.close()
            return None
    
    def get_event_scores(self, event_id: str) -> List[EventScore]:
        """获取事件的所有评分历史"""
        try:
            conn = self.get_connection()
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT * FROM event_scores 
                    WHERE event_id = %s 
                    ORDER BY created_at DESC
                """, (event_id,))
                
                rows = cursor.fetchall()
                conn.close()
                
                scores = []
                for row in rows:
                    score = EventScore(
                        protagonist_involvement=float(row['protagonist_involvement']),
                        plot_coherence=float(row['plot_coherence']),
                        writing_quality=float(row.get('writing_quality', row.get('emotional_impact', 5.0))),
                        dramatic_tension=float(row['dramatic_tension']),
                        overall_quality=float(row['overall_quality']),
                        feedback=row['feedback'] or '',
                        strengths=row['strengths'] or [],
                        weaknesses=row['weaknesses'] or []
                    )
                    scores.append(score)
                
                return scores
        except Exception as e:
            print(f"❌ 获取事件评分历史失败: {e}")
            if 'conn' in locals():
                conn.close()
            return []
    
    def get_latest_event_score_with_id(self, event_id: str) -> Optional[dict]:
        """获取事件的最新评分（包含ID）"""
        try:
            conn = self.get_connection()
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT * FROM event_scores 
                    WHERE event_id = %s 
                    ORDER BY created_at DESC 
                    LIMIT 1
                """, (event_id,))
                
                row = cursor.fetchone()
                conn.close()
                
                if row:
                    return {
                        'id': row['id'],
                        'protagonist_involvement': float(row['protagonist_involvement']),
                        'plot_coherence': float(row['plot_coherence']),
                        'writing_quality': float(row.get('writing_quality', row.get('emotional_impact', 5.0))),
                        'dramatic_tension': float(row['dramatic_tension']),
                        'overall_quality': float(row['overall_quality']),
                        'feedback': row['feedback'] or '',
                        'strengths': row['strengths'] or [],
                        'weaknesses': row['weaknesses'] or []
                    }
                return None
        except Exception as e:
            print(f"❌ 获取最新事件评分失败: {e}")
            if 'conn' in locals():
                conn.close()
            return None

    def get_latest_evolution(self, event_id: str) -> Optional[dict]:
        """获取事件的最新进化记录"""
        try:
            conn = self.get_connection()
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT * FROM event_evolution_history 
                    WHERE original_event_id = %s 
                    ORDER BY created_at DESC 
                    LIMIT 1
                """, (event_id,))
                
                row = cursor.fetchone()
                conn.close()
                return dict(row) if row else None
        except Exception as e:
            print(f"❌ 获取最新进化失败: {e}")
            return None

    def get_evolution_count(self, event_id: str) -> int:
        """获取事件进化次数"""
        try:
            conn = self.get_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(*) FROM event_evolution_history 
                    WHERE original_event_id = %s
                """, (event_id,))
                
                count = cursor.fetchone()[0]
                conn.close()
                return count
        except Exception as e:
            print(f"❌ 获取进化次数失败: {e}")
            return 0

    def get_evolution_history(self, event_id: str) -> List[dict]:
        """获取事件完整进化历史"""
        try:
            conn = self.get_connection()
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT * FROM event_evolution_history 
                    WHERE original_event_id = %s 
                    ORDER BY created_at ASC
                """, (event_id,))
                
                rows = cursor.fetchall()
                conn.close()
                return [dict(row) for row in rows]
        except Exception as e:
            print(f"❌ 获取进化历史失败: {e}")
            return []

    # ==================== 事件版本管理相关方法 ====================
    
    def get_latest_event_version(self, event_id: str) -> Optional[Event]:
        """获取事件的最新进化版本，如果没有进化版本则返回原始事件"""
        try:
            print(f"🔍 查询事件最新进化版本: {event_id}")
            conn = self.get_connection()
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                # 先尝试获取进化版本
                cursor.execute("SELECT * FROM get_event_latest_version(%s)", (event_id,))
                row = cursor.fetchone()
                
                if row:
                    print(f"✅ 找到事件进化版本: {row['id']} v{row['version']}")
                    conn.close()
                    return self._row_to_evolution_event_from_dict(dict(row))
                else:
                    # 如果没有进化版本，获取原始事件
                    print(f"⚠️ 未找到进化版本，查询原始事件: {event_id}")
                    cursor.execute("SELECT * FROM events WHERE id = %s", (event_id,))
                    original_row = cursor.fetchone()
                    conn.close()
                    
                    if original_row:
                        print(f"✅ 找到原始事件: {original_row['id']}")
                        return self._row_to_event_from_dict(dict(original_row))
                    else:
                        print(f"❌ 原始事件也不存在: {event_id}")
                        return None
                        
        except Exception as e:
            print(f"❌ 获取最新事件版本失败: {e}")
            if 'conn' in locals():
                conn.close()
            return None
    
    def get_event_all_evolution_versions(self, event_id: str) -> List[Event]:
        """获取事件的所有进化版本"""
        try:
            conn = self.get_connection()
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT * FROM get_event_all_evolution_versions(%s)", (event_id,))
                rows = cursor.fetchall()
                conn.close()
                
                return [self._row_to_evolution_event_from_dict(dict(row)) for row in rows]
        except Exception as e:
            print(f"❌ 获取所有进化版本失败: {e}")
            if 'conn' in locals():
                conn.close()
            return []
    
    def _row_to_evolution_event_from_dict(self, data: dict) -> Event:
        """将进化历史表的行转换为Event对象"""
        # 优先使用当前版本（进化版本），如果没有则使用原始版本
        title = data.get('title') or data.get('current_title') or data.get('original_title') or '未命名事件'
        event_type = data.get('event_type') or data.get('current_event_type') or data.get('original_event_type') or '日常事件'
        description = data.get('description') or data.get('current_description') or data.get('original_description') or ''
        outcome = data.get('outcome') or data.get('current_outcome') or data.get('original_outcome') or ''
        
        return Event(
            id=data.get('id') or data.get('original_event_id'),  # 使用原始事件ID
            title=title,
            event_type=event_type,
            description=description,
            outcome=outcome,
            setting='',  # 进化版本可能没有setting
            participants=[],  # 进化版本可能没有participants
            duration='',  # 进化版本可能没有duration
            plot_impact='',  # 进化版本可能没有plot_impact
            foreshadowing_elements=[],  # 进化版本可能没有foreshadowing_elements
            dramatic_tension=5,  # 默认值
            emotional_impact=5,  # 默认值
            sequence_order=data['sequence_order'] or 0,
            character_impact={},  # 默认值
            conflict_core='',  # 默认值
            logical_consistency='',  # 默认值
            realistic_elements='',  # 默认值
            plot_outline_id=data['plot_outline_id'],
            chapter_number=data['chapter_number'],
            created_at=data['created_at'],
            updated_at=data['updated_at'],
            metadata={
                'evolution_id': data.get('current_evolution_id'),
                'version': data.get('current_version', 1),
                'is_current_version': data.get('has_evolution', False),
                'evolution_reason': data.get('evolution_reason'),
                'score_id': data.get('score_id'),
                'parent_version_id': data.get('parent_version_id')
            }
        )
    
    def get_event_all_versions(self, event_id: str) -> List[Event]:
        """获取事件的所有版本（包括原始版本和进化版本）"""
        try:
            conn = self.get_connection()
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                # 获取原始事件
                cursor.execute("SELECT * FROM events WHERE id = %s", (event_id,))
                original_event = cursor.fetchone()
                
                # 获取所有进化版本
                cursor.execute("SELECT * FROM get_event_all_evolution_versions(%s)", (event_id,))
                evolution_versions = cursor.fetchall()
                
                conn.close()
                
                versions = []
                
                # 添加原始事件（版本0）
                if original_event:
                    original_data = dict(original_event)
                    original_event_obj = self._row_to_event_from_dict(original_data)
                    original_event_obj.metadata = original_event_obj.metadata or {}
                    original_event_obj.metadata.update({
                        'version': 0,
                        'is_original': True,
                        'evolution_id': None,
                        'evolution_reason': None,
                        'score_id': None,
                        'parent_version_id': None
                    })
                    versions.append(original_event_obj)
                
                # 添加进化版本
                for row in evolution_versions:
                    evolution_data = dict(row)
                    evolution_event_obj = self._row_to_evolution_event_from_dict(evolution_data)
                    versions.append(evolution_event_obj)
                
                # 按版本号排序
                versions.sort(key=lambda x: x.metadata.get('version', 0))
                
                return versions
        except Exception as e:
            print(f"❌ 获取事件所有版本失败: {e}")
            if 'conn' in locals():
                conn.close()
            return []
    
    def get_latest_versions_by_plot(self, plot_outline_id: str) -> List[Event]:
        """获取剧情大纲下所有事件的最新版本"""
        try:
            conn = self.get_connection()
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT * FROM get_latest_versions_by_plot(%s)", (plot_outline_id,))
                rows = cursor.fetchall()
                conn.close()
                
                return [self._row_to_event_from_dict(dict(row)) for row in rows]
        except Exception as e:
            print(f"❌ 获取剧情大纲最新版本失败: {e}")
            return []
    
    def create_event_version(self, event_id: str, new_title: str, 
                           new_event_type: str, new_description: str, new_outcome: str,
                           evolution_reason: str = "", score_id: int = None) -> Optional[str]:
        """创建事件的新版本（使用进化历史表）"""
        try:
            conn = self.get_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT create_event_evolution_version(%s, %s, %s, %s, %s, %s, %s)
                """, (event_id, new_title, new_event_type, new_description, new_outcome, evolution_reason, score_id))
                
                new_evolution_id = cursor.fetchone()[0]
                conn.commit()
                conn.close()
                
                print(f"✅ 创建事件进化版本成功: {new_evolution_id}")
                return new_evolution_id
        except Exception as e:
            print(f"❌ 创建事件进化版本失败: {e}")
            if 'conn' in locals():
                conn.rollback()
                conn.close()
            return None
    
    def delete_event_version(self, event_id: str, version: Optional[int] = None) -> bool:
        """删除事件版本
        - 如果指定版本号：只删除该版本
        - 如果未指定版本号：删除整个事件的所有版本
        """
        try:
            conn = self.get_connection()
            with conn.cursor() as cursor:
                cursor.execute("SELECT delete_event_version(%s, %s)", (event_id, version))
                result = cursor.fetchone()[0]
                conn.commit()
                conn.close()
                
                if version:
                    print(f"✅ 删除事件版本成功: {event_id} v{version}")
                else:
                    print(f"✅ 删除整个事件成功: {event_id}")
                return result
        except Exception as e:
            print(f"❌ 删除事件版本失败: {e}")
            if 'conn' in locals():
                conn.rollback()
                conn.close()
            return False
    
    # ==================== 事件进化相关方法 ====================
    
    def save_evolution_history(self, original_event_id: str, evolved_event_id: str, score_id: int) -> bool:
        """保存事件进化历史"""
        try:
            conn = self.get_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO event_evolution_history (
                        original_event_id, evolved_event_id, score_id, status
                    ) VALUES (%s, %s, %s, %s)
                    RETURNING id
                """, (
                    original_event_id,
                    evolved_event_id,
                    score_id,
                    'pending'
                ))
                
                evolution_id = cursor.fetchone()[0]
                conn.commit()
                conn.close()
                print(f"✅ 事件进化历史保存成功，进化ID: {evolution_id}")
                return True
        except Exception as e:
            print(f"❌ 保存事件进化历史失败: {e}")
            if 'conn' in locals():
                conn.rollback()
                conn.close()
            return False
    
    def get_evolution_history(self, event_id: str) -> List[Dict[str, Any]]:
        """获取事件的进化历史"""
        try:
            conn = self.get_connection()
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT 
                        eeh.id,
                        eeh.original_event_id,
                        eeh.evolved_event_id,
                        eeh.score_id,
                        eeh.evolution_reason,
                        eeh.status,
                        eeh.created_at,
                        es.overall_quality as score_quality
                    FROM event_evolution_history eeh
                    LEFT JOIN event_scores es ON eeh.score_id = es.id
                    WHERE eeh.original_event_id = %s
                    ORDER BY eeh.created_at DESC
                """, (event_id,))
                
                rows = cursor.fetchall()
                conn.close()
                
                history = []
                for row in rows:
                    history.append({
                        'id': row['id'],
                        'original_event_id': row['original_event_id'],
                        'evolved_event_id': row['evolved_event_id'],
                        'score_id': row['score_id'],
                        'evolution_reason': row['evolution_reason'],
                        'status': row['status'],
                        'created_at': row['created_at'],
                        'score_quality': float(row['score_quality']) if row['score_quality'] else None
                    })
                
                return history
        except Exception as e:
            print(f"❌ 获取事件进化历史失败: {e}")
            if 'conn' in locals():
                conn.close()
            return []
    
    def update_evolution_status(self, evolution_id: int, status: str) -> bool:
        """更新进化状态"""
        try:
            conn = self.get_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE event_evolution_history 
                    SET status = %s, updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                """, (status, evolution_id))
                
                conn.commit()
                conn.close()
                print(f"✅ 进化状态更新成功: {status}")
                return True
        except Exception as e:
            print(f"❌ 更新进化状态失败: {e}")
            if 'conn' in locals():
                conn.rollback()
                conn.close()
            return False
    
    def get_evolution_statistics(self) -> Dict[str, Any]:
        """获取进化统计信息"""
        try:
            conn = self.get_connection()
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_evolutions,
                        COUNT(CASE WHEN status = 'accepted' THEN 1 END) as accepted_evolutions,
                        COUNT(CASE WHEN status = 'rejected' THEN 1 END) as rejected_evolutions,
                        COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending_evolutions,
                        AVG(CASE WHEN status = 'accepted' THEN 1.0 ELSE 0.0 END) as acceptance_rate
                    FROM event_evolution_history
                """)
                
                row = cursor.fetchone()
                conn.close()
                
                return {
                    'total_evolutions': row['total_evolutions'],
                    'accepted_evolutions': row['accepted_evolutions'],
                    'rejected_evolutions': row['rejected_evolutions'],
                    'pending_evolutions': row['pending_evolutions'],
                    'acceptance_rate': float(row['acceptance_rate']) if row['acceptance_rate'] else 0.0
                }
        except Exception as e:
            print(f"❌ 获取进化统计信息失败: {e}")
            if 'conn' in locals():
                conn.close()
            return {}
    
    def get_scoring_statistics(self) -> Dict[str, Any]:
        """获取评分统计信息"""
        try:
            conn = self.get_connection()
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_scores,
                        AVG(overall_quality) as avg_overall_quality,
                        AVG(protagonist_involvement) as avg_protagonist_involvement,
                        AVG(plot_coherence) as avg_plot_coherence,
                        AVG(character_development) as avg_character_development,
                        AVG(world_consistency) as avg_world_consistency,
                        AVG(dramatic_tension) as avg_dramatic_tension,
                        AVG(emotional_impact) as avg_emotional_impact,
                        AVG(foreshadowing) as avg_foreshadowing
                    FROM event_scores
                """)
                
                row = cursor.fetchone()
                conn.close()
                
                return {
                    'total_scores': row['total_scores'],
                    'avg_overall_quality': float(row['avg_overall_quality']) if row['avg_overall_quality'] else 0.0,
                    'avg_protagonist_involvement': float(row['avg_protagonist_involvement']) if row['avg_protagonist_involvement'] else 0.0,
                    'avg_plot_coherence': float(row['avg_plot_coherence']) if row['avg_plot_coherence'] else 0.0,
                    'avg_character_development': float(row['avg_character_development']) if row['avg_character_development'] else 0.0,
                    'avg_world_consistency': float(row['avg_world_consistency']) if row['avg_world_consistency'] else 0.0,
                    'avg_dramatic_tension': float(row['avg_dramatic_tension']) if row['avg_dramatic_tension'] else 0.0,
                    'avg_emotional_impact': float(row['avg_emotional_impact']) if row['avg_emotional_impact'] else 0.0,
                    'avg_foreshadowing': float(row['avg_foreshadowing']) if row['avg_foreshadowing'] else 0.0
                }
        except Exception as e:
            print(f"❌ 获取评分统计信息失败: {e}")
            if 'conn' in locals():
                conn.close()
            return {}
    
    def get_next_sequence_order(self, plot_outline_id: str) -> int:
        """获取下一个可用的序号"""
        try:
            conn = self.get_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT COALESCE(MAX(sequence_order), 0) + 1
                    FROM events 
                    WHERE plot_outline_id = %s
                """, (plot_outline_id,))
                
                next_order = cursor.fetchone()[0]
                conn.close()
                return next_order
        except Exception as e:
            print(f"获取下一个序号失败: {e}")
            if 'conn' in locals():
                conn.close()
            return 1  # 默认返回1
    
    def get_next_sequence_order_for_evolution(self, plot_outline_id: str) -> int:
        """获取下一个可用的序号（考虑进化历史表）"""
        try:
            conn = self.get_connection()
            with conn.cursor() as cursor:
                # 从原始事件表和进化历史表中获取最大序号
                cursor.execute("""
                    SELECT COALESCE(MAX(sequence_order), 0) + 1
                    FROM (
                        SELECT sequence_order FROM events WHERE plot_outline_id = %s
                        UNION ALL
                        SELECT sequence_order FROM event_evolution_history WHERE plot_outline_id = %s
                    ) AS all_events
                """, (plot_outline_id, plot_outline_id))
                
                next_order = cursor.fetchone()[0]
                conn.close()
                return next_order
        except Exception as e:
            print(f"获取下一个序号失败: {e}")
            if 'conn' in locals():
                conn.close()
            return 1  # 默认返回1
    
