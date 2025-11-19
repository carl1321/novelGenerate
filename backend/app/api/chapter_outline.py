"""
章节大纲API接口 - 独立模块
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

from app.core.chapter_engine.chapter_engine import ChapterOutlineEngine
from app.core.chapter_engine.chapter_models_simplified import (
    ChapterOutline, ChapterOutlineRequest, ChapterOutlineResponse,
    EnhancedChapterRequest
)
from app.core.chapter_engine.chapter_database import ChapterOutlineDatabase

router = APIRouter()
chapter_engine = ChapterOutlineEngine()
chapter_database = ChapterOutlineDatabase()


class EnhancedChapterRequest(BaseModel):
    """增强的章节大纲生成请求（基于事件）"""
    plot_outline_id: str = Field(..., description="剧情大纲ID")
    worldview_id: Optional[str] = Field(None, description="世界观ID")
    character_ids: Optional[List[str]] = Field(None, description="角色ID列表")
    event_integration_mode: str = Field("auto", description="事件融入模式：auto/manual/none")
    chapter_count: Optional[int] = Field(None, description="要生成的章节数")
    start_chapter: Optional[int] = Field(1, description="起始章节号")
    act_belonging: Optional[str] = Field(None, description="选择的幕次")
    additional_requirements: Optional[str] = Field(None, description="额外要求")
    generate_event_mappings: bool = Field(True, description="是否生成事件-章节映射")


@router.post("/chapter-outlines", response_model=ChapterOutlineResponse)
async def create_chapter_outlines(request: EnhancedChapterRequest):
    """基于事件生成章节大纲"""
    try:
        # 1. 获取剧情大纲信息
        from app.core.plot_engine.plot_database import PlotOutlineDatabase
        plot_database = PlotOutlineDatabase()
        plot_outline = plot_database.get_plot_outline(request.plot_outline_id)
        if not plot_outline:
            raise HTTPException(status_code=404, detail="剧情大纲不存在")
        
        # 2. 获取世界观信息
        world_view = None
        if request.worldview_id:
            from app.core.world.database import WorldViewDatabase
            worldview_database = WorldViewDatabase()
            world_view = worldview_database.get_worldview(request.worldview_id)
            if not world_view:
                raise HTTPException(status_code=404, detail="世界观不存在")
        
        # 3. 获取角色信息
        characters = []
        if request.character_ids:
            from app.core.character.database import CharacterDatabase
            character_database = CharacterDatabase()
            characters = character_database.get_characters_by_ids(request.character_ids)
        elif world_view:
            from app.core.character.database import CharacterDatabase
            character_database = CharacterDatabase()
            # 处理Pydantic对象
            if hasattr(world_view, 'worldview_id'):
                worldview_id = world_view.worldview_id
            elif isinstance(world_view, dict):
                worldview_id = world_view.get("worldview_id", "")
            else:
                worldview_id = str(world_view.id) if hasattr(world_view, 'id') else ""
            characters = character_database.get_characters_by_worldview(worldview_id)
        
        # 4. 获取相关事件
        related_events = []
        if request.event_integration_mode != "none":
            from app.core.event_generator.event_database import EventDatabase
            event_database = EventDatabase()
            # 如果指定了幕次，按幕次过滤事件
            related_events = event_database.get_events_by_plot_outline(
                request.plot_outline_id, 
                request.act_belonging
            )
        
        # 5. 生成增强的章节大纲
        response = await chapter_engine.generate_enhanced_chapter_outlines(
            plot_outline=plot_outline,
            world_view=world_view or {},
            characters=characters,
            related_events=related_events,
            event_integration_mode=request.event_integration_mode,
            chapter_count=request.chapter_count,
            start_chapter=request.start_chapter,
            act_belonging=request.act_belonging,
            additional_requirements=request.additional_requirements,
            generate_event_mappings=request.generate_event_mappings
        )
        
        # 6. 保存生成的章节大纲到数据库
        if response.success:
            print(f"📝 开始保存 {len(response.chapters)} 个章节大纲到数据库...")
            for i, chapter in enumerate(response.chapters):
                print(f"📝 保存章节 {i+1}/{len(response.chapters)}: {chapter.id}")
                try:
                    result = chapter_database.save_chapter_outline(chapter)
                    if result:
                        print(f"✅ 章节 {chapter.id} 保存成功")
                    else:
                        print(f"❌ 章节 {chapter.id} 保存失败")
                except Exception as e:
                    print(f"❌ 保存章节 {chapter.id} 时出错: {e}")
                    import traceback
                    traceback.print_exc()
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chapter-outlines", response_model=List[ChapterOutline])
async def get_all_chapter_outlines():
    """获取所有章节大纲"""
    try:
        chapters = chapter_database.get_all_chapter_outlines()
        return chapters
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chapter-outlines/{plot_id}", response_model=List[ChapterOutline])
async def get_chapter_outlines(plot_id: str):
    """获取指定剧情大纲的所有章节大纲"""
    try:
        chapters = chapter_database.get_chapters_by_plot(plot_id)
        return chapters
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chapter-outlines/single/{chapter_id}", response_model=ChapterOutline)
async def get_chapter_outline(chapter_id: str):
    """获取单个章节大纲"""
    try:
        chapter = chapter_database.get_chapter_outline(chapter_id)
        if not chapter:
            raise HTTPException(status_code=404, detail="章节大纲不存在")
        return chapter
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/chapter-outlines/{chapter_id}", response_model=ChapterOutline)
async def update_chapter_outline(chapter_id: str, request: dict):
    """更新章节大纲"""
    try:
        # 先获取现有的章节大纲数据
        existing_chapter = chapter_database.get_chapter_outline(chapter_id)
        if not existing_chapter:
            raise HTTPException(status_code=404, detail="章节大纲不存在")
        
        # 将现有数据转换为字典，并更新传入的字段
        existing_data = existing_chapter.dict()
        existing_data.update(request)
        
        # 处理时间字段
        if 'updated_at' in existing_data:
            from datetime import datetime
            existing_data['updated_at'] = datetime.now()
        
        if 'created_at' in existing_data and isinstance(existing_data['created_at'], str):
            from datetime import datetime
            try:
                existing_data['created_at'] = datetime.fromisoformat(existing_data['created_at'].replace('Z', '+00:00'))
            except ValueError:
                existing_data['created_at'] = datetime.now()
        
        # 创建ChapterOutline对象
        chapter_outline = ChapterOutline(**existing_data)
        chapter_outline.id = chapter_id
        
        success = chapter_database.update_chapter_outline(chapter_id, chapter_outline)
        if not success:
            raise HTTPException(status_code=500, detail="更新失败")
        
        # 返回更新后的章节大纲
        updated_chapter = chapter_database.get_chapter_outline(chapter_id)
        if not updated_chapter:
            raise HTTPException(status_code=404, detail="章节大纲不存在")
        
        return updated_chapter
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/chapter-outlines/{chapter_id}")
async def delete_chapter_outline(chapter_id: str):
    """删除章节大纲"""
    try:
        success = chapter_database.delete_chapter_outline(chapter_id)
        if success:
            return {"message": "章节大纲删除成功"}
        else:
            raise HTTPException(status_code=400, detail="无法删除章节大纲：存在关联的详细剧情，请先删除所有详细剧情")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chapter-outlines/generate-by-template", response_model=ChapterOutline)
async def generate_chapter_by_template(
    plot_outline_id: str,
    chapter_number: int,
    template_id: str
):
    """使用指定模板生成章节"""
    try:
        chapter = await chapter_engine.generate_chapter_by_template(
            plot_outline_id, chapter_number, template_id
        )
        return chapter
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




@router.get("/chapter-outlines/{plot_id}/stats")
async def get_chapter_outline_stats(plot_id: str):
    """获取章节大纲统计信息"""
    try:
        stats = chapter_database.get_chapter_outline_stats(plot_id)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chapter-outlines/list/{plot_id}")
async def get_chapter_outlines_list(plot_id: str, page: int = 1, page_size: int = 20):
    """获取章节大纲列表（分页）"""
    try:
        offset = (page - 1) * page_size
        chapters = chapter_database.get_chapters_by_plot(plot_id, limit=page_size, offset=offset)
        
        # 获取总数
        total_chapters = chapter_database.get_chapter_outline_stats(plot_id).get('total_chapters', 0)
        
        return {
            "chapters": chapters,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total_chapters,
                "total_pages": (total_chapters + page_size - 1) // page_size
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chapter-outlines/summary/{plot_id}")
async def get_chapter_outlines_summary(plot_id: str):
    """获取章节大纲摘要列表（用于列表页面）"""
    try:
        chapters = chapter_database.get_chapters_by_plot(plot_id, limit=100)  # 限制数量避免性能问题
        
        # 转换为摘要格式
        summaries = []
        for chapter in chapters:
            summary = {
                "id": chapter.id,
                "chapter_number": chapter.chapter_number,
                "title": chapter.title,
                "act_belonging": chapter.act_belonging,
                "core_event": chapter.core_event,
                "status": chapter.status,
                "created_at": chapter.created_at,
                "updated_at": chapter.updated_at,
                "scene_count": len(chapter.key_scenes),
                "chapter_summary": chapter.chapter_summary[:200] + "..." if len(chapter.chapter_summary) > 200 else chapter.chapter_summary
            }
            summaries.append(summary)
        
        return {
            "summaries": summaries,
            "total": len(summaries)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chapter-outlines/{plot_id}/details")
async def get_chapter_outline_details(plot_id: str):
    """获取章节大纲详细信息（包含所有相关数据）"""
    try:
        chapters = chapter_database.get_chapters_by_plot(plot_id)
        stats = chapter_database.get_chapter_outline_stats(plot_id)
        
        return {
            "chapters": chapters,
            "stats": stats,
            "total_chapters": len(chapters)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chapter-outlines/export/{plot_id}")
async def export_chapter_outlines(plot_id: str, format: str = "json"):
    """导出章节大纲数据"""
    try:
        chapters = chapter_database.get_chapters_by_plot(plot_id)
        stats = chapter_database.get_chapter_outline_stats(plot_id)
        
        export_data = {
            "plot_id": plot_id,
            "export_time": datetime.now().isoformat(),
            "statistics": stats,
            "chapters": []
        }
        
        for chapter in chapters:
            chapter_data = {
                "id": chapter.id,
                "chapter_number": chapter.chapter_number,
                "title": chapter.title,
                "worldview_elements": chapter.worldview_elements,
                "act_belonging": chapter.act_belonging,
                "chapter_summary": chapter.chapter_summary,
                "key_scenes": [
                    {
                        "scene_number": scene.scene_number,
                        "title": scene.title,
                        "description": scene.description,
                        "location": scene.location,
                        "characters_present": scene.characters_present,
                        "purpose": scene.purpose,
                        "related_events": scene.related_events
                    } for scene in chapter.key_scenes
                ],
                "plot_function": chapter.plot_function,
                "conflict_development": chapter.conflict_development,
                "writing_notes": chapter.writing_notes,
                "estimated_word_count": chapter.estimated_word_count,
                "status": chapter.status,
                "created_at": chapter.created_at.isoformat() if chapter.created_at else None,
                "updated_at": chapter.updated_at.isoformat() if chapter.updated_at else None
            }
            export_data["chapters"].append(chapter_data)
        
        return export_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chapter-outlines/batch-update")
async def batch_update_chapter_outlines(updates: List[dict]):
    """批量更新章节大纲"""
    try:
        results = []
        for update in updates:
            chapter_id = update.get('id')
            if not chapter_id:
                results.append({"id": None, "success": False, "error": "缺少章节ID"})
                continue
            
            # 这里可以添加更复杂的更新逻辑
            # 目前只是简单的示例
            try:
                # 获取现有章节
                existing_chapter = chapter_database.get_chapter_outline(chapter_id)
                if not existing_chapter:
                    results.append({"id": chapter_id, "success": False, "error": "章节不存在"})
                    continue
                
                # 更新字段
                for key, value in update.items():
                    if key != 'id' and hasattr(existing_chapter, key):
                        setattr(existing_chapter, key, value)
                
                # 保存更新
                success = chapter_database.update_chapter_outline(chapter_id, existing_chapter)
                results.append({"id": chapter_id, "success": success, "error": None if success else "更新失败"})
                
            except Exception as e:
                results.append({"id": chapter_id, "success": False, "error": str(e)})
        
        return {
            "total": len(updates),
            "successful": len([r for r in results if r["success"]]),
            "failed": len([r for r in results if not r["success"]]),
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 章节大纲相关API ====================


@router.get("/chapter-outlines/{chapter_id}/events")
async def get_chapter_events(chapter_id: str):
    """获取章节的相关事件"""
    try:
        from app.core.event_generator.event_database import EventDatabase
        event_database = EventDatabase()
        
        events = event_database.get_chapter_events(chapter_id)
        return {
            "chapter_id": chapter_id,
            "events": events,
            "total_count": len(events)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chapter-outlines/{chapter_id}/event-analysis")
async def get_chapter_event_analysis(chapter_id: str):
    """获取章节的事件分析"""
    try:
        from app.core.event_generator.event_database import EventDatabase
        event_database = EventDatabase()
        
        analysis = event_database.get_chapter_event_analysis(chapter_id)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
