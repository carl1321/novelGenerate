"""
知识图谱存储和查询
"""
from typing import Dict, List, Any, Optional, Tuple
from neo4j import GraphDatabase
import json
from datetime import datetime

from app.core.config import settings
from app.core.world.models import (
    WorldView, Location, Organization, CultivationTechnique, 
    Artifact, Pill
)
from app.core.character.models import Character
# 反派模块已删除，统一合并到角色生成中


class KnowledgeGraph:
    """知识图谱管理类"""
    
    def __init__(self):
        self.driver = GraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
        )
    
    def close(self):
        """关闭数据库连接"""
        self.driver.close()
    
    def create_world_view(self, world_view: WorldView) -> bool:
        """创建世界观节点"""
        with self.driver.session() as session:
            try:
                session.run("""
                    CREATE (w:WorldView {
                        id: $id,
                        name: $name,
                        description: $description,
                        core_concept: $core_concept,
                        power_system: $power_system,
                        geography: $geography,
                        history: $history,
                        culture: $culture,
                        created_at: $created_at,
                        updated_at: $updated_at
                    })
                """, 
                id=world_view.id,
                name=world_view.name,
                description=world_view.description,
                core_concept=world_view.core_concept,
                power_system=json.dumps(world_view.power_system, ensure_ascii=False),
                geography=json.dumps(world_view.geography, ensure_ascii=False),
                history=json.dumps(world_view.history, ensure_ascii=False),
                culture=json.dumps(world_view.culture, ensure_ascii=False),
                created_at=world_view.created_at.isoformat(),
                updated_at=world_view.updated_at.isoformat()
                )
                return True
            except Exception as e:
                print(f"创建世界观节点失败: {e}")
                return False
    
    def create_location(self, location: Location, world_view_id: str) -> bool:
        """创建地点节点"""
        with self.driver.session() as session:
            try:
                session.run("""
                    MATCH (w:WorldView {id: $world_view_id})
                    CREATE (l:Location {
                        id: $id,
                        name: $name,
                        description: $description,
                        location_type: $location_type,
                        parent_id: $parent_id,
                        coordinates: $coordinates,
                        climate: $climate,
                        resources: $resources,
                        dangers: $dangers,
                        population: $population,
                        power_level: $power_level,
                        created_at: $created_at,
                        updated_at: $updated_at
                    })
                    CREATE (w)-[:CONTAINS]->(l)
                """,
                world_view_id=world_view_id,
                id=location.id,
                name=location.name,
                description=location.description,
                location_type=location.location_type.value,
                parent_id=location.parent_id,
                coordinates=json.dumps(location.coordinates) if location.coordinates else None,
                climate=location.climate,
                resources=location.resources,
                dangers=location.dangers,
                population=location.population,
                power_level=location.power_level,
                created_at=location.created_at.isoformat(),
                updated_at=location.updated_at.isoformat()
                )
                return True
            except Exception as e:
                print(f"创建地点节点失败: {e}")
                return False
    
    def create_organization(self, organization: Organization, world_view_id: str) -> bool:
        """创建组织节点"""
        with self.driver.session() as session:
            try:
                session.run("""
                    MATCH (w:WorldView {id: $world_view_id})
                    CREATE (o:Organization {
                        id: $id,
                        name: $name,
                        description: $description,
                        org_type: $org_type,
                        location_id: $location_id,
                        leader_id: $leader_id,
                        member_count: $member_count,
                        power_level: $power_level,
                        reputation: $reputation,
                        resources: $resources,
                        techniques: $techniques,
                        enemies: $enemies,
                        allies: $allies,
                        created_at: $created_at,
                        updated_at: $updated_at
                    })
                    CREATE (w)-[:CONTAINS]->(o)
                """,
                world_view_id=world_view_id,
                id=organization.id,
                name=organization.name,
                description=organization.description,
                org_type=organization.org_type.value,
                location_id=organization.location_id,
                leader_id=organization.leader_id,
                member_count=organization.member_count,
                power_level=organization.power_level,
                reputation=organization.reputation,
                resources=organization.resources,
                techniques=organization.techniques,
                enemies=organization.enemies,
                allies=organization.allies,
                created_at=organization.created_at.isoformat(),
                updated_at=organization.updated_at.isoformat()
                )
                return True
            except Exception as e:
                print(f"创建组织节点失败: {e}")
                return False
    
    def create_technique(self, technique: CultivationTechnique, world_view_id: str) -> bool:
        """创建功法节点"""
        with self.driver.session() as session:
            try:
                session.run("""
                    MATCH (w:WorldView {id: $world_view_id})
                    CREATE (t:Technique {
                        id: $id,
                        name: $name,
                        description: $description,
                        level_requirement: $level_requirement,
                        element_type: $element_type,
                        difficulty: $difficulty,
                        power_level: $power_level,
                        cultivation_speed: $cultivation_speed,
                        side_effects: $side_effects,
                        prerequisites: $prerequisites,
                        creator: $creator,
                        origin_org: $origin_org,
                        created_at: $created_at,
                        updated_at: $updated_at
                    })
                    CREATE (w)-[:CONTAINS]->(t)
                """,
                world_view_id=world_view_id,
                id=technique.id,
                name=technique.name,
                description=technique.description,
                level_requirement=technique.level_requirement.value,
                element_type=technique.element_type.value,
                difficulty=technique.difficulty,
                power_level=technique.power_level,
                cultivation_speed=technique.cultivation_speed,
                side_effects=technique.side_effects,
                prerequisites=technique.prerequisites,
                creator=technique.creator,
                origin_org=technique.origin_org,
                created_at=technique.created_at.isoformat(),
                updated_at=technique.updated_at.isoformat()
                )
                return True
            except Exception as e:
                print(f"创建功法节点失败: {e}")
                return False
    
    def create_character(self, character: Character, world_view_id: str) -> bool:
        """创建角色节点"""
        with self.driver.session() as session:
            try:
                session.run("""
                    MATCH (w:WorldView {id: $world_view_id})
                    CREATE (c:Character {
                        id: $id,
                        name: $name,
                        age: $age,
                        gender: $gender,
                        cultivation_level: $cultivation_level,
                        element_type: $element_type,
                        personality: $personality,
                        background: $background,
                        goals: $goals,
                        relationships: $relationships,
                        current_location: $current_location,
                        organization_id: $organization_id,
                        created_at: $created_at,
                        updated_at: $updated_at
                    })
                    CREATE (w)-[:CONTAINS]->(c)
                """,
                world_view_id=world_view_id,
                id=character.id,
                name=character.name,
                age=character.age,
                gender=character.gender,
                cultivation_level=character.cultivation_level.value,
                element_type=character.element_type.value,
                personality=json.dumps(character.personality, ensure_ascii=False),
                background=character.background,
                goals=json.dumps(character.goals, ensure_ascii=False),
                relationships=json.dumps(character.relationships, ensure_ascii=False),
                current_location=character.current_location,
                organization_id=character.organization_id,
                created_at=character.created_at.isoformat(),
                updated_at=character.updated_at.isoformat()
                )
                return True
            except Exception as e:
                print(f"创建角色节点失败: {e}")
                return False
    
    def create_relationship(self, from_id: str, to_id: str, 
                          relationship_type: str, properties: Optional[Dict] = None) -> bool:
        """创建节点间关系"""
        with self.driver.session() as session:
            try:
                query = f"""
                    MATCH (a), (b)
                    WHERE a.id = $from_id AND b.id = $to_id
                    CREATE (a)-[r:{relationship_type}]->(b)
                    SET r += $properties
                """
                session.run(query, 
                           from_id=from_id, 
                           to_id=to_id, 
                           properties=properties or {})
                return True
            except Exception as e:
                print(f"创建关系失败: {e}")
                return False
    
    def query_by_type(self, node_type: str, filters: Optional[Dict] = None) -> List[Dict]:
        """根据类型查询节点"""
        with self.driver.session() as session:
            try:
                if filters:
                    filter_conditions = " AND ".join([f"n.{k} = ${k}" for k in filters.keys()])
                    query = f"MATCH (n:{node_type}) WHERE {filter_conditions} RETURN n"
                    result = session.run(query, **filters)
                else:
                    query = f"MATCH (n:{node_type}) RETURN n"
                    result = session.run(query)
                
                return [record["n"] for record in result]
            except Exception as e:
                print(f"查询节点失败: {e}")
                return []
    
    def query_relationships(self, node_id: str, relationship_types: Optional[List[str]] = None) -> List[Dict]:
        """查询节点的关系"""
        with self.driver.session() as session:
            try:
                if relationship_types:
                    rel_conditions = "|".join(relationship_types)
                    query = f"""
                        MATCH (n)-[r:{rel_conditions}]-(m)
                        WHERE n.id = $node_id
                        RETURN r, m
                    """
                else:
                    query = """
                        MATCH (n)-[r]-(m)
                        WHERE n.id = $node_id
                        RETURN r, m
                    """
                
                result = session.run(query, node_id=node_id)
                return [{"relationship": record["r"], "target": record["m"]} for record in result]
            except Exception as e:
                print(f"查询关系失败: {e}")
                return []
    
    def find_path(self, start_id: str, end_id: str, 
                  max_depth: int = 5) -> List[List[Dict]]:
        """查找两个节点间的路径"""
        with self.driver.session() as session:
            try:
                query = """
                    MATCH path = (start)-[*1..{max_depth}]-(end)
                    WHERE start.id = $start_id AND end.id = $end_id
                    RETURN path
                """.format(max_depth=max_depth)
                
                result = session.run(query, start_id=start_id, end_id=end_id)
                return [record["path"] for record in result]
            except Exception as e:
                print(f"查找路径失败: {e}")
                return []
    
    def get_character_network(self, character_id: str, depth: int = 2) -> Dict:
        """获取角色的关系网络"""
        with self.driver.session() as session:
            try:
                query = f"""
                    MATCH (c:Character {{id: $character_id}})-[r*1..{depth}]-(related)
                    RETURN c, r, related
                """
                
                result = session.run(query, character_id=character_id)
                
                network = {
                    "character": None,
                    "relationships": []
                }
                
                for record in result:
                    if not network["character"]:
                        network["character"] = record["c"]
                    network["relationships"].append({
                        "relationship": record["r"],
                        "related": record["related"]
                    })
                
                return network
            except Exception as e:
                print(f"获取角色网络失败: {e}")
                return {}
    
    def search_by_keyword(self, keyword: str, node_types: Optional[List[str]] = None) -> List[Dict]:
        """根据关键词搜索节点"""
        with self.driver.session() as session:
            try:
                if node_types:
                    type_conditions = "|".join(node_types)
                    query = f"""
                        MATCH (n:{type_conditions})
                        WHERE n.name CONTAINS $keyword 
                           OR n.description CONTAINS $keyword
                        RETURN n
                    """
                else:
                    query = """
                        MATCH (n)
                        WHERE n.name CONTAINS $keyword 
                           OR n.description CONTAINS $keyword
                        RETURN n
                    """
                
                result = session.run(query, keyword=keyword)
                return [record["n"] for record in result]
            except Exception as e:
                print(f"关键词搜索失败: {e}")
                return []
    
    def get_world_statistics(self, world_view_id: str) -> Dict:
        """获取世界观统计信息"""
        with self.driver.session() as session:
            try:
                query = """
                    MATCH (w:WorldView {id: $world_view_id})-[:CONTAINS]->(n)
                    WITH labels(n)[0] as node_type, count(n) as count
                    RETURN node_type, count
                """
                
                result = session.run(query, world_view_id=world_view_id)
                stats = {}
                for record in result:
                    stats[record["node_type"]] = record["count"]
                
                return stats
            except Exception as e:
                print(f"获取统计信息失败: {e}")
                return {}
    
    def validate_consistency(self, world_view_id: str) -> List[str]:
        """验证知识图谱的一致性"""
        violations = []
        
        with self.driver.session() as session:
            try:
                # 检查孤立节点
                query = """
                    MATCH (n)
                    WHERE NOT (n)-[]-()
                    RETURN n
                """
                result = session.run(query)
                isolated = [record["n"]["name"] for record in result]
                if isolated:
                    violations.append(f"发现孤立节点: {', '.join(isolated)}")
                
                # 检查循环引用
                query = """
                    MATCH (n)-[r*]->(n)
                    RETURN n
                """
                result = session.run(query)
                cycles = [record["n"]["name"] for record in result]
                if cycles:
                    violations.append(f"发现循环引用: {', '.join(cycles)}")
                
                # 检查必填字段
                query = """
                    MATCH (n)
                    WHERE n.name IS NULL OR n.name = ""
                    RETURN labels(n)[0] as node_type, n.id as node_id
                """
                result = session.run(query)
                missing_names = [f"{record['node_type']}:{record['node_id']}" for record in result]
                if missing_names:
                    violations.append(f"发现缺少名称的节点: {', '.join(missing_names)}")
                
            except Exception as e:
                print(f"一致性检查失败: {e}")
                violations.append(f"一致性检查失败: {e}")
        
        return violations
    
    # 反派相关方法已删除，统一合并到角色生成中
