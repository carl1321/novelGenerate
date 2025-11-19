"""
世界观数据库操作类
用于管理PostgreSQL中的世界观数据
"""
import json
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class WorldViewDatabase:
    """世界观数据库操作类"""
    
    def __init__(self):
        self.connection_string = settings.DATABASE_URL
        
    def get_connection(self):
        """获取数据库连接"""
        return psycopg2.connect(
            self.connection_string,
            cursor_factory=RealDictCursor
        )
    
    def insert_worldview(self, worldview_data: Dict[str, Any], created_by: str = "system") -> str:
        """
        插入完整的世界观数据
        
        Args:
            worldview_data: 世界观数据字典
            created_by: 创建者
            
        Returns:
            世界观ID
        """
        worldview_id = worldview_data.get('id', f"world_{hash(worldview_data.get('name', 'unknown'))}")
        
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    # 直接插入各个表，只包含prompt中定义的字段
                    # 1. 插入主表
                    cursor.execute("""
                        INSERT INTO worldviews (worldview_id, name, description, core_concept, created_by)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (
                        worldview_id,
                        worldview_data.get('name', ''),
                        worldview_data.get('description', ''),
                        worldview_data.get('core_concept', ''),
                        created_by
                    ))
                    
                    # 2. 插入力量体系
                    power_system_data = worldview_data.get('power_system', {})
                    cursor.execute("""
                        INSERT INTO power_systems (worldview_id, cultivation_realms)
                        VALUES (%s, %s)
                    """, (
                        worldview_id,
                        json.dumps(power_system_data.get('cultivation_realms', []))
                    ))
                    
                    # 3. 插入地理设定
                    geography_data = worldview_data.get('geography', {})
                    cursor.execute("""
                        INSERT INTO geographies (worldview_id, regions, main_regions, special_locations)
                        VALUES (%s, %s, %s, %s)
                    """, (
                        worldview_id,
                        json.dumps(geography_data.get('regions', [])),
                        json.dumps(geography_data.get('main_regions', [])),
                        json.dumps(geography_data.get('special_locations', []))
                    ))
                    
                    conn.commit()
                    
                    logger.info(f"成功插入世界观数据: {worldview_id}")
                    return worldview_id
                    
        except Exception as e:
            logger.error(f"插入世界观数据失败: {e}")
            raise
    
    def get_worldview(self, worldview_id: str) -> Optional[Dict[str, Any]]:
        """
        获取完整的世界观数据
        
        Args:
            worldview_id: 世界观ID
            
        Returns:
            世界观数据字典，如果不存在返回None
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    # 使用显式 JOIN 获取完整数据
                    cursor.execute("""
                        SELECT 
                            w.*,
                            ps.cultivation_realms,
                            g.regions,
                            g.main_regions,
                            g.special_locations,
                            s.organizations,
                            s.social_hierarchy,
                            hc.historical_events,
                            hc.cultural_features,
                            hc.current_conflicts
                        FROM worldviews w
                        LEFT JOIN power_systems ps ON w.worldview_id = ps.worldview_id
                        LEFT JOIN geographies g ON w.worldview_id = g.worldview_id
                        LEFT JOIN societies s ON w.worldview_id = s.worldview_id
                        LEFT JOIN history_cultures hc ON w.worldview_id = hc.worldview_id
                        WHERE w.worldview_id = %s AND w.status = 'active'
                    """, (worldview_id,))
                    
                    result = cursor.fetchone()
                    if result:
                        worldview_data = dict(result)
                        
                        # 构建前端期望的数据结构，只包含prompt中定义的字段
                        power_system = {
                            'cultivation_realms': worldview_data.get('cultivation_realms') or []
                        }
                        
                        geography = {
                            'regions': worldview_data.get('regions') or [],
                            'main_regions': worldview_data.get('main_regions') or [],
                            'special_locations': worldview_data.get('special_locations') or []
                        }
                        
                        # 返回重构的数据结构，只包含prompt中定义的字段
                        return {
                            'id': worldview_data['worldview_id'],  # 前端期望的字段名
                            'worldview_id': worldview_data['worldview_id'],
                            'name': worldview_data['name'],
                            'description': worldview_data['description'] or '',
                            'core_concept': worldview_data['core_concept'] or '',
                            'created_at': worldview_data['created_at'],
                            'updated_at': worldview_data['updated_at'],
                            'created_by': worldview_data['created_by'],
                            'version': worldview_data['version'],
                            'status': worldview_data['status'],
                            'power_system': power_system,
                            'geography': geography
                        }
                    return None
                    
        except Exception as e:
            logger.error(f"获取世界观数据失败: {e}")
            raise
    
    def get_geography(self, worldview_id: str) -> Optional[Dict[str, Any]]:
        """获取地理设定信息"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT main_regions, special_locations, regions
                        FROM geographies 
                        WHERE worldview_id = %s
                    """, (worldview_id,))
                    
                    row = cursor.fetchone()
                    if row:
                        return dict(row)
                    return None
        except Exception as e:
            logger.error(f"获取地理设定失败: {e}")
            return None
    
    def get_worldview_list(self, limit: int = 50, offset: int = 0, 
                          status: str = "active") -> List[Dict[str, Any]]:
        """
        获取世界观列表（简化版，只返回基本信息）
        
        Args:
            limit: 限制数量
            offset: 偏移量
            status: 状态过滤
            
        Returns:
            世界观列表
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    # 只查询基本信息，不查询复杂的JSONB字段
                    cursor.execute("""
                        SELECT 
                            worldview_id,
                            name,
                            description,
                            core_concept,
                            created_at,
                            updated_at,
                            created_by,
                            version,
                            status
                        FROM worldviews 
                        WHERE status = %s
                        ORDER BY created_at DESC
                        LIMIT %s OFFSET %s
                    """, (status, limit, offset))
                    
                    results = cursor.fetchall()
                    worldviews = []
                    for row in results:
                        if isinstance(row, dict):
                            # 如果返回的是字典
                            worldview_data = {
                                'worldview_id': row.get('worldview_id'),
                                'name': row.get('name'),
                                'description': row.get('description'),
                                'core_concept': row.get('core_concept'),
                                'created_at': row.get('created_at').isoformat() if row.get('created_at') else None,
                                'updated_at': row.get('updated_at').isoformat() if row.get('updated_at') else None,
                                'created_by': row.get('created_by'),
                                'version': row.get('version'),
                                'status': row.get('status')
                            }
                        else:
                            # 如果返回的是元组
                            worldview_data = {
                                'worldview_id': row[0],
                                'name': row[1],
                                'description': row[2],
                                'core_concept': row[3],
                                'created_at': row[4].isoformat() if row[4] else None,
                                'updated_at': row[5].isoformat() if row[5] else None,
                                'created_by': row[6],
                                'version': row[7],
                                'status': row[8]
                            }
                        worldviews.append(worldview_data)
                    
                    return worldviews
                    
        except Exception as e:
            logger.error(f"获取世界观列表失败: {e}")
            raise
    
    def update_worldview(self, worldview_id: str, worldview_data: Dict[str, Any]) -> bool:
        """
        更新世界观数据
        
        Args:
            worldview_id: 世界观ID
            worldview_data: 更新的数据
            
        Returns:
            是否更新成功
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    # 直接更新各个子表，避免存储过程参数不匹配问题
                    # 1. 更新主表
                    cursor.execute("""
                        UPDATE worldviews 
                        SET name = %s, description = %s, core_concept = %s, updated_at = NOW()
                        WHERE worldview_id = %s
                    """, (
                        worldview_data.get('name'),
                        worldview_data.get('description'), 
                        worldview_data.get('core_concept'),
                        worldview_id
                    ))
                    
                    # 2. 更新或插入力量体系
                    power_system_data = worldview_data.get('power_system', {})
                    # 确保 power_system_data 是字典类型
                    if isinstance(power_system_data, str):
                        try:
                            power_system_data = json.loads(power_system_data)
                        except json.JSONDecodeError:
                            logger.warning(f"power_system 数据不是有效的JSON: {power_system_data}")
                            power_system_data = {}
                    elif not isinstance(power_system_data, dict):
                        logger.warning(f"power_system 数据类型错误: {type(power_system_data)}")
                        power_system_data = {}
                    
                    cursor.execute("""
                        INSERT INTO power_systems (worldview_id, cultivation_realms)
                        VALUES (%s, %s)
                        ON CONFLICT (worldview_id) 
                        DO UPDATE SET 
                            cultivation_realms = EXCLUDED.cultivation_realms,
                            updated_at = NOW()
                    """, (
                        worldview_id,
                        json.dumps(power_system_data.get('cultivation_realms', []))
                    ))
                    
                    # 3. 更新或插入地理设定
                    geography_data = worldview_data.get('geography', {})
                    # 确保 geography_data 是字典类型
                    if isinstance(geography_data, str):
                        try:
                            geography_data = json.loads(geography_data)
                        except json.JSONDecodeError:
                            logger.warning(f"geography 数据不是有效的JSON: {geography_data}")
                            geography_data = {}
                    elif not isinstance(geography_data, dict):
                        logger.warning(f"geography 数据类型错误: {type(geography_data)}")
                        geography_data = {}
                    
                    cursor.execute("""
                        INSERT INTO geographies (worldview_id, regions, main_regions, special_locations)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (worldview_id) 
                        DO UPDATE SET 
                            regions = EXCLUDED.regions,
                            main_regions = EXCLUDED.main_regions,
                            special_locations = EXCLUDED.special_locations,
                            updated_at = NOW()
                    """, (
                        worldview_id,
                        json.dumps(geography_data.get('regions', [])),
                        json.dumps(geography_data.get('main_regions', [])),
                        json.dumps(geography_data.get('special_locations', []))
                    ))
                    
                    conn.commit()
                    
                    logger.info(f"成功更新世界观数据: {worldview_id}")
                    return True  # 存储过程总是返回True
                    
        except Exception as e:
            logger.error(f"更新世界观数据失败: {e}")
            raise
    
    def delete_worldview(self, worldview_id: str, soft_delete: bool = True) -> bool:
        """
        删除世界观数据
        
        Args:
            worldview_id: 世界观ID
            soft_delete: 是否软删除（只标记状态）
            
        Returns:
            是否删除成功
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    if soft_delete:
                        cursor.execute("""
                            UPDATE worldviews 
                            SET status = 'deleted' 
                            WHERE worldview_id = %s
                        """, (worldview_id,))
                    else:
                        cursor.execute("""
                            DELETE FROM worldviews 
                            WHERE worldview_id = %s
                        """, (worldview_id,))
                    
                    conn.commit()
                    
                    logger.info(f"成功删除世界观数据: {worldview_id}")
                    return True
                    
        except Exception as e:
            logger.error(f"删除世界观数据失败: {e}")
            raise
    
    def search_worldviews(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        搜索世界观
        
        Args:
            query: 搜索关键词
            limit: 限制数量
            
        Returns:
            搜索结果列表
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT worldview_id, name, description, core_concept, 
                               created_at, updated_at, created_by, version, status
                        FROM worldviews 
                        WHERE status = 'active' 
                        AND (
                            name ILIKE %s OR 
                            description ILIKE %s OR 
                            core_concept ILIKE %s
                        )
                        ORDER BY created_at DESC
                        LIMIT %s
                    """, (f'%{query}%', f'%{query}%', f'%{query}%', limit))
                    
                    results = cursor.fetchall()
                    return [dict(row) for row in results]
                    
        except Exception as e:
            logger.error(f"搜索世界观失败: {e}")
            raise
    
    def get_worldview_statistics(self) -> Dict[str, Any]:
        """
        获取世界观统计信息
        
        Returns:
            统计信息字典
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    # 总数统计
                    cursor.execute("""
                        SELECT 
                            COUNT(*) as total,
                            COUNT(CASE WHEN status = 'active' THEN 1 END) as active,
                            COUNT(CASE WHEN status = 'archived' THEN 1 END) as archived,
                            COUNT(CASE WHEN status = 'deleted' THEN 1 END) as deleted
                        FROM worldviews
                    """)
                    
                    stats = dict(cursor.fetchone())
                    
                    # 最近创建统计
                    cursor.execute("""
                        SELECT COUNT(*) as recent_count
                        FROM worldviews 
                        WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'
                        AND status = 'active'
                    """)
                    
                    recent_stats = dict(cursor.fetchone())
                    stats.update(recent_stats)
                    
                    return stats
                    
        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            raise
    
    def get_worldview_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        根据名称获取世界观
        
        Args:
            name: 世界观名称
            
        Returns:
            世界观数据字典，如果不存在返回None
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT * FROM worldview_complete 
                        WHERE name = %s AND status = 'active'
                    """, (name,))
                    
                    result = cursor.fetchone()
                    if result:
                        return dict(result)
                    return None
                    
        except Exception as e:
            logger.error(f"根据名称获取世界观失败: {e}")
            raise
    
    def backup_worldview(self, worldview_id: str) -> bool:
        """
        备份世界观数据到元数据表
        
        Args:
            worldview_id: 世界观ID
            
        Returns:
            是否备份成功
        """
        try:
            worldview_data = self.get_worldview(worldview_id)
            if not worldview_data:
                return False
            
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO worldview_metadata (worldview_id, metadata_key, metadata_value)
                        VALUES (%s, 'backup', %s)
                        ON CONFLICT (worldview_id, metadata_key) 
                        DO UPDATE SET metadata_value = %s
                    """, (
                        worldview_id, 
                        json.dumps(worldview_data, default=str),
                        json.dumps(worldview_data, default=str)
                    ))
                    
                    conn.commit()
                    
                    logger.info(f"成功备份世界观数据: {worldview_id}")
                    return True
                    
        except Exception as e:
            logger.error(f"备份世界观数据失败: {e}")
            raise


# 创建全局实例
worldview_db = WorldViewDatabase()
