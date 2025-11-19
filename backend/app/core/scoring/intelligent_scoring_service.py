"""
智能评分服务
"""
from typing import Dict, List, Any, Optional
import asyncio
import json
from datetime import datetime
from uuid import uuid4

from app.utils.llm_client import get_llm_client
from app.utils.prompt_manager import PromptManager
from app.core.scoring.database import ScoringDatabase
from app.core.scoring.models import (
    ScoringRecord, ScoringDimension, ScoringResult, 
    ScoringDisplayData, DimensionScore, ScoringType, ScoringLevel
)
from app.core.detailed_plot.detailed_plot_models import ScoringStatus


class IntelligentScoringService:
    """智能评分服务类"""
    
    def __init__(self):
        self.llm_client = get_llm_client()
        self.prompt_manager = PromptManager()
        self.scoring_db = ScoringDatabase()
    
    async def score_detailed_plot(self, content: str, detailed_plot_id: str, scorer_id: str = "system") -> Dict[str, Any]:
        """对详细剧情进行智能评分"""
        try:
            # 获取评分标准prompt
            prompt = self.prompt_manager.get_scoring_criteria_prompt(content)
            
            # 调用LLM进行评分
            response = await self.llm_client.generate_text(
                prompt=prompt,
                temperature=0.3,
                max_tokens=4000
            )
            
            # 解析LLM响应
            scoring_data = self._parse_scoring_response(response)
            
            # 生成评分记录ID
            scoring_record_id = str(uuid4())
            
            # 获取维度映射配置
            dimension_mappings = self.scoring_db.get_dimension_mappings()
            dimension_map = {dm.technical_name: dm for dm in dimension_mappings}
            
            # 创建评分记录
            scoring_record = ScoringRecord(
                id=scoring_record_id,
                detailed_plot_id=detailed_plot_id,
                scorer_id=scorer_id,
                scoring_type=ScoringType.INTELLIGENT,
                total_score=scoring_data.get("total_score", 0.0),
                scoring_level=ScoringLevel.POOR,  # 临时值，稍后会计算
                overall_feedback=scoring_data.get("overall_feedback", ""),
                improvement_suggestions=scoring_data.get("improvement_suggestions", []),
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            # 计算评分等级
            scoring_record.scoring_level = scoring_record.calculate_scoring_level()
            
            # 创建各维度评分记录
            dimensions = []
            scores = scoring_data.get("scores", {})
            detailed_feedback = scoring_data.get("detailed_feedback", {})
            
            for dimension_name, score in scores.items():
                dimension_info = dimension_map.get(dimension_name)
                dimension_id = str(uuid4())
                
                dimensions.append(ScoringDimension(
                    id=dimension_id,
                    scoring_record_id=scoring_record_id,
                    dimension_name=dimension_name,
                    dimension_display_name=dimension_info.display_name if dimension_info else dimension_name,
                    score=float(score),
                    feedback=detailed_feedback.get(dimension_name, ""),
                    weight=dimension_info.weight if dimension_info else 1.0,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                ))
            
            # 保存到数据库
            success = self.scoring_db.create_scoring_record(scoring_record, dimensions)
            
            if success:
                return {
                    "scoring_status": ScoringStatus.COMPLETED,
                    "total_score": scoring_record.total_score,
                    "scoring_level": scoring_record.scoring_level.value,
                    "overall_feedback": scoring_record.overall_feedback,
                    "improvement_suggestions": scoring_record.improvement_suggestions,
                    "dimensions": [
                        {
                            "dimension_name": dim.dimension_name,
                            "dimension_display_name": dim.dimension_display_name,
                            "score": dim.score,
                            "feedback": dim.feedback,
                            "weight": dim.weight
                        }
                        for dim in dimensions
                    ],
                    "scored_at": scoring_record.created_at.isoformat(),
                    "scored_by": scorer_id,
                    "scoring_record_id": scoring_record_id
                }
            else:
                return {
                    "scoring_status": ScoringStatus.FAILED,
                    "total_score": 0.0,
                    "scoring_level": "评分失败",
                    "error": "数据库保存失败"
                }
                
        except Exception as e:
            return {
                "scoring_status": ScoringStatus.FAILED,
                "total_score": 0.0,
                "scoring_level": "评分失败",
                "error": str(e)
            }
    
    def get_scoring_result(self, detailed_plot_id: str) -> Optional[ScoringDisplayData]:
        """获取评分结果"""
        try:
            latest_scoring = self.scoring_db.get_latest_scoring_by_detailed_plot_id(detailed_plot_id)
            if not latest_scoring:
                return None
            
            dimensions = []
            for dim in latest_scoring.dimensions:
                dimensions.append(DimensionScore(
                    dimension_name=dim.dimension_name,
                    dimension_display_name=dim.dimension_display_name,
                    score=dim.score,
                    feedback=dim.feedback,
                    weight=dim.weight
                ))
            
            return ScoringDisplayData(
                total_score=latest_scoring.scoring_record.total_score,
                scoring_level=latest_scoring.scoring_record.scoring_level,
                overall_feedback=latest_scoring.scoring_record.overall_feedback or "",
                improvement_suggestions=latest_scoring.scoring_record.improvement_suggestions or [],
                dimensions=dimensions
            )
            
        except Exception as e:
            return None
    
    def _parse_scoring_response(self, response: str) -> Dict[str, Any]:
        """解析LLM评分响应"""
        try:
            # 尝试解析JSON
            if response.strip().startswith('```json'):
                # 提取JSON部分
                start = response.find('```json') + 7
                end = response.find('```', start)
                json_str = response[start:end].strip()
            elif response.strip().startswith('```'):
                # 提取JSON部分
                start = response.find('```') + 3
                end = response.find('```', start)
                json_str = response[start:end].strip()
            else:
                json_str = response.strip()
            
            return json.loads(json_str)
            
        except json.JSONDecodeError as e:
            print(f"解析评分响应失败: {e}")
            print(f"响应内容: {response}")
            
            # 返回默认结构
            return {
                "total_score": 0.0,
                "scores": {
                    "logic_consistency": 0.0,
                    "dramatic_conflict": 0.0,
                    "character_development": 0.0,
                    "world_usage": 0.0,
                    "writing_style": 0.0
                },
                "detailed_feedback": {
                    "logic_consistency": "解析失败",
                    "dramatic_conflict": "解析失败",
                    "character_development": "解析失败",
                    "world_usage": "解析失败",
                    "writing_style": "解析失败"
                },
                "overall_feedback": "评分解析失败，请重试",
                "improvement_suggestions": ["请重新进行评分"]
            }
    
    async def get_scoring_analysis(self, scoring_result: Dict[str, Any]) -> Dict[str, Any]:
        """获取评分分析"""
        if not scoring_result:
            return {"error": "无评分结果"}
        
        total_score = scoring_result.get("total_score", 0.0)
        scores = scoring_result.get("scores", {})
        
        # 计算等级
        if total_score >= 90:
            level = "优秀"
            level_color = "#52c41a"
        elif total_score >= 80:
            level = "良好"
            level_color = "#1890ff"
        elif total_score >= 70:
            level = "一般"
            level_color = "#faad14"
        elif total_score >= 60:
            level = "较差"
            level_color = "#fa8c16"
        else:
            level = "很差"
            level_color = "#ff4d4f"
        
        # 找出最低分的维度
        min_score_dimension = min(scores.items(), key=lambda x: x[1]) if scores else ("无", 0)
        
        return {
            "total_score": total_score,
            "level": level,
            "level_color": level_color,
            "scores": scores,
            "min_score_dimension": min_score_dimension,
            "detailed_feedback": scoring_result.get("detailed_feedback", {}),
            "overall_feedback": scoring_result.get("overall_feedback", ""),
            "improvement_suggestions": scoring_result.get("improvement_suggestions", [])
        }
