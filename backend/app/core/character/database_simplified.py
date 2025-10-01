"""
简化的角色数据库管理器
使用单一characters表存储所有角色信息
"""
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Dict, List, Any, Optional
import json
import logging

logger = logging.getLogger(__name__)


class CharacterDatabase:
    """简化的角色数据库管理器"""
    
    def __init__(self, connection_string: str = None):
        if connection_string is None:
            # 使用配置文件中的数据库连接字符串
            from app.core.config import settings
            connection_string = settings.DATABASE_URL
        self.connection_string = connection_string
    
    def get_connection(self):
        """获取数据库连接"""
        return psycopg2.connect(self.connection_string)
    
    def insert_character(self, character_data: Dict[str, Any], created_by: str = "system") -> str:
        """插入角色数据"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    # 直接插入到characters表
                    cursor.execute("""
                        INSERT INTO characters (
                            character_id, worldview_id, name, age, gender, role_type,
                            cultivation_level, element_type, background, current_location,
                            organization_id, personality_traits, goals, relationships,
                            techniques, artifacts, resources, stats, metadata,
                            created_by, status
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                        )
                        RETURNING character_id
                    """, (
                        character_data.get("id"),
                        character_data.get("worldview_id"),
                        character_data.get("name"),
                        character_data.get("age"),
                        character_data.get("gender"),
                        character_data.get("role_type"),
                        character_data.get("cultivation_level"),
                        character_data.get("element_type"),
                        character_data.get("background"),
                        character_data.get("current_location"),
                        character_data.get("organization_id"),
                        json.dumps(character_data.get("personality_traits", [])),
                        json.dumps(character_data.get("goals", [])),
                        json.dumps(character_data.get("relationships", {})),
                        json.dumps(character_data.get("techniques", [])),
                        json.dumps(character_data.get("artifacts", [])),
                        json.dumps(character_data.get("resources", {})),
                        json.dumps(character_data.get("stats", {})),
                        json.dumps(character_data.get("metadata", {})),
                        created_by,
                        character_data.get("status", "active")
                    ))
                    
                    result = cursor.fetchone()
                    conn.commit()
                    return result[0] if result else character_data.get("id")
                    
        except Exception as e:
            logger.error(f"插入角色数据失败: {e}")
            raise
    
    def get_character(self, character_id: str) -> Optional[Dict[str, Any]]:
        """获取角色数据"""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute("""
                        SELECT * FROM characters WHERE character_id = %s
                    """, (character_id,))
                    
                    result = cursor.fetchone()
                    if result:
                        # JSONB字段已经是Python对象，不需要解析
                        character_data = dict(result)
                        
                        # 调试信息：检查单个角色查询的原始结果
                        logger.debug(f"单个角色查询原始结果 - 所有字段: {list(character_data.keys())}")
                        logger.debug(f"单个角色查询原始结果 - worldview_id: {character_data.get('worldview_id')}")
                        logger.debug(f"单个角色查询原始结果 - character_id: {character_data.get('character_id')}")
                        logger.debug(f"单个角色查询原始结果 - name: {character_data.get('name')}")
                        
                        if character_data.get('personality_traits') is None:
                            character_data['personality_traits'] = []
                        if character_data.get('goals') is None:
                            character_data['goals'] = []
                        if character_data.get('relationships') is None:
                            character_data['relationships'] = {}
                        if character_data.get('techniques') is None:
                            character_data['techniques'] = []
                        if character_data.get('artifacts') is None:
                            character_data['artifacts'] = []
                        if character_data.get('resources') is None:
                            character_data['resources'] = {}
                        if character_data.get('stats') is None:
                            character_data['stats'] = {}
                        if character_data.get('metadata') is None:
                            character_data['metadata'] = {}
                        return character_data
                    return None
                    
        except Exception as e:
            logger.error(f"获取角色数据失败: {e}")
            raise
    
    def update_character(self, character_id: str, character_data: Dict[str, Any]) -> bool:
        """更新角色数据"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        UPDATE characters SET
                            worldview_id = %s, name = %s, age = %s, gender = %s, role_type = %s,
                            cultivation_level = %s, element_type = %s, background = %s,
                            current_location = %s, organization_id = %s,
                            personality_traits = %s, goals = %s, relationships = %s,
                            techniques = %s, artifacts = %s, resources = %s,
                            stats = %s, metadata = %s, status = %s
                        WHERE character_id = %s
                    """, (
                        character_data.get("worldview_id"),
                        character_data.get("name"),
                        character_data.get("age"),
                        character_data.get("gender"),
                        character_data.get("role_type"),
                        character_data.get("cultivation_level"),
                        character_data.get("element_type"),
                        character_data.get("background"),
                        character_data.get("current_location"),
                        character_data.get("organization_id"),
                        json.dumps(character_data.get("personality_traits", [])),
                        json.dumps(character_data.get("goals", [])),
                        json.dumps(character_data.get("relationships", {})),
                        json.dumps(character_data.get("techniques", [])),
                        json.dumps(character_data.get("artifacts", [])),
                        json.dumps(character_data.get("resources", {})),
                        json.dumps(character_data.get("stats", {})),
                        json.dumps(character_data.get("metadata", {})),
                        character_data.get("status", "active"),
                        character_id
                    ))
                    
                    conn.commit()
                    return cursor.rowcount > 0
                    
        except Exception as e:
            logger.error(f"更新角色数据失败: {e}")
            raise
    
    def delete_character(self, character_id: str) -> bool:
        """删除角色数据"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        DELETE FROM characters WHERE character_id = %s
                    """, (character_id,))
                    
                    conn.commit()
                    return cursor.rowcount > 0
                    
        except Exception as e:
            logger.error(f"删除角色数据失败: {e}")
            raise
    
    def search_characters(self, worldview_id: str = None, role_type: str = None, 
                         name: str = None, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """搜索角色"""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    # 构建查询条件
                    conditions = []
                    params = []
                    
                    if worldview_id:
                        conditions.append("worldview_id = %s")
                        params.append(worldview_id)
                    
                    if role_type:
                        conditions.append("role_type = %s")
                        params.append(role_type)
                    
                    if name:
                        conditions.append("name ILIKE %s")
                        params.append(f"%{name}%")
                    
                    where_clause = " AND ".join(conditions) if conditions else "1=1"
                    
                    # 添加分页参数
                    params.extend([limit, offset])
                    
                    cursor.execute(f"""
                        SELECT * FROM characters 
                        WHERE {where_clause}
                        ORDER BY created_at DESC
                        LIMIT %s OFFSET %s
                    """, params)
                    
                    results = cursor.fetchall()
                    characters = []
                    for result in results:
                        character_data = dict(result)
                        
                        # 调试信息：检查数据库查询的原始结果
                        logger.debug(f"数据库查询原始结果 - 所有字段: {list(character_data.keys())}")
                        logger.debug(f"数据库查询原始结果 - worldview_id: {character_data.get('worldview_id')}")
                        logger.debug(f"数据库查询原始结果 - character_id: {character_data.get('character_id')}")
                        logger.debug(f"数据库查询原始结果 - name: {character_data.get('name')}")
                        
                        # 检查是否有worldview_id字段
                        if 'worldview_id' not in character_data:
                            logger.warning("警告: 数据库查询结果中没有worldview_id字段!")
                        else:
                            logger.debug(f"worldview_id字段存在，值为: {character_data['worldview_id']}")
                        
                        # JSONB字段已经是Python对象，不需要解析
                        if character_data.get('personality_traits') is None:
                            character_data['personality_traits'] = []
                        if character_data.get('goals') is None:
                            character_data['goals'] = []
                        if character_data.get('relationships') is None:
                            character_data['relationships'] = {}
                        if character_data.get('techniques') is None:
                            character_data['techniques'] = []
                        if character_data.get('artifacts') is None:
                            character_data['artifacts'] = []
                        if character_data.get('resources') is None:
                            character_data['resources'] = {}
                        if character_data.get('stats') is None:
                            character_data['stats'] = {}
                        if character_data.get('metadata') is None:
                            character_data['metadata'] = {}
                        characters.append(character_data)
                    
                    return characters
                    
        except Exception as e:
            logger.error(f"搜索角色失败: {e}")
            raise
    
    def get_character_count(self, worldview_id: str = None) -> int:
        """获取角色数量"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    if worldview_id:
                        cursor.execute("SELECT COUNT(*) FROM characters WHERE worldview_id = %s", (worldview_id,))
                    else:
                        cursor.execute("SELECT COUNT(*) FROM characters")
                    
                    result = cursor.fetchone()
                    return result[0] if result else 0
                    
        except Exception as e:
            logger.error(f"获取角色数量失败: {e}")
            raise
    
    def get_character_role_type_stats(self, worldview_id: str = None) -> Dict[str, int]:
        """获取角色类型统计"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    if worldview_id:
                        cursor.execute("""
                            SELECT role_type, COUNT(*) 
                            FROM characters 
                            WHERE worldview_id = %s 
                            GROUP BY role_type
                        """, (worldview_id,))
                    else:
                        cursor.execute("""
                            SELECT role_type, COUNT(*) 
                            FROM characters 
                            GROUP BY role_type
                        """)
                    
                    results = cursor.fetchall()
                    return {row[0]: row[1] for row in results}
                    
        except Exception as e:
            logger.error(f"获取角色类型统计失败: {e}")
            raise


# 全局数据库实例
character_db = CharacterDatabase()
