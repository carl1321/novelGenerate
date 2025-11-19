"""
事件-章节映射管理API
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.core.event_generator.event_database import EventDatabase
from app.core.chapter_engine.chapter_database import ChapterOutlineDatabase

router = APIRouter()

# 初始化数据库
event_database = EventDatabase()
chapter_database = ChapterOutlineDatabase()


class EventChapterMappingRequest(BaseModel):
    """事件-章节映射请求"""
    event_id: str = Field(..., description="事件ID")
    chapter_outline_id: str = Field(..., description="章节大纲ID")
    integration_type: str = Field(..., description="融入类型：driving/conflict/emotional/background")
    sequence_order: int = Field(0, description="在同一章节中的顺序")
    integration_notes: Optional[str] = Field(None, description="融入说明")


class EventChapterMappingResponse(BaseModel):
    """事件-章节映射响应"""
    success: bool
    mapping_id: Optional[str] = None
    message: str


class BulkMappingRequest(BaseModel):
    """批量映射请求"""
    mappings: List[EventChapterMappingRequest]
    auto_assign_order: bool = True  # 是否自动分配顺序


@router.post("/event-chapter-mappings", response_model=EventChapterMappingResponse)
async def create_event_chapter_mapping(request: EventChapterMappingRequest):
    """创建事件-章节映射"""
    try:
        # 验证事件是否存在
        event = event_database.get_event_by_id(request.event_id)
        if not event:
            raise HTTPException(status_code=404, detail="事件不存在")
        
        # 验证章节大纲是否存在
        chapter = chapter_database.get_chapter_outline(request.chapter_outline_id)
        if not chapter:
            raise HTTPException(status_code=404, detail="章节大纲不存在")
        
        # 创建映射
        mapping_id = event_database.create_event_chapter_mapping(
            event_id=request.event_id,
            chapter_outline_id=request.chapter_outline_id,
            integration_type=request.integration_type,
            sequence_order=request.sequence_order,
            integration_notes=request.integration_notes
        )
        
        return EventChapterMappingResponse(
            success=True,
            mapping_id=mapping_id,
            message="事件-章节映射创建成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/event-chapter-mappings/bulk", response_model=Dict[str, Any])
async def create_bulk_event_chapter_mappings(request: BulkMappingRequest):
    """批量创建事件-章节映射"""
    try:
        created_mappings = []
        failed_mappings = []
        
        for i, mapping_request in enumerate(request.mappings):
            try:
                # 自动分配顺序
                if request.auto_assign_order:
                    mapping_request.sequence_order = i
                
                # 创建映射
                mapping_id = event_database.create_event_chapter_mapping(
                    event_id=mapping_request.event_id,
                    chapter_outline_id=mapping_request.chapter_outline_id,
                    integration_type=mapping_request.integration_type,
                    sequence_order=mapping_request.sequence_order,
                    integration_notes=mapping_request.integration_notes
                )
                
                created_mappings.append({
                    "mapping_id": mapping_id,
                    "event_id": mapping_request.event_id,
                    "chapter_outline_id": mapping_request.chapter_outline_id,
                    "integration_type": mapping_request.integration_type
                })
                
            except Exception as e:
                failed_mappings.append({
                    "index": i,
                    "event_id": mapping_request.event_id,
                    "chapter_outline_id": mapping_request.chapter_outline_id,
                    "error": str(e)
                })
        
        return {
            "success": len(failed_mappings) == 0,
            "created_count": len(created_mappings),
            "failed_count": len(failed_mappings),
            "created_mappings": created_mappings,
            "failed_mappings": failed_mappings,
            "message": f"成功创建{len(created_mappings)}个映射，失败{len(failed_mappings)}个"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/event-chapter-mappings/chapter/{chapter_outline_id}")
async def get_chapter_event_mappings(chapter_outline_id: str):
    """获取章节的事件映射"""
    try:
        mappings = event_database.get_chapter_event_mappings(chapter_outline_id)
        return {
            "chapter_outline_id": chapter_outline_id,
            "mappings": mappings,
            "total_count": len(mappings)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/event-chapter-mappings/event/{event_id}")
async def get_event_chapter_mappings(event_id: str):
    """获取事件的章节映射"""
    try:
        mappings = event_database.get_event_chapter_mappings(event_id)
        return {
            "event_id": event_id,
            "mappings": mappings,
            "total_count": len(mappings)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/event-chapter-mappings/{mapping_id}")
async def update_event_chapter_mapping(mapping_id: str, request: EventChapterMappingRequest):
    """更新事件-章节映射"""
    try:
        success = event_database.update_event_chapter_mapping(
            mapping_id=mapping_id,
            integration_type=request.integration_type,
            sequence_order=request.sequence_order,
            integration_notes=request.integration_notes
        )
        
        if success:
            return {"success": True, "message": "映射更新成功"}
        else:
            raise HTTPException(status_code=404, detail="映射不存在")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/event-chapter-mappings/{mapping_id}")
async def delete_event_chapter_mapping(mapping_id: str):
    """删除事件-章节映射"""
    try:
        success = event_database.delete_event_chapter_mapping(mapping_id)
        if success:
            return {"success": True, "message": "映射删除成功"}
        else:
            raise HTTPException(status_code=404, detail="映射不存在")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/event-chapter-mappings/plot/{plot_outline_id}")
async def get_plot_event_chapter_mappings(plot_outline_id: str):
    """获取剧情大纲的所有事件-章节映射"""
    try:
        mappings = event_database.get_plot_event_chapter_mappings(plot_outline_id)
        return {
            "plot_outline_id": plot_outline_id,
            "mappings": mappings,
            "total_count": len(mappings)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/event-chapter-mappings/auto-assign/{plot_outline_id}")
async def auto_assign_events_to_chapters(plot_outline_id: str):
    """自动为剧情大纲的事件分配章节"""
    try:
        # 获取剧情大纲的所有事件和章节
        events = event_database.get_events_by_plot_outline(plot_outline_id)
        chapters = chapter_database.get_chapter_outlines_by_plot(plot_outline_id)
        
        if not events or not chapters:
            raise HTTPException(status_code=400, detail="没有找到事件或章节")
        
        # 执行自动分配逻辑
        assignments = event_database.auto_assign_events_to_chapters(events, chapters)
        
        return {
            "success": True,
            "plot_outline_id": plot_outline_id,
            "assignments": assignments,
            "total_assignments": len(assignments),
            "message": f"成功为{len(assignments)}个事件分配了章节"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
