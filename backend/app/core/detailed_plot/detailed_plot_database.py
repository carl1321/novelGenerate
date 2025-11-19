"""
详细剧情数据库操作
"""
import psycopg2
import json
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from app.core.config import settings
from app.core.detailed_plot.detailed_plot_models import DetailedPlot, DetailedPlotStatus, ScoringStatus
from app.core.logic.models import LogicCheckResult, LogicStatus
from app.utils.logger import debug_log, error_log


class DetailedPlotDatabase:
    """详细剧情数据库操作类"""
    
    def __init__(self):
        self.connection_string = settings.DATABASE_URL
    
    def get_connection(self):
        """获取数据库连接"""
        return psycopg2.connect(self.connection_string)
    
    def save_detailed_plot(self, detailed_plot: DetailedPlot) -> bool:
        """保存详细剧情"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO detailed_plots (
                            id, chapter_outline_id, plot_outline_id, title, 
                            content, word_count, status, created_at, updated_at
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s
                        )
                        ON CONFLICT (id) DO UPDATE SET
                            title = EXCLUDED.title,
                            content = EXCLUDED.content,
                            word_count = EXCLUDED.word_count,
                            status = EXCLUDED.status,
                            updated_at = EXCLUDED.updated_at
                    """, (
                        detailed_plot.id,
                        detailed_plot.chapter_outline_id,
                        detailed_plot.plot_outline_id,
                        detailed_plot.title,
                        detailed_plot.content,
                        detailed_plot.word_count,
                        detailed_plot.status.value,
                        detailed_plot.created_at or datetime.now(),
                        detailed_plot.updated_at or datetime.now()
                    ))
                    conn.commit()
                    return True
        except Exception as e:
            error_log("保存详细剧情失败", e)
            return False
    
    def get_detailed_plot_by_id(self, detailed_plot_id: str) -> Optional[DetailedPlot]:
        """根据ID获取详细剧情（优先返回最新版本）"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    # 使用视图获取最新版本
                    cursor.execute("""
                        SELECT 
                            original_id, chapter_outline_id, plot_outline_id, status,
                            logic_status, logic_check_result, scoring_status, total_score,
                            scoring_result, scoring_feedback, scored_at, scored_by,
                            original_created_at, original_updated_at,
                            original_title, original_content, original_word_count,
                            current_version_id, current_version_type, current_version_number,
                            current_title, current_content, current_word_count,
                            current_source_table, current_source_record_id, current_version_notes,
                            current_created_by, current_created_at, current_updated_at,
                            has_version_record
                        FROM detailed_plots_with_latest_version 
                        WHERE original_id = %s
                    """, (detailed_plot_id,))
                    
                    row = cursor.fetchone()
                    if row:
                        return self._row_to_detailed_plot_with_version(row)
                    return None
        except Exception as e:
            error_log("获取详细剧情失败", e)
            return None
    
    def get_detailed_plots_by_chapter_outline(self, chapter_outline_id: str) -> List[DetailedPlot]:
        """根据章节大纲ID获取详细剧情列表（优先返回最新版本）"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    # 使用视图获取最新版本
                    cursor.execute("""
                        SELECT 
                            original_id, chapter_outline_id, plot_outline_id, status,
                            logic_status, logic_check_result, scoring_status, total_score,
                            scoring_result, scoring_feedback, scored_at, scored_by,
                            original_created_at, original_updated_at,
                            original_title, original_content, original_word_count,
                            current_version_id, current_version_type, current_version_number,
                            current_title, current_content, current_word_count,
                            current_source_table, current_source_record_id, current_version_notes,
                            current_created_by, current_created_at, current_updated_at,
                            has_version_record
                        FROM detailed_plots_with_latest_version 
                        WHERE chapter_outline_id = %s
                        ORDER BY original_created_at DESC
                    """, (chapter_outline_id,))
                    
                    rows = cursor.fetchall()
                    return [self._row_to_detailed_plot_with_version(row) for row in rows]
        except Exception as e:
            error_log("获取详细剧情列表失败", e)
            return []
    
    def get_detailed_plots_by_plot_outline(self, plot_outline_id: str, 
                                          page: int = 1, page_size: int = 20) -> tuple[List[DetailedPlot], int]:
        """根据剧情大纲ID获取详细剧情列表（分页，优先返回最新版本）"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    # 获取总数
                    cursor.execute("""
                        SELECT COUNT(*) FROM detailed_plots_with_latest_version 
                        WHERE plot_outline_id = %s
                    """, (plot_outline_id,))
                    total = cursor.fetchone()[0]
                    
                    # 获取分页数据
                    offset = (page - 1) * page_size
                    cursor.execute("""
                        SELECT 
                            original_id, chapter_outline_id, plot_outline_id, status,
                            logic_status, logic_check_result, scoring_status, total_score,
                            scoring_result, scoring_feedback, scored_at, scored_by,
                            original_created_at, original_updated_at,
                            original_title, original_content, original_word_count,
                            current_version_id, current_version_type, current_version_number,
                            current_title, current_content, current_word_count,
                            current_source_table, current_source_record_id, current_version_notes,
                            current_created_by, current_created_at, current_updated_at,
                            has_version_record
                        FROM detailed_plots_with_latest_version 
                        WHERE plot_outline_id = %s
                        ORDER BY original_created_at DESC
                        LIMIT %s OFFSET %s
                    """, (plot_outline_id, page_size, offset))
                    
                    rows = cursor.fetchall()
                    detailed_plots = [self._row_to_detailed_plot_with_version(row) for row in rows]
                    return detailed_plots, total
        except Exception as e:
            error_log("获取详细剧情列表失败", e)
            return [], 0
    
    def delete_correction_history(self, detailed_plot_id: str) -> int:
        """删除指定详细剧情的所有修正记录"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        DELETE FROM correction_history WHERE detailed_plot_id = %s
                    """, (detailed_plot_id,))
                    conn.commit()
                    deleted_count = cursor.rowcount
                    debug_log("删除修正记录", f"ID: {detailed_plot_id}, 删除数量: {deleted_count}")
                    return deleted_count
        except Exception as e:
            error_log("删除修正记录失败", f"ID: {detailed_plot_id}, 错误: {str(e)}")
            return 0

    def delete_detailed_plot(self, detailed_plot_id: str) -> bool:
        """删除详细剧情及其相关记录"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    # 首先删除相关的修正记录
                    correction_deleted = self.delete_correction_history(detailed_plot_id)
                    
                    # 然后删除详细剧情
                    cursor.execute("""
                        DELETE FROM detailed_plots WHERE id = %s
                    """, (detailed_plot_id,))
                    conn.commit()
                    
                    deleted_detail_plot = cursor.rowcount > 0
                    
                    if deleted_detail_plot:
                        debug_log("删除详细剧情成功", f"ID: {detailed_plot_id}, 同时删除了 {correction_deleted} 条修正记录")
                    else:
                        debug_log("详细剧情不存在", f"ID: {detailed_plot_id}")
                    
                    return deleted_detail_plot
        except Exception as e:
            error_log("删除详细剧情失败", f"ID: {detailed_plot_id}, 错误: {str(e)}")
            return False
    
    def update_detailed_plot_status(self, detailed_plot_id: str, status: DetailedPlotStatus) -> bool:
        """更新详细剧情状态"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        UPDATE detailed_plots 
                        SET status = %s, updated_at = %s
                        WHERE id = %s
                    """, (status.value, datetime.now(), detailed_plot_id))
                    conn.commit()
                    return cursor.rowcount > 0
        except Exception as e:
            error_log("更新详细剧情状态失败", e)
            return False
    
    def update_detailed_plot_title(self, detailed_plot_id: str, title: str) -> bool:
        """更新详细剧情标题"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        UPDATE detailed_plots 
                        SET title = %s, updated_at = %s
                        WHERE id = %s
                    """, (title, datetime.now(), detailed_plot_id))
                    conn.commit()
                    return cursor.rowcount > 0
        except Exception as e:
            error_log("更新详细剧情标题失败", e)
            return False
    
    def update_logic_check_result(self, detailed_plot_id: str, logic_check_result: LogicCheckResult, 
                                 logic_status: LogicStatus) -> bool:
        """更新详细剧情的逻辑检查结果"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        UPDATE detailed_plots 
                        SET logic_check_result = %s,
                            logic_status = %s,
                            updated_at = %s
                        WHERE id = %s
                    """, (
                        json.dumps(logic_check_result.dict(), default=str) if logic_check_result else None,
                        logic_status.value if logic_status else None,
                        datetime.now(),
                        detailed_plot_id
                    ))
                    conn.commit()
                    return cursor.rowcount > 0
        except Exception as e:
            error_log("更新逻辑检查结果失败", e)
            return False
    
    def update_scoring_result(self, detailed_plot_id: str, scoring_status: str, 
                             total_score: float, scoring_result: Dict[str, Any], 
                             scoring_feedback: str, scored_by: str) -> bool:
        """更新详细剧情的评分结果"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        UPDATE detailed_plots 
                        SET scoring_status = %s,
                            total_score = %s,
                            scoring_result = %s,
                            scoring_feedback = %s,
                            scored_at = %s,
                            scored_by = %s,
                            updated_at = %s
                        WHERE id = %s
                    """, (
                        scoring_status,
                        total_score,
                        json.dumps(scoring_result) if scoring_result else None,
                        scoring_feedback,
                        datetime.now(),
                        scored_by,
                        datetime.now(),
                        detailed_plot_id
                    ))
                    conn.commit()
                    return cursor.rowcount > 0
        except Exception as e:
            error_log("更新评分结果失败", e)
            return False
    
    def save_scoring_history(self, scoring_history: Dict[str, Any]) -> bool:
        """保存评分历史记录"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO scoring_history 
                        (id, detailed_plot_id, scoring_type, total_score, dimension_scores, 
                         detailed_feedback, overall_feedback, improvement_suggestions, 
                         scored_by, scored_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        scoring_history["id"],
                        scoring_history["detailed_plot_id"],
                        scoring_history["scoring_type"],
                        scoring_history["total_score"],
                        json.dumps(scoring_history["dimension_scores"]),
                        json.dumps(scoring_history["detailed_feedback"]),
                        scoring_history["overall_feedback"],
                        json.dumps(scoring_history["improvement_suggestions"]),
                        scoring_history["scored_by"],
                        scoring_history["scored_at"]
                    ))
                    conn.commit()
                    return cursor.rowcount > 0
        except Exception as e:
            error_log("保存评分历史失败", e)
            return False
    
    def get_scoring_history(self, detailed_plot_id: str) -> List[Dict[str, Any]]:
        """获取详细剧情的评分历史"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT id, scoring_type, total_score, dimension_scores, 
                               detailed_feedback, overall_feedback, improvement_suggestions,
                               scored_by, scored_at
                        FROM scoring_history 
                        WHERE detailed_plot_id = %s
                        ORDER BY scored_at DESC
                    """, (detailed_plot_id,))
                    
                    rows = cursor.fetchall()
                    history = []
                    for row in rows:
                        history.append({
                            "id": row[0],
                            "scoring_type": row[1],
                            "total_score": row[2],
                            "dimension_scores": json.loads(row[3]) if row[3] else {},
                            "detailed_feedback": json.loads(row[4]) if row[4] else {},
                            "overall_feedback": row[5],
                            "improvement_suggestions": json.loads(row[6]) if row[6] else [],
                            "scored_by": row[7],
                            "scored_at": row[8]
                        })
                    return history
        except Exception as e:
            error_log("获取评分历史失败", e)
            return []

    def _row_to_detailed_plot(self, row) -> DetailedPlot:
        """将数据库行转换为DetailedPlot对象"""
        debug_log("Row data", row)
        debug_log("Row length", len(row))
        
        # 处理logic_check_result字段
        logic_check_result = None
        if row[7]:
            if isinstance(row[7], str):
                try:
                    logic_check_result = json.loads(row[7])
                except json.JSONDecodeError:
                    logic_check_result = None
            elif isinstance(row[7], dict):
                logic_check_result = row[7]
        
        # 处理scoring_result字段
        scoring_result = None
        if len(row) > 12 and row[12]:
            if isinstance(row[12], str):
                try:
                    scoring_result = json.loads(row[12])
                except json.JSONDecodeError:
                    scoring_result = None
            elif isinstance(row[12], dict):
                scoring_result = row[12]
        
        return DetailedPlot(
            id=row[0],
            chapter_outline_id=row[1],
            plot_outline_id=row[2],
            title=row[3],
            content=row[4],
            word_count=row[5] or 0,
            status=DetailedPlotStatus(row[6]) if row[6] else DetailedPlotStatus.DRAFT,
            logic_check_result=logic_check_result,
            logic_status=LogicStatus(row[8]) if row[8] else None,
            scoring_status=ScoringStatus(row[9]) if len(row) > 9 and row[9] else ScoringStatus.NOT_SCORED,
            total_score=row[10] if len(row) > 10 else None,
            scoring_result=scoring_result,
            scoring_feedback=row[12] if len(row) > 12 else None,
            scored_at=row[13] if len(row) > 13 else None,
            scored_by=row[14] if len(row) > 14 else None,
            created_at=row[15] if len(row) > 15 else None,
            updated_at=row[16] if len(row) > 16 else None
        )
    
    def update_detailed_plot_content(self, detailed_plot_id: str, content: str, word_count: int) -> bool:
        """更新详细剧情内容"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    query = """
                        UPDATE detailed_plots 
                        SET content = %s, word_count = %s, updated_at = NOW()
                        WHERE id = %s
                    """
                    cursor.execute(query, (content, word_count, detailed_plot_id))
                    conn.commit()
                    return True
        except Exception as e:
            error_log("更新详细剧情内容失败", f"ID: {detailed_plot_id}, 错误: {str(e)}")
            return False
    
    def save_evolution_history(self, evolution_history: Dict[str, Any]) -> bool:
        """保存进化历史记录"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    query = """
                        INSERT INTO evolution_history 
                        (id, detailed_plot_id, evolution_type, original_content, evolved_content, 
                         improvements, evolution_summary, word_count_change, quality_score, 
                         evolution_notes, evolved_by, evolved_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(query, (
                        evolution_history["id"],
                        evolution_history["detailed_plot_id"],
                        evolution_history["evolution_type"],
                        evolution_history["original_content"],
                        evolution_history["evolved_content"],
                        json.dumps(evolution_history["improvements"]),
                        evolution_history["evolution_summary"],
                        evolution_history["word_count_change"],
                        evolution_history["quality_score"],
                        evolution_history["evolution_notes"],
                        evolution_history["evolved_by"],
                        evolution_history["evolved_at"]
                    ))
                    conn.commit()
                    return True
        except Exception as e:
            error_log("保存进化历史失败", f"错误: {str(e)}")
            return False
    
    def get_evolution_history(self, detailed_plot_id: str) -> List[Dict[str, Any]]:
        """获取进化历史记录"""
        try:
            query = """
                SELECT id, evolution_type, original_content, evolved_content, 
                       improvements, evolution_summary, word_count_change, 
                       quality_score, evolution_notes, evolved_by, evolved_at
                FROM evolution_history 
                WHERE detailed_plot_id = %s 
                ORDER BY evolved_at DESC
            """
            self.cursor.execute(query, (detailed_plot_id,))
            rows = self.cursor.fetchall()
            
            history = []
            for row in rows:
                # 解析improvements字段
                improvements = {}
                if row[4]:
                    try:
                        improvements = json.loads(row[4]) if isinstance(row[4], str) else row[4]
                    except json.JSONDecodeError:
                        improvements = {}
                
                history.append({
                    "id": row[0],
                    "evolution_type": row[1],
                    "original_content": row[2],
                    "evolved_content": row[3],
                    "improvements": improvements,
                    "evolution_summary": row[5],
                    "word_count_change": row[6],
                    "quality_score": row[7],
                    "evolution_notes": row[8],
                    "evolved_by": row[9],
                    "evolved_at": row[10].isoformat() if row[10] else None
                })
            
            return history
        except Exception as e:
            error_log("获取进化历史失败", f"ID: {detailed_plot_id}, 错误: {str(e)}")
            return []
    
    def save_correction_history(self, correction_history: Dict[str, Any]) -> bool:
        """保存修正历史记录"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    query = """
                        INSERT INTO correction_history 
                        (id, detailed_plot_id, original_content, corrected_content, 
                         logic_check_result, corrections_made, correction_summary, 
                         word_count_change, quality_improvement, correction_notes, 
                         corrected_by, corrected_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(query, (
                        correction_history["id"],
                        correction_history["detailed_plot_id"],
                        correction_history["original_content"],
                        correction_history["corrected_content"],
                        json.dumps(correction_history["logic_check_result"]),
                        json.dumps(correction_history["corrections_made"]),
                        correction_history["correction_summary"],
                        correction_history["word_count_change"],
                        correction_history["quality_improvement"],
                        correction_history["correction_notes"],
                        correction_history["corrected_by"],
                        correction_history["corrected_at"]
                    ))
                    conn.commit()
                    return True
        except Exception as e:
            error_log("保存修正历史失败", f"错误: {str(e)}")
            return False
    
    def get_correction_history(self, detailed_plot_id: str) -> List[Dict[str, Any]]:
        """获取修正历史记录"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    query = """
                        SELECT id, original_content, corrected_content, 
                               logic_check_result, corrections_made, correction_summary, 
                               word_count_change, quality_improvement, correction_notes, 
                               corrected_by, corrected_at
                        FROM correction_history 
                        WHERE detailed_plot_id = %s 
                        ORDER BY corrected_at DESC
                    """
                    cursor.execute(query, (detailed_plot_id,))
                    rows = cursor.fetchall()
                    
                    history = []
                    for row in rows:
                        # 解析JSON字段
                        logic_check_result = {}
                        if row[3]:
                            try:
                                logic_check_result = json.loads(row[3]) if isinstance(row[3], str) else row[3]
                            except json.JSONDecodeError:
                                logic_check_result = {}
                        
                        corrections_made = []
                        if row[4]:
                            try:
                                corrections_made = json.loads(row[4]) if isinstance(row[4], str) else row[4]
                            except json.JSONDecodeError:
                                corrections_made = []
                        
                        history.append({
                            "id": row[0],
                            "original_content": row[1],
                            "corrected_content": row[2],
                            "logic_check_result": logic_check_result,
                            "corrections_made": corrections_made,
                            "correction_summary": row[5],
                            "word_count_change": row[6],
                            "quality_improvement": row[7],
                            "correction_notes": row[8],
                            "corrected_by": row[9],
                            "corrected_at": row[10].isoformat() if row[10] else None
                        })
                    
                    return history
        except Exception as e:
            error_log("获取修正历史失败", f"ID: {detailed_plot_id}, 错误: {str(e)}")
            return []
    
    def _row_to_detailed_plot_with_version(self, row) -> DetailedPlot:
        """将数据库记录转换为DetailedPlot对象（支持版本管理）"""
        try:
            # 解析JSON字段
            logic_check_result = None
            if row[5]:  # logic_check_result
                try:
                    logic_check_result = json.loads(row[5]) if isinstance(row[5], str) else row[5]
                except json.JSONDecodeError:
                    logic_check_result = None
            
            scoring_result = None
            if row[9]:  # scoring_result
                try:
                    scoring_result = json.loads(row[9]) if isinstance(row[9], str) else row[9]
                except json.JSONDecodeError:
                    scoring_result = None
            
            # 确定使用哪个版本的内容
            if row[29]:  # has_version_record (索引29，总共30个字段)
                # 有版本记录，使用最新版本
                title = row[20] or row[14]  # current_title or original_title
                content = row[21] or row[15]  # current_content or original_content
                word_count = row[22] or row[16]  # current_word_count or original_word_count
                created_at = row[27] or row[12]  # current_created_at or original_created_at
                updated_at = row[28] or row[13]  # current_updated_at or original_updated_at
            else:
                # 没有版本记录，使用原始内容
                title = row[14]  # original_title
                content = row[15]  # original_content
                word_count = row[16]  # original_word_count
                created_at = row[12]  # original_created_at
                updated_at = row[13]  # original_updated_at
            
            return DetailedPlot(
                id=row[0],  # original_id
                chapter_outline_id=row[1],
                plot_outline_id=row[2],
                title=title,
                content=content,
                word_count=word_count,
                status=DetailedPlotStatus(row[3]) if row[3] else DetailedPlotStatus.DRAFT,
                logic_check_result=logic_check_result,
                logic_status=LogicStatus(row[4]) if row[4] else None,
                scoring_status=ScoringStatus(row[6]) if row[6] else ScoringStatus.NOT_SCORED,
                total_score=float(row[7]) if row[7] else None,
                scoring_result=scoring_result,
                scoring_feedback=row[8],
                scored_at=row[10],
                scored_by=row[11],
                created_at=created_at,
                updated_at=updated_at
            )
        except Exception as e:
            error_log("转换详细剧情对象失败", e)
            raise
    
    def save_detailed_plot_version(self, detailed_plot_id: str, version_type: str, 
                                  title: str, content: str, source_table: str = None, 
                                  source_record_id: str = None, version_notes: str = None) -> bool:
        """保存详细剧情版本记录"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    # 先将该详细剧情的所有版本设为非当前版本
                    cursor.execute("""
                        UPDATE detailed_plot_versions 
                        SET is_current_version = FALSE, updated_at = CURRENT_TIMESTAMP
                        WHERE detailed_plot_id = %s
                    """, (detailed_plot_id,))
                    
                    # 插入新版本记录
                    cursor.execute("""
                        INSERT INTO detailed_plot_versions (
                            detailed_plot_id, version_type, is_current_version,
                            title, content, word_count, source_table, source_record_id,
                            version_notes, created_by, created_at, updated_at
                        ) VALUES (
                            %s, %s, TRUE, %s, %s, %s, %s, %s, %s, 'system', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                        )
                    """, (
                        detailed_plot_id, version_type, title, content, len(content),
                        source_table, source_record_id, version_notes
                    ))
                    
                    conn.commit()
                    return True
        except Exception as e:
            error_log("保存详细剧情版本失败", e)
            return False
    
    def get_detailed_plot_versions(self, detailed_plot_id: str) -> List[Dict[str, Any]]:
        """获取详细剧情的所有版本"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT id, version_type, version_number, is_current_version,
                               title, content, word_count, source_table, source_record_id,
                               version_notes, created_by, created_at, updated_at
                        FROM detailed_plot_versions 
                        WHERE detailed_plot_id = %s
                        ORDER BY updated_at DESC, created_at DESC
                    """, (detailed_plot_id,))
                    
                    rows = cursor.fetchall()
                    versions = []
                    for row in rows:
                        versions.append({
                            "id": row[0],
                            "version_type": row[1],
                            "version_number": row[2],
                            "is_current_version": row[3],
                            "title": row[4],
                            "content": row[5],
                            "word_count": row[6],
                            "source_table": row[7],
                            "source_record_id": row[8],
                            "version_notes": row[9],
                            "created_by": row[10],
                            "created_at": row[11].isoformat() if row[11] else None,
                            "updated_at": row[12].isoformat() if row[12] else None
                        })
                    
                    return versions
        except Exception as e:
            error_log("获取详细剧情版本失败", e)
            return []
    
    def set_current_version(self, detailed_plot_id: str, version_record_id: int) -> bool:
        """设置指定版本为当前版本"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    # 使用数据库函数
                    cursor.execute("""
                        SELECT set_detailed_plot_current_version(%s, %s)
                    """, (detailed_plot_id, version_record_id))
                    
                    result = cursor.fetchone()[0]
                    conn.commit()
                    return result
        except Exception as e:
            error_log("设置当前版本失败", e)
            return False
