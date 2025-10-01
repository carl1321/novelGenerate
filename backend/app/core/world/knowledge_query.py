"""
知识图谱查询层
"""
from typing import Dict, List, Any, Optional, Tuple
import json
from neo4j import GraphDatabase
from datetime import datetime

from app.core.config import settings
from app.core.world.models import WorldView, Location, Organization
from app.core.character.models import Character


class KnowledgeQueryEngine:
    """知识图谱查询引擎"""
    
    def __init__(self):
        self.driver = GraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
        )
    
    def close(self):
        """关闭数据库连接"""
        self.driver.close()
    
    def get_world_view(self, world_view_id: str) -> Optional[Dict[str, Any]]:
        """获取世界观详细信息"""
        with self.driver.session() as session:
            try:
                result = session.run("""
                    MATCH (w:WorldView {id: $id})
                    RETURN w
                """, id=world_view_id)
                
                record = result.single()
                if record:
                    world_data = dict(record['w'])
                    # 解析JSON字段
                    world_data['power_system'] = json.loads(world_data.get('power_system', '{}'))
                    world_data['geography'] = json.loads(world_data.get('geography', '{}'))
                    world_data['history'] = json.loads(world_data.get('history', '{}'))
                    world_data['culture'] = json.loads(world_data.get('culture', '{}'))
                    return world_data
                return None
            except Exception as e:
                print(f"查询世界观失败: {e}")
                return None
    
    def get_characters_by_world(self, world_view_id: str) -> List[Dict[str, Any]]:
        """获取世界观下的所有角色"""
        with self.driver.session() as session:
            try:
                result = session.run("""
                    MATCH (w:WorldView {id: $world_id})-[:CONTAINS]->(c:Character)
                    RETURN c
                    ORDER BY c.created_at
                """, world_id=world_view_id)
                
                characters = []
                for record in result:
                    char_data = dict(record['c'])
                    # 解析JSON字段
                    char_data['personality'] = json.loads(char_data.get('personality', '[]'))
                    char_data['goals'] = json.loads(char_data.get('goals', '[]'))
                    char_data['relationships'] = json.loads(char_data.get('relationships', '{}'))
                    characters.append(char_data)
                
                return characters
            except Exception as e:
                print(f"查询角色失败: {e}")
                return []
    
    def get_character_relationships(self, character_id: str) -> List[Dict[str, Any]]:
        """获取角色的所有关系"""
        with self.driver.session() as session:
            try:
                result = session.run("""
                    MATCH (c:Character {id: $char_id})-[r]-(other)
                    RETURN other.id as other_id, 
                           other.name as other_name,
                           type(r) as relationship_type,
                           r as properties
                """, char_id=character_id)
                
                relationships = []
                for record in result:
                    rel_data = {
                        'other_id': record['other_id'],
                        'other_name': record['other_name'],
                        'type': record['relationship_type'],
                        'properties': dict(record['properties']) if record['properties'] else {}
                    }
                    relationships.append(rel_data)
                
                return relationships
            except Exception as e:
                print(f"查询角色关系失败: {e}")
                return []
    
    def get_locations_by_region(self, world_view_id: str, region: str = None) -> List[Dict[str, Any]]:
        """获取指定区域的地点"""
        with self.driver.session() as session:
            try:
                if region:
                    query = """
                        MATCH (w:WorldView {id: $world_id})-[:CONTAINS]->(l:Location)
                        WHERE l.region = $region
                        RETURN l
                        ORDER BY l.importance DESC
                    """
                    result = session.run(query, world_id=world_view_id, region=region)
                else:
                    query = """
                        MATCH (w:WorldView {id: $world_id})-[:CONTAINS]->(l:Location)
                        RETURN l
                        ORDER BY l.importance DESC
                    """
                    result = session.run(query, world_id=world_view_id)
                
                locations = []
                for record in result:
                    loc_data = dict(record['l'])
                    locations.append(loc_data)
                
                return locations
            except Exception as e:
                print(f"查询地点失败: {e}")
                return []
    
    def get_organizations_by_type(self, world_view_id: str, org_type: str = None) -> List[Dict[str, Any]]:
        """获取指定类型的组织"""
        with self.driver.session() as session:
            try:
                if org_type:
                    query = """
                        MATCH (w:WorldView {id: $world_id})-[:CONTAINS]->(o:Organization)
                        WHERE o.organization_type = $org_type
                        RETURN o
                        ORDER BY o.power_level DESC
                    """
                    result = session.run(query, world_id=world_view_id, org_type=org_type)
                else:
                    query = """
                        MATCH (w:WorldView {id: $world_id})-[:CONTAINS]->(o:Organization)
                        RETURN o
                        ORDER BY o.power_level DESC
                    """
                    result = session.run(query, world_id=world_view_id)
                
                organizations = []
                for record in result:
                    org_data = dict(record['o'])
                    organizations.append(org_data)
                
                return organizations
            except Exception as e:
                print(f"查询组织失败: {e}")
                return []
    
    def get_characters_at_location(self, location_id: str) -> List[Dict[str, Any]]:
        """获取指定地点的角色"""
        with self.driver.session() as session:
            try:
                result = session.run("""
                    MATCH (c:Character)-[:LOCATED_AT]->(l:Location {id: $location_id})
                    RETURN c
                    ORDER BY c.cultivation_level DESC
                """, location_id=location_id)
                
                characters = []
                for record in result:
                    char_data = dict(record['c'])
                    char_data['personality'] = json.loads(char_data.get('personality', '[]'))
                    char_data['goals'] = json.loads(char_data.get('goals', '[]'))
                    char_data['relationships'] = json.loads(char_data.get('relationships', '{}'))
                    characters.append(char_data)
                
                return characters
            except Exception as e:
                print(f"查询地点角色失败: {e}")
                return []
    
    def get_plot_relevant_data(self, world_view_id: str, plot_segment: Dict[str, Any]) -> Dict[str, Any]:
        """获取剧情段落相关的所有数据"""
        try:
            # 获取基础数据
            world_view = self.get_world_view(world_view_id)
            characters = self.get_characters_by_world(world_view_id)
            
            # 获取涉及角色的详细信息
            involved_characters = []
            for char_id in plot_segment.get('characters_involved', []):
                char_data = next((c for c in characters if c['id'] == char_id), None)
                if char_data:
                    char_data['relationships'] = self.get_character_relationships(char_id)
                    involved_characters.append(char_data)
            
            # 获取相关地点
            locations = self.get_locations_by_region(world_view_id)
            
            # 获取相关组织
            organizations = self.get_organizations_by_type(world_view_id)
            
            return {
                'world_view': world_view,
                'all_characters': characters,
                'involved_characters': involved_characters,
                'locations': locations,
                'organizations': organizations,
                'plot_segment': plot_segment
            }
            
        except Exception as e:
            print(f"获取剧情相关数据失败: {e}")
            return {}
    
    def search_by_keywords(self, world_view_id: str, keywords: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        """根据关键词搜索相关实体"""
        with self.driver.session() as session:
            try:
                results = {
                    'characters': [],
                    'locations': [],
                    'organizations': [],
                    'events': []
                }
                
                for keyword in keywords:
                    # 搜索角色
                    char_result = session.run("""
                        MATCH (w:WorldView {id: $world_id})-[:CONTAINS]->(c:Character)
                        WHERE c.name CONTAINS $keyword OR c.background CONTAINS $keyword
                        RETURN c
                    """, world_id=world_view_id, keyword=keyword)
                    
                    for record in char_result:
                        char_data = dict(record['c'])
                        char_data['personality'] = json.loads(char_data.get('personality', '[]'))
                        char_data['goals'] = json.loads(char_data.get('goals', '[]'))
                        char_data['relationships'] = json.loads(char_data.get('relationships', '{}'))
                        results['characters'].append(char_data)
                    
                    # 搜索地点
                    loc_result = session.run("""
                        MATCH (w:WorldView {id: $world_id})-[:CONTAINS]->(l:Location)
                        WHERE l.name CONTAINS $keyword OR l.description CONTAINS $keyword
                        RETURN l
                    """, world_id=world_view_id, keyword=keyword)
                    
                    for record in loc_result:
                        results['locations'].append(dict(record['l']))
                    
                    # 搜索组织
                    org_result = session.run("""
                        MATCH (w:WorldView {id: $world_id})-[:CONTAINS]->(o:Organization)
                        WHERE o.name CONTAINS $keyword OR o.description CONTAINS $keyword
                        RETURN o
                    """, world_id=world_view_id, keyword=keyword)
                    
                    for record in org_result:
                        results['organizations'].append(dict(record['o']))
                
                return results
                
            except Exception as e:
                print(f"关键词搜索失败: {e}")
                return {'characters': [], 'locations': [], 'organizations': [], 'events': []}
    
    def get_timeline_events(self, world_view_id: str, start_time: str = None, end_time: str = None) -> List[Dict[str, Any]]:
        """获取时间线事件"""
        with self.driver.session() as session:
            try:
                if start_time and end_time:
                    query = """
                        MATCH (w:WorldView {id: $world_id})-[:CONTAINS]->(e:Event)
                        WHERE e.timestamp >= $start_time AND e.timestamp <= $end_time
                        RETURN e
                        ORDER BY e.timestamp
                    """
                    result = session.run(query, world_id=world_view_id, 
                                       start_time=start_time, end_time=end_time)
                else:
                    query = """
                        MATCH (w:WorldView {id: $world_id})-[:CONTAINS]->(e:Event)
                        RETURN e
                        ORDER BY e.timestamp
                    """
                    result = session.run(query, world_id=world_view_id)
                
                events = []
                for record in result:
                    event_data = dict(record['e'])
                    events.append(event_data)
                
                return events
            except Exception as e:
                print(f"查询时间线事件失败: {e}")
                return []
