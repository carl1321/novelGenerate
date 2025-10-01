"""
故事动态更新器
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

from app.core.world.knowledge_query import KnowledgeQueryEngine


class StoryUpdater:
    """故事动态更新器"""
    
    def __init__(self, knowledge_query: KnowledgeQueryEngine):
        self.knowledge_query = knowledge_query
    
    def update_story_progress(self, chapter: Dict[str, Any], world_view_id: str) -> bool:
        """更新故事进度"""
        try:
            with self.knowledge_query.driver.session() as session:
                # 创建章节节点
                session.run("""
                    CREATE (ch:Chapter {
                        id: $id,
                        chapter_number: $chapter_number,
                        title: $title,
                        content: $content,
                        word_count: $word_count,
                        created_at: $created_at
                    })
                """, 
                id=f"chapter_{chapter.chapter_number}",
                chapter_number=chapter.chapter_number,
                title=chapter.title,
                content=chapter.content[:1000],  # 只存储前1000字符
                word_count=chapter.word_count,
                created_at=datetime.now().isoformat()
                )
                
                # 关联到世界观
                session.run("""
                    MATCH (w:WorldView {id: $world_id})
                    MATCH (ch:Chapter {id: $chapter_id})
                    CREATE (w)-[:CONTAINS]->(ch)
                """, world_id=world_view_id, chapter_id=f"chapter_{chapter.chapter_number}")
                
                # 更新角色状态
                self._update_character_states(chapter, session)
                
                # 记录关键事件
                self._record_key_events(chapter, session, world_view_id)
                
                print(f"✅ 第{chapter.chapter_number}章进度已更新到知识图谱")
                return True
                
        except Exception as e:
            print(f"❌ 更新故事进度失败: {e}")
            return False
    
    def _update_character_states(self, chapter: Dict[str, Any], session) -> None:
        """更新角色状态"""
        try:
            # 从章节内容中提取角色状态变化
            character_development = chapter.get('character_development', {})
            
            for char_id, development in character_development.items():
                # 更新角色位置
                if 'location' in development:
                    session.run("""
                        MATCH (c:Character {id: $char_id})
                        SET c.current_location = $location,
                            c.updated_at = $updated_at
                    """, char_id=char_id, location=development['location'], 
                    updated_at=datetime.now().isoformat())
                
                # 更新角色境界
                if 'cultivation_level' in development:
                    session.run("""
                        MATCH (c:Character {id: $char_id})
                        SET c.cultivation_level = $level,
                            c.updated_at = $updated_at
                    """, char_id=char_id, level=development['cultivation_level'],
                    updated_at=datetime.now().isoformat())
                
                # 更新角色关系
                if 'relationships' in development:
                    session.run("""
                        MATCH (c:Character {id: $char_id})
                        SET c.relationships = $relationships,
                            c.updated_at = $updated_at
                    """, char_id=char_id, 
                    relationships=json.dumps(development['relationships'], ensure_ascii=False),
                    updated_at=datetime.now().isoformat())
                    
        except Exception as e:
            print(f"更新角色状态失败: {e}")
    
    def _record_key_events(self, chapter: Dict[str, Any], session, world_view_id: str) -> None:
        """记录关键事件"""
        try:
            for event in chapter.get('key_events', []):
                # 创建事件节点
                session.run("""
                    CREATE (e:Event {
                        id: $id,
                        title: $title,
                        description: $description,
                        event_type: $event_type,
                        importance: $importance,
                        timestamp: $timestamp,
                        chapter_number: $chapter_number
                    })
                """, 
                id=f"event_{world_view_id}_{chapter['chapter_number']}_{len(chapter.get('key_events', []))}",
                title=event.get('title', f"第{chapter['chapter_number']}章事件"),
                description=event.get('description', ''),
                event_type=event.get('type', 'plot'),
                importance=event.get('importance', 5),
                timestamp=datetime.now().isoformat(),
                chapter_number=chapter['chapter_number']
                )
                
                # 关联到世界观
                session.run("""
                    MATCH (w:WorldView {id: $world_id})
                    MATCH (e:Event {id: $event_id})
                    CREATE (w)-[:CONTAINS]->(e)
                """, world_id=world_view_id, event_id=f"event_{world_view_id}_{chapter['chapter_number']}_{len(chapter.get('key_events', []))}")
                
        except Exception as e:
            print(f"记录关键事件失败: {e}")
    
    def get_story_timeline(self, world_view_id: str, start_chapter: int = 1, 
                          end_chapter: int = None) -> List[Dict[str, Any]]:
        """获取故事时间线"""
        try:
            with self.knowledge_query.driver.session() as session:
                if end_chapter:
                    query = """
                        MATCH (w:WorldView {id: $world_id})-[:CONTAINS]->(e:Event)
                        WHERE e.chapter_number >= $start AND e.chapter_number <= $end
                        RETURN e
                        ORDER BY e.chapter_number, e.timestamp
                    """
                    result = session.run(query, world_id=world_view_id, 
                                       start=start_chapter, end=end_chapter)
                else:
                    query = """
                        MATCH (w:WorldView {id: $world_id})-[:CONTAINS]->(e:Event)
                        WHERE e.chapter_number >= $start
                        RETURN e
                        ORDER BY e.chapter_number, e.timestamp
                    """
                    result = session.run(query, world_id=world_view_id, start=start_chapter)
                
                events = []
                for record in result:
                    event_data = dict(record['e'])
                    events.append(event_data)
                
                return events
                
        except Exception as e:
            print(f"获取故事时间线失败: {e}")
            return []
    
    def get_character_development_timeline(self, character_id: str) -> List[Dict[str, Any]]:
        """获取角色发展时间线"""
        try:
            with self.knowledge_query.driver.session() as session:
                result = session.run("""
                    MATCH (c:Character {id: $char_id})
                    MATCH (c)-[:APPEARS_IN]->(ch:Chapter)
                    RETURN ch.chapter_number as chapter_number,
                           ch.title as chapter_title,
                           ch.created_at as timestamp
                    ORDER BY ch.chapter_number
                """, char_id=character_id)
                
                timeline = []
                for record in result:
                    timeline.append({
                        'chapter_number': record['chapter_number'],
                        'chapter_title': record['chapter_title'],
                        'timestamp': record['timestamp']
                    })
                
                return timeline
                
        except Exception as e:
            print(f"获取角色发展时间线失败: {e}")
            return []
    
    def analyze_story_consistency(self, world_view_id: str) -> Dict[str, Any]:
        """分析故事一致性"""
        try:
            with self.knowledge_query.driver.session() as session:
                # 检查角色状态一致性
                character_consistency = session.run("""
                    MATCH (c:Character)
                    WHERE c.current_location IS NOT NULL
                    RETURN c.id as char_id, 
                           c.name as name,
                           c.current_location as location,
                           c.cultivation_level as level
                """).data()
                
                # 检查时间线一致性
                timeline_consistency = session.run("""
                    MATCH (e:Event)
                    RETURN e.chapter_number as chapter,
                           count(e) as event_count
                    ORDER BY e.chapter_number
                """).data()
                
                # 检查关系一致性
                relationship_consistency = session.run("""
                    MATCH (c1:Character)-[r]-(c2:Character)
                    RETURN c1.name as char1, 
                           c2.name as char2,
                           type(r) as relationship_type,
                           count(r) as relationship_count
                """).data()
                
                return {
                    'character_consistency': character_consistency,
                    'timeline_consistency': timeline_consistency,
                    'relationship_consistency': relationship_consistency,
                    'analysis_time': datetime.now().isoformat()
                }
                
        except Exception as e:
            print(f"分析故事一致性失败: {e}")
            return {}
