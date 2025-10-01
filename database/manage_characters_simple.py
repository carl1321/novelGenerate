#!/usr/bin/env python3
"""
角色数据库管理脚本（简化版）
"""
import psycopg2
import json
from typing import List, Dict, Any, Optional
import os
from datetime import datetime

class CharacterDatabaseManager:
    """角色数据库管理器（简化版）"""
    
    def __init__(self, connection_string: str = None):
        if connection_string:
            self.connection_string = connection_string
        else:
            # 从环境变量获取连接信息
            self.connection_string = os.getenv(
                'DATABASE_URL', 
                'postgresql://postgres:password@localhost:5432/novel_generate'
            )
    
    def connect(self):
        """连接数据库"""
        return psycopg2.connect(self.connection_string)
    
    def create_character(self, character_data: Dict[str, Any]) -> str:
        """创建单个角色"""
        with self.connect() as conn:
            with conn.cursor() as cur:
                character_id = f"char_{int(datetime.now().timestamp())}_{hash(character_data['name']) % 10000}"
                
                cur.execute("""
                    INSERT INTO characters (
                        character_id, worldview_id, name, age, gender, role_type,
                        cultivation_level, element_type, background, current_location,
                        organization_id, personality_traits, goals, relationships,
                        techniques, artifacts, resources, stats, metadata, created_by
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    ) RETURNING character_id
                """, (
                    character_id,
                    character_data.get('worldview_id'),
                    character_data.get('name'),
                    character_data.get('age'),
                    character_data.get('gender'),
                    character_data.get('role_type', '配角'),
                    character_data.get('cultivation_level'),
                    character_data.get('element_type'),
                    character_data.get('background'),
                    character_data.get('current_location'),
                    character_data.get('organization_id'),
                    json.dumps(character_data.get('personality_traits', [])),
                    json.dumps(character_data.get('goals', [])),
                    json.dumps(character_data.get('relationships', {})),
                    json.dumps(character_data.get('techniques', [])),
                    json.dumps(character_data.get('artifacts', [])),
                    json.dumps(character_data.get('resources', {})),
                    json.dumps(character_data.get('stats', {})),
                    json.dumps(character_data.get('metadata', {})),
                    character_data.get('created_by', 'system')
                ))
                
                return cur.fetchone()[0]
    
    def create_characters_batch(self, worldview_id: str, characters_data: List[Dict[str, Any]], created_by: str = 'system') -> List[str]:
        """批量创建角色"""
        with self.connect() as conn:
            with conn.cursor() as cur:
                # 调用存储过程
                cur.execute("""
                    SELECT create_characters_batch_simple(%s, %s, %s)
                """, (worldview_id, json.dumps(characters_data), created_by))
                
                result = cur.fetchone()[0]
                return [char['character_id'] for char in result]
    
    def get_character(self, character_id: str) -> Optional[Dict[str, Any]]:
        """获取单个角色"""
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT * FROM character_complete WHERE character_id = %s
                """, (character_id,))
                
                row = cur.fetchone()
                if row:
                    columns = [desc[0] for desc in cur.description]
                    character = dict(zip(columns, row))
                    
                    # 解析JSONB字段
                    jsonb_fields = ['personality_traits', 'goals', 'relationships', 
                                  'techniques', 'artifacts', 'resources', 'stats', 'metadata']
                    for field in jsonb_fields:
                        if character.get(field):
                            character[field] = json.loads(character[field])
                    
                    return character
                return None
    
    def get_characters_by_worldview(self, worldview_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """获取世界观下的所有角色"""
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT * FROM character_complete 
                    WHERE worldview_id = %s AND status = 'active'
                    ORDER BY created_at DESC
                    LIMIT %s
                """, (worldview_id, limit))
                
                rows = cur.fetchall()
                columns = [desc[0] for desc in cur.description]
                characters = []
                
                for row in rows:
                    character = dict(zip(columns, row))
                    
                    # 解析JSONB字段
                    jsonb_fields = ['personality_traits', 'goals', 'relationships', 
                                  'techniques', 'artifacts', 'resources', 'stats', 'metadata']
                    for field in jsonb_fields:
                        if character.get(field):
                            character[field] = json.loads(character[field])
                    
                    characters.append(character)
                
                return characters
    
    def search_characters(self, worldview_id: str, keyword: str = None, role_type: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """搜索角色"""
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT search_characters_simple(%s, %s, %s, %s)
                """, (worldview_id, keyword, role_type, limit))
                
                result = cur.fetchone()[0]
                return json.loads(result) if result else []
    
    def get_character_stats(self, worldview_id: str) -> Dict[str, int]:
        """获取角色统计信息"""
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT get_character_stats_by_type_simple(%s)
                """, (worldview_id,))
                
                result = cur.fetchone()[0]
                return json.loads(result) if result else {}
    
    def update_character(self, character_id: str, updates: Dict[str, Any]) -> bool:
        """更新角色信息"""
        with self.connect() as conn:
            with conn.cursor() as cur:
                # 构建更新语句
                set_clauses = []
                values = []
                
                for key, value in updates.items():
                    if key in ['personality_traits', 'goals', 'relationships', 
                              'techniques', 'artifacts', 'resources', 'stats', 'metadata']:
                        set_clauses.append(f"{key} = %s")
                        values.append(json.dumps(value))
                    else:
                        set_clauses.append(f"{key} = %s")
                        values.append(value)
                
                if not set_clauses:
                    return False
                
                set_clauses.append("updated_at = CURRENT_TIMESTAMP")
                values.append(character_id)
                
                cur.execute(f"""
                    UPDATE characters 
                    SET {', '.join(set_clauses)}
                    WHERE character_id = %s
                """, values)
                
                return cur.rowcount > 0
    
    def delete_character(self, character_id: str) -> bool:
        """删除角色（软删除）"""
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE characters 
                    SET status = 'deleted', updated_at = CURRENT_TIMESTAMP
                    WHERE character_id = %s
                """, (character_id,))
                
                return cur.rowcount > 0
    
    def create_character_group(self, group_data: Dict[str, Any]) -> str:
        """创建角色组"""
        with self.connect() as conn:
            with conn.cursor() as cur:
                group_id = f"group_{int(datetime.now().timestamp())}_{hash(group_data['group_name']) % 10000}"
                
                cur.execute("""
                    INSERT INTO character_groups (
                        group_id, group_name, group_description, group_type,
                        worldview_id, character_ids, common_goals, 
                        internal_conflicts, external_enemies, created_by
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    ) RETURNING group_id
                """, (
                    group_id,
                    group_data.get('group_name'),
                    group_data.get('group_description'),
                    group_data.get('group_type', 'custom'),
                    group_data.get('worldview_id'),
                    json.dumps(group_data.get('character_ids', [])),
                    json.dumps(group_data.get('common_goals', [])),
                    json.dumps(group_data.get('internal_conflicts', [])),
                    json.dumps(group_data.get('external_enemies', [])),
                    group_data.get('created_by', 'system')
                ))
                
                return cur.fetchone()[0]

def main():
    """测试函数"""
    manager = CharacterDatabaseManager()
    
    # 测试创建角色
    test_character = {
        'worldview_id': 'test_world_001',
        'name': '测试角色',
        'age': 25,
        'gender': '男',
        'role_type': '主角',
        'cultivation_level': '筑基',
        'element_type': '火',
        'background': '一个年轻的修仙者',
        'personality_traits': [{'trait': '勇敢', 'intensity': 8}],
        'goals': [{'type': '短期目标', 'description': '突破到金丹期'}],
        'relationships': {'master': '师父张三'},
        'techniques': [{'name': '火球术', 'level': 3, 'type': '攻击技能'}],
        'artifacts': [],
        'resources': {'灵石': 100},
        'stats': {'攻击力': 80, '防御力': 60},
        'metadata': {'appearance': '英俊潇洒'}
    }
    
    try:
        character_id = manager.create_character(test_character)
        print(f"创建角色成功: {character_id}")
        
        # 获取角色
        character = manager.get_character(character_id)
        print(f"获取角色: {character['name']}")
        
        # 获取统计信息
        stats = manager.get_character_stats('test_world_001')
        print(f"角色统计: {stats}")
        
    except Exception as e:
        print(f"测试失败: {e}")

if __name__ == "__main__":
    main()
