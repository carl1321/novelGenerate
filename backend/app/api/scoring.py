"""
评分智能体API接口
"""
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.core.scoring.intelligent_scoring_service import IntelligentScoringService
from app.core.scoring.database import ScoringDatabase
from app.core.scoring.models import ScoringCreateRequest, ScoringResponse, ScoringDisplayData
from app.core.detailed_plot.detailed_plot_database import DetailedPlotDatabase

router = APIRouter()

# 初始化服务
scoring_service = IntelligentScoringService()
scoring_db = ScoringDatabase()
detailed_plot_database = DetailedPlotDatabase()


class ScoringRequestApi(BaseModel):
    """评分请求API模型"""
    detailed_plot_id: str = Field(..., description="详细剧情ID")
    scorer_id: str = Field(default="system", description="评分者ID")


class ScoringInfoRequest(BaseModel):
    """详细剧情信息请求模型"""
    detailed_plot_id: str = Field(..., description="详细剧情ID")
    content: str = Field(..., description="详细剧情内容")


@router.post("/detailed-plots/{detailed_plot_id}/scoring", response_model=Dict[str, Any])
async def score_detailed_plot(detailed_plot_id: str, request: ScoringInfoRequest):
    """对详细剧情进行智能评分"""
    try:
        # 调用智能评分服务
        result = await scoring_service.score_detailed_plot(
            content=request.content,
            detailed_plot_id=request.detailed_plot_id,
            scorer_id="manual"
        )
        
        # 更新详细剧情的评分结果
        if "scoring_status" in result and "total_score" in result:
            success = detailed_plot_database.update_scoring_result(
                detailed_plot_id=detailed_plot_id,
                scoring_status=result["scoring_status"].value if hasattr(result["scoring_status"], 'value') else result["scoring_status"],
                total_score=result["total_score"],
                scoring_result=result.get("scoring_result", {}),
                scoring_feedback=result.get("scoring_feedback", ""),
                scored_by=result.get("scored_by", "manual")
            )
            
            if not success:
                print(f"警告: 更新详细剧情评分结果失败 - {detailed_plot_id}")
        
        return {
            "message": "智能评分完成",
            "scoring_result": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"智能评分失败: {str(e)}")


@router.get("/detailed-plots/{detailed_plot_id}/scoring", response_model=Dict[str, Any])
async def get_scoring_result(detailed_plot_id: str):
    """获取详细剧情的最新评分结果"""
    try:
        latest_scoring = scoring_db.get_latest_scoring_by_detailed_plot_id(detailed_plot_id)
        
        if not latest_scoring:
            return {
                "message": "暂无评分记录",
                "scoring_result": None
            }
        
        # 构建前端需要的数据格式
        dimensions = []
        for dim in latest_scoring.dimensions:
            dimensions.append({
                "dimension_name": dim.dimension_name,
                "dimension_display_name": dim.dimension_display_name,
                "score": dim.score,
                "feedback": dim.feedback,
                "weight": dim.weight
            })
        
        return {
            "message": "获取评分结果成功",
            "scoring_result": {
                "total_score": latest_scoring.scoring_record.total_score,
                "scoring_level": latest_scoring.scoring_record.scoring_level.value,
                "overall_feedback": latest_scoring.scoring_record.overall_feedback or "",
                "improvement_suggestions": latest_scoring.scoring_record.improvement_suggestions or [],
                "dimensions": dimensions,
                "scored_at": latest_scoring.scoring_record.created_at.isoformat() if latest_scoring.scoring_record.created_at else None,
                "scored_by": latest_scoring.scoring_record.scorer_id,
                "scoring_type": latest_scoring.scoring_record.scoring_type.value
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取评分结果失败: {str(e)}")


@router.get("/detailed-plots/{detailed_plot_id}/scoring-history", response_model=Dict[str, Any])
async def get_scoring_history(
    detailed_plot_id: str,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页大小")
):
    """获取详细剧情的评分历史"""
    try:
        scoring_results = scoring_db.get_scoring_by_detailed_plot_id(detailed_plot_id)
        
        # 分页处理
        total = len(scoring_results)
        start = (page - 1) * page_size
        end = start + page_size
        paginated_results = scoring_results[start:end]
        
        # 构建历史记录数据
        history_data = []
        for scoring_result in paginated_results:
            dimensions = []
            for dim in scoring_result.dimensions:
                dimensions.append({
                    "dimension_name": dim.dimension_name,
                    "dimension_display_name": dim.dimension_display_name,
                    "score": dim.score,
                    "feedback": dim.feedback,
                    "weight": dim.weight
                })
            
            history_data.append({
                "scoring_record_id": scoring_result.scoring_record.id,
                "total_score": scoring_result.scoring_record.total_score,
                "scoring_level": scoring_result.scoring_record.scoring_level.value,
                "overall_feedback": scoring_result.scoring_record.overall_feedback or "",
                "improvement_suggestions": scoring_result.scoring_record.improvement_suggestions or [],
                "dimensions": dimensions,
                "scored_at": scoring_result.scoring_record.created_at.isoformat() if scoring_result.scoring_record.created_at else None,
                "scored_by": scoring_result.scoring_record.scorer_id,
                "scoring_type": scoring_result.scoring_record.scoring_type.value
            })
        
        return {
            "message": "获取评分历史成功",
            "scoring_history": history_data,
            "pagination": {
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取评分历史失败: {str(e)}")


@router.delete("/detailed-plots/{detailed_plot_id}/scoring", response_model=Dict[str, Any])
async def delete_scoring_records(detailed_plot_id: str):
    """删除详细剧情的所有评分记录"""
    try:
        deleted_count = scoring_db.delete_scoring_records_by_plot_id(detailed_plot_id)
        
        return {
            "message": f"删除评分记录成功",
            "deleted_count": deleted_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除评分记录失败: {str(e)}")


@router.get("/scoring/statistics/{detailed_plot_id}", response_model=Dict[str, Any])
async def get_scoring_statistics(detailed_plot_id: str):
    """获取详细剧情的评分统计信息"""
    try:
        stats = scoring_db.get_scoring_statistics(detailed_plot_id)
        
        return {
            "message": "获取评分统计成功",
            "statistics": stats
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取评分统计失败: {str(e)}")


@router.get("/scoring/dimension-mappings", response_model=Dict[str, Any])
async def get_dimension_mappings():
    """获取维度映射配置"""
    try:
        mappings = scoring_db.get_dimension_mappings()
        
        mapping_data = []
        for mapping in mappings:
            mapping_data.append({
                "technical_name": mapping.technical_name,
                "display_name": mapping.display_name,
                "description": mapping.description,
                "color_code": mapping.color_code,
                "weight": mapping.weight,
                "is_active": mapping.is_active
            })
        
        return {
            "message": "获取维度映射成功",
            "dimension_mappings": mapping_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取维度映射失败: {str(e)}")