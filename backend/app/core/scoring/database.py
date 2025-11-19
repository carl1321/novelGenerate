"""
评分智能体数据库操作
"""
from typing import List, Optional, Dict, Any, Tuple
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from uuid import uuid4

from app.core.scoring.models import (
    ScoringRecord, ScoringDimension, DimensionMapping, 
    ScoringResult, ScoringType, ScoringLevel
)
from app.utils.database import get_database_url
import logging

logger = logging.getLogger(__name__)


class ScoringDatabase:
    """评分智能体数据库操作类"""
    
    def __init__(self):
        self.connection_string = get_database_url()
    
    def get_connection(self):
        """获取数据库连接"""
        return psycopg2.connect(
            self.connection_string,
            cursor_factory=RealDictCursor
        )
    
    def create_scoring_record(self, scoring_record: ScoringRecord, dimensions: List[ScoringDimension]) -> bool:
        """创建评分记录"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    # 插入评分记录
                    cursor.execute("""
                        INSERT INTO scoring_records 
                        (id, detailed_plot_id, scorer_id, scoring_type, total_score, 
                         scoring_level, overall_feedback, improvement_suggestions, created_at, updated_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        scoring_record.id,
                        scoring_record.detailed_plot_id,
                        scoring_record.scorer_id,
                        scoring_record.scoring_type.value,
                        scoring_record.total_score,
                        scoring_record.scoring_level.value,
                        scoring_record.overall_feedback,
                        scoring_record.improvement_suggestions,
                        datetime.now(),
                        datetime.now()
                    ))
                    
                    # 插入各维度详情
                    for dimension in dimensions:
                        cursor.execute("""
                            INSERT INTO scoring_dimensions 
                            (id, scoring_record_id, dimension_name, dimension_display_name, 
                             score, feedback, weight, created_at, updated_at)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, (
                            dimension.id,
                            dimension.scoring_record_id,
                            dimension.dimension_name,
                            dimension.dimension_display_name,
                            dimension.score,
                            dimension.feedback,
                            dimension.weight,
                            datetime.now(),
                            datetime.now()
                        ))
                    
                    conn.commit()
                    logger.info(f"创建评分记录成功: {scoring_record.id}")
                    return True
                    
        except Exception as e:
            logger.error(f"创建评分记录失败: {str(e)}")
            return False
    
    def get_scoring_by_detailed_plot_id(self, detailed_plot_id: str) -> List[ScoringResult]:
        """根据详细剧情ID获取评分记录"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    # 获取评分记录
                    cursor.execute("""
                        SELECT sr.* FROM scoring_records sr
                        WHERE sr.detailed_plot_id = %s
                        ORDER BY sr.created_at DESC
                    """, (detailed_plot_id,))
                    
                    scoring_records = []
                    for row in cursor.fetchall():
                        scoring_records.append(ScoringRecord(
                            id=row['id'],
                            detailed_plot_id=row['detailed_plot_id'],
                            scorer_id=row['scorer_id'],
                            scoring_type=ScoringType(row['scoring_type']),
                            total_score=float(row['total_score']),
                            scoring_level=ScoringLevel(row['scoring_level']),
                            overall_feedback=row['overall_feedback'],
                            improvement_suggestions=row['improvement_suggestions'] if row['improvement_suggestions'] else [],
                            created_at=row['created_at'],
                            updated_at=row['updated_at']
                        ))
                    
                    # 获取各维度详情
                    scoring_results = []
                    for scoring_record in scoring_records:
                        cursor.execute("""
                            SELECT sd.* FROM scoring_dimensions sd
                            WHERE sd.scoring_record_id = %s
                            ORDER BY sd.dimension_name
                        """, (scoring_record.id,))
                        
                        dimensions = []
                        for dim_row in cursor.fetchall():
                            dimensions.append(ScoringDimension(
                                id=dim_row['id'],
                                scoring_record_id=dim_row['scoring_record_id'],
                                dimension_name=dim_row['dimension_name'],
                                dimension_display_name=dim_row['dimension_display_name'],
                                score=float(dim_row['score']),
                                feedback=dim_row['feedback'],
                                weight=float(dim_row['weight']),
                                created_at=dim_row['created_at'],
                                updated_at=dim_row['updated_at']
                            ))
                        
                        scoring_results.append(ScoringResult(
                            scoring_record=scoring_record,
                            dimensions=dimensions
                        ))
                    
                    return scoring_results
                        
        except Exception as e:
            logger.error(f"获取评分记录失败: {detailed_plot_id}, 错误: {str(e)}")
            return []
    
    def get_latest_scoring_by_detailed_plot_id(self, detailed_plot_id: str) -> Optional[ScoringResult]:
        """获取详细剧情的最新评分记录"""
        try:
            scoring_results = self.get_scoring_by_detailed_plot_id(detailed_plot_id)
            return scoring_results[0] if scoring_results else None
        except Exception as e:
            logger.error(f"获取最新评分记录失败: {detailed_plot_id}, 错误: {str(e)}")
            return None
    
    def get_dimension_mappings(self) -> List[DimensionMapping]:
        """获取所有维度映射配置"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT id, technical_name, display_name, description, 
                               color_code, weight, is_active, created_at, updated_at
                        FROM dimension_mappings
                        WHERE is_active = TRUE
                        ORDER BY technical_name
                    """)
                    
                    mappings = []
                    for row in cursor.fetchall():
                        mappings.append(DimensionMapping(
                            id=row[0],
                            technical_name=row[1],
                            display_name=row[2],
                            description=row[3],
                            color_code=row[4],
                            weight=float(row[5]),
                            is_active=bool(row[6]),
                            created_at=row[7],
                            updated_at=row[8]
                        ))
                    
                    return mappings
                    
        except Exception as e:
            logger.error(f"获取维度映射失败: {str(e)}")
            return self._get_default_dimension_mappings()
    
    def _get_default_dimension_mappings(self) -> List[DimensionMapping]:
        """获取默认维度映射（备用）"""
        return [
            DimensionMapping(
                id=f"dim_{name}",
                technical_name=name,
                display_name=display_name,
                color_code=color_code,
                weight=weight
            )
            for name, display_name, color_code, weight in [
                ("logic_consistency", "逻辑自洽性", "#1890ff", 0.25),
                ("dramatic_conflict", "戏剧冲突性", "#52c41a", 0.20),
                ("character_development", "角色发展性", "#fa8c16", 0.20),
                ("world_usage", "世界观运用", "#722ed1", 0.15),
                ("writing_style", "文笔风格", "#eb2f96", 0.20),
                ("dramatic_tension", "戏剧张力", "#1890ff", 0.10),
                ("emotional_impact", "情感冲击", "#52c41a", 0.10),
                ("thematic_depth", "主题深度", "#722ed1", 0.10),
                ("pacing_fluency", "节奏流畅度", "#eb2f96", 0.10),
                ("originality_creativity", "创新性", "#fa8c16", 0.10)
            ]
        ]
    
    def delete_scoring_records_by_plot_id(self, detailed_plot_id: str) -> int:
        """删除指定详细剧情的所有评分记录"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    # 由于外键约束，删除scoring_records会自动删除关联的scoring_dimensions
                    cursor.execute("""
                        DELETE FROM scoring_records WHERE detailed_plot_id = %s
                    """, (detailed_plot_id,))
                    
                    deleted_count = cursor.rowcount
                    conn.commit()
                    logger.info(f"删除评分记录: {detailed_plot_id}, 删除数量: {deleted_count}")
                    return deleted_count
                    
        except Exception as e:
            logger.error(f"删除评分记录失败: {detailed_plot_id}, 错误: {str(e)}")
            return 0
    
    def get_scoring_statistics(self, detailed_plot_id: str) -> Dict[str, Any]:
        """获取评分统计信息"""
        try:
            scoring_records = self.get_scoring_by_detailed_plot_id(detailed_plot_id)
            
            if not scoring_records:
                return {"total_count": 0, "latest_score": None}
            
            # 计算统计信息
            latest_scoring = scoring_records[0]
            scores = [sr.scoring_record.total_score for sr in scoring_records]
            
            return {
                "total_count": len(scoring_records),
                "latest_score": latest_scoring.scoring_record.total_score,
                "latest_level": latest_scoring.scoring_record.scoring_level.value,
                "average_score": sum(scores) / len(scores) if scores else 0,
                "highest_score": max(scores) if scores else 0,
                "lowest_score": min(scores) if scores else 0,
                "latest_dimensions": [
                    {
                        "dimension_name": dim.dimension_name,
                        "dimension_display_name": dim.dimension_display_name,
                        "score": dim.score,
                        "feedback": dim.feedback
                    }
                    for dim in latest_scoring.dimensions
                ]
            }
            
        except Exception as e:
            logger.error(f"获取评分统计失败: {detailed_plot_id}, 错误: {str(e)}")
            return {"total_count": 0, "latest_score": None}
