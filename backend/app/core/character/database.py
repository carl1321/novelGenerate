"""
角色数据库管理器
"""
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Dict, List, Any, Optional
import json
import logging

logger = logging.getLogger(__name__)


class CharacterDatabase:
    """角色数据库管理器"""
    
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
        """插入角色数据（简化版）"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    # 直接插入到characters表（简化版）
                    cursor.execute("""
                        INSERT INTO characters (
                            character_id, worldview_id, name, age, gender, role_type,
                            cultivation_level, element_type, background, current_location,
                            organization_id, personality_traits, main_goals, short_term_goals,
                            techniques, weaknesses, appearance, turning_point, relationship_text, values, metadata, created_by
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                        ) RETURNING character_id
                    """, (
                        character_data.get("character_id") or character_data.get("id"),
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
                        character_data.get("personality_traits", ""),
                        character_data.get("main_goals", ""),
                        character_data.get("short_term_goals", ""),
                        json.dumps(character_data.get("techniques", [])),
                        character_data.get("weaknesses", ""),
                        character_data.get("appearance", ""),
                        character_data.get("turning_point", ""),
                        character_data.get("relationship_text", ""),
                        character_data.get("values", ""),
                        json.dumps(character_data.get("metadata", {})),
                        created_by
                    ))
                    
                    result = cursor.fetchone()
                    conn.commit()
                    
                    if result:
                        return result[0]  # 返回character_id
                    else:
                        raise Exception("插入角色失败")
                        
        except Exception as e:
            logger.error(f"插入角色失败: {e}")
            raise
    
    def get_character(self, character_id: str) -> Optional[Dict[str, Any]]:
        """获取角色信息"""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute("""
                        SELECT * FROM characters 
                        WHERE character_id = %s AND status = 'active'
                    """, (character_id,))
                    
                    result = cursor.fetchone()
                    if result:
                        return dict(result)
                    return None
                    
        except Exception as e:
            logger.error(f"获取角色失败: {e}")
            return None
    
    def get_characters_by_worldview(self, worldview_id: str, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """获取世界观下的角色列表"""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute("""
                        SELECT * FROM characters 
                        WHERE worldview_id = %s AND status = 'active'
                        ORDER BY created_at DESC
                        LIMIT %s OFFSET %s
                    """, (worldview_id, limit, offset))
                    
                    results = cursor.fetchall()
                    return [dict(row) for row in results]
                    
        except Exception as e:
            logger.error(f"获取角色列表失败: {e}")
            return []
    
    def search_characters(self, keyword: str, worldview_id: str = None, 
                         role_type: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """搜索角色"""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    # 构建查询条件
                    conditions = ["status = 'active'"]
                    params = []
                    
                    if keyword:
                        conditions.append("(name ILIKE %s OR background ILIKE %s)")
                        params.extend([f"%{keyword}%", f"%{keyword}%"])
                    
                    if worldview_id:
                        conditions.append("worldview_id = %s")
                        params.append(worldview_id)
                    
                    if role_type:
                        conditions.append("role_type = %s")
                        params.append(role_type)
                    
                    where_clause = " AND ".join(conditions)
                    params.extend([limit])
                    
                    query = f"""
                        SELECT * FROM characters 
                        WHERE {where_clause}
                        ORDER BY created_at DESC
                        LIMIT %s
                    """
                    cursor.execute(query, params)
                    
                    results = cursor.fetchall()
                    return [dict(row) for row in results]
                    
        except Exception as e:
            logger.error(f"搜索角色失败: {e}")
            return []
    
    def update_character(self, character_id: str, updates: Dict[str, Any]) -> bool:
        """更新角色信息"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    # 更新所有字段（包括主字段和JSONB字段）
                    main_fields = ["name", "age", "gender", "role_type", "cultivation_level", 
                                 "element_type", "background", "current_location", "organization_id"]
                    text_fields = ["personality_traits", "main_goals", "short_term_goals", 
                                 "weaknesses", "appearance", "turning_point", "relationship_text", "values"]
                    jsonb_fields = ["techniques", "metadata"]
                    
                    update_fields = []
                    params = []
                    
                    # 处理主字段
                    for field in main_fields:
                        if field in updates:
                            update_fields.append(f"{field} = %s")
                            params.append(updates[field])
                    
                    # 处理文本字段
                    for field in text_fields:
                        if field in updates:
                            update_fields.append(f"{field} = %s")
                            params.append(updates[field])
                    
                    # 处理JSONB字段
                    for field in jsonb_fields:
                        if field in updates:
                            update_fields.append(f"{field} = %s")
                            params.append(json.dumps(updates[field]))
                    
                    if update_fields:
                        params.append(character_id)
                        cursor.execute(f"""
                            UPDATE characters 
                            SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP
                            WHERE character_id = %s
                        """, params)
                    
                    conn.commit()
                    return True
                    
        except Exception as e:
            logger.error(f"更新角色失败: {e}")
            return False
    
    def delete_character(self, character_id: str) -> bool:
        """删除角色（软删除）"""
        try:
            logger.info(f"尝试删除角色ID: {character_id}")
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        UPDATE characters 
                        SET status = 'deleted', updated_at = CURRENT_TIMESTAMP
                        WHERE character_id = %s
                    """, (character_id,))
                    
                    conn.commit()
                    logger.info(f"删除操作影响行数: {cursor.rowcount}")
                    return cursor.rowcount > 0
                    
        except Exception as e:
            logger.error(f"删除角色失败: {e}")
            logger.error(f"删除角色数据库错误: {e}")
            return False
    
    def get_character_stats(self, worldview_id: str = None) -> Dict[str, Any]:
        """获取角色统计信息"""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    # 基础统计
                    base_query = "SELECT COUNT(*) as total FROM characters WHERE status = 'active'"
                    params = []
                    
                    if worldview_id:
                        base_query += " AND worldview_id = %s"
                        params.append(worldview_id)
                    
                    cursor.execute(base_query, params)
                    total = cursor.fetchone()["total"]
                    
                    # 按角色类型统计
                    type_query = """
                        SELECT role_type, COUNT(*) as count 
                        FROM characters 
                        WHERE status = 'active'
                    """
                    if worldview_id:
                        type_query += " AND worldview_id = %s"
                        params.append(worldview_id)
                    type_query += " GROUP BY role_type"
                    
                    cursor.execute(type_query, params)
                    role_type_stats = {row["role_type"]: row["count"] for row in cursor.fetchall()}
                    
                    # 按修炼境界统计
                    level_query = """
                        SELECT cultivation_level, COUNT(*) as count 
                        FROM characters 
                        WHERE status = 'active' AND cultivation_level IS NOT NULL
                    """
                    if worldview_id:
                        level_query += " AND worldview_id = %s"
                        params.append(worldview_id)
                    level_query += " GROUP BY cultivation_level"
                    
                    cursor.execute(level_query, params)
                    level_stats = {row["cultivation_level"]: row["count"] for row in cursor.fetchall()}
                    
                    return {
                        "total": total,
                        "role_type_stats": role_type_stats,
                        "cultivation_level_stats": level_stats
                    }
                    
        except Exception as e:
            logger.error(f"获取角色统计失败: {e}")
            return {"total": 0, "role_type_stats": {}, "cultivation_level_stats": {}}


# 创建全局实例
character_db = CharacterDatabase()
