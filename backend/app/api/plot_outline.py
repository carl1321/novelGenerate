"""
剧情大纲API接口 - 专注于故事框架设计
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel, Field

from app.core.plot_engine.plot_engine import PlotOutlineEngine
from app.core.plot_engine.plot_models import (
    PlotOutline, PlotOutlineRequest, PlotOutlineResponse,
    PlotStructure, ConflictType, NarrativeStructure
)

router = APIRouter()
plot_engine = PlotOutlineEngine()


class SimplePlotRequest(BaseModel):
    """简化的剧情生成请求 - 故事驱动模式"""
    worldview_id: str = Field(..., description="世界观ID")
    title: str = Field(..., description="小说标题")
    
    # 故事要素（人工输入）
    core_conflict: str = Field(..., description="核心冲突")
    story_tone: str = Field(..., description="故事基调")
    narrative_structure: str = Field(..., description="叙事结构")
    story_structure: str = Field(..., description="故事结构")
    theme: str = Field(..., description="主题思想")
    
    # 主角信息（从角色数据获取）
    protagonist_character_id: str = Field(..., description="主角角色ID")
    
    # 技术参数
    target_word_count: int = Field(default=100000, description="目标字数")
    estimated_chapters: int = Field(default=20, description="预计章节数")
    
    # 可选参数
    additional_requirements: Optional[str] = Field(None, description="额外要求")


@router.post("/generate", response_model=PlotOutlineResponse)
async def generate_plot_outline(request: PlotOutlineRequest):
    """生成剧情大纲"""
    try:
        response = await plot_engine.generate_plot_outline(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/plot-outlines", response_model=PlotOutlineResponse)
async def create_plot_outline(request: PlotOutlineRequest):
    """创建剧情大纲"""
    try:
        response = await plot_engine.generate_plot_outline(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/plot-outlines/simple", response_model=PlotOutlineResponse)
async def create_simple_plot_outline(request: SimplePlotRequest):
    """创建简化的剧情大纲（故事驱动模式）"""
    try:
        # 转换请求格式
        plot_request = PlotOutlineRequest(
            worldview_id=request.worldview_id,
            title=request.title,
            core_conflict=request.core_conflict,
            story_tone=request.story_tone,
            narrative_structure=request.narrative_structure,
            story_structure=request.story_structure,
            theme=request.theme,
            protagonist_character_id=request.protagonist_character_id,
            target_word_count=request.target_word_count,
            estimated_chapters=request.estimated_chapters
        )
        
        response = await plot_engine.generate_plot_outline(plot_request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/plot-outlines/{plot_id}", response_model=PlotOutline)
async def get_plot_outline(plot_id: str):
    """获取剧情大纲"""
    try:
        plot_outline = plot_engine.plot_database.get_plot_outline(plot_id)
        if not plot_outline:
            raise HTTPException(status_code=404, detail="剧情大纲不存在")
        return plot_outline
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/plot-outlines/{plot_id}", response_model=PlotOutline)
async def update_plot_outline(plot_id: str, plot_data: dict):
    """更新剧情大纲"""
    try:
        from app.core.plot_engine.plot_models import PlotOutline
        
        # 验证数据
        plot_outline = PlotOutline(**plot_data)
        
        # 更新数据库
        success = plot_engine.plot_database.save_plot_outline(plot_outline)
        
        if success:
            return plot_outline
        else:
            raise HTTPException(status_code=500, detail="更新失败")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/plot-outlines/{plot_id}")
async def delete_plot_outline(plot_id: str):
    """删除剧情大纲"""
    try:
        success = plot_engine.plot_database.delete_plot_outline(plot_id)
        if success:
            return {"message": "剧情大纲删除成功"}
        else:
            raise HTTPException(status_code=400, detail="无法删除剧情大纲：存在关联的章节大纲，请先删除所有章节大纲")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/plot-outlines", response_model=List[PlotOutline])
async def list_plot_outlines(
    worldview_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 20,
    offset: int = 0
):
    """获取剧情大纲列表"""
    try:
        plot_outlines = plot_engine.plot_database.get_plot_outlines_by_worldview(
            worldview_id=worldview_id,
            status=status,
            limit=limit,
            offset=offset
        )
        return plot_outlines
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/plot-outlines/{plot_id}/stats")
async def get_plot_outline_stats(plot_id: str):
    """获取剧情大纲统计信息"""
    # 这里应该从数据库获取统计信息
    # 目前返回模拟数据
    raise HTTPException(status_code=501, detail="功能尚未实现")


@router.get("/plot-outlines/{plot_id}/details")
async def get_plot_outline_details(plot_id: str):
    """获取剧情大纲详细信息（包含所有相关数据）"""
    # 这里应该从数据库获取详细信息
    # 目前返回模拟数据
    raise HTTPException(status_code=501, detail="功能尚未实现")
