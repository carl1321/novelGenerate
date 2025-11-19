"""
事件相关API端点
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
import time
import uuid

from app.core.event_generator.event_generator import EventGenerator
from app.core.event_generator.event_models import Event, EventType, EventImportance, EventCategory, SimpleEvent
from app.core.event_generator.event_database import EventDatabase
from app.core.event_generator.event_scoring_agent import EventScoringAgent, EventScore
from app.core.event_generator.event_evolution_agent import EventEvolutionAgent
from app.core.plot_engine.plot_database import PlotOutlineDatabase
from app.core.world.database import WorldViewDatabase
from app.core.character.database import CharacterDatabase
from app.utils.llm_client import get_llm_client

router = APIRouter()

# 初始化数据库和生成器
event_generator = EventGenerator()
event_database = EventDatabase()
plot_database = PlotOutlineDatabase()
worldview_database = WorldViewDatabase()
character_database = CharacterDatabase()
llm_client = get_llm_client()
scoring_agent = EventScoringAgent(llm_client)
evolution_agent = EventEvolutionAgent(llm_client)


class EventRequest(BaseModel):
    """事件生成请求"""
    worldview_id: Optional[str] = None
    plot_outline_id: Optional[str] = None
    event_requirements: str = ""


class EnhancedEventRequest(BaseModel):
    """增强的事件生成请求（优化版）"""
    plot_outline_id: str
    worldview_id: Optional[str] = None
    importance_distribution: Optional[dict] = None  # {"重大事件": 3, "重要事件": 5, "普通事件": 10, "特殊事件": 2}
    event_requirements: str = ""
    generate_chapter_integration: bool = True  # 是否生成章节融入信息
    selected_act: Optional[dict] = None  # 选中的幕次信息
    character_ids: Optional[List[str]] = None  # 指定角色ID列表
    story_tone: Optional[str] = None  # 故事基调
    narrative_structure: Optional[str] = None  # 叙事结构


class EventResponse(BaseModel):
    """事件生成响应"""
    success: bool
    events: List[Event]
    message: str
    generation_time: float


class SimpleEventResponse(BaseModel):
    """简化事件生成响应"""
    success: bool
    events: List[SimpleEvent]
    message: str
    generation_time: float


@router.get("/events", response_model=List[Event])
async def get_all_events():
    """获取所有事件列表"""
    try:
        events = event_database.get_all_events()
        return events
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/events/{plot_outline_id}/with-scores")
async def get_events_with_scores(plot_outline_id: str):
    """根据剧情大纲ID获取带评分的事件列表（只显示最新版本）"""
    try:
        # 获取所有事件的最新版本
        events = event_database.get_latest_versions_by_plot(plot_outline_id)
        
        # 为每个事件添加评分信息
        events_with_scores = []
        for event in events:
            # 获取最新评分
            latest_score_data = event_database.get_latest_event_score_with_id(event.id)
            
            # 创建事件字典并添加评分
            event_dict = event.dict() if hasattr(event, 'dict') else event.__dict__
            if latest_score_data:
                event_dict['latest_score'] = {
                    'protagonist_involvement': latest_score_data['protagonist_involvement'],
                    'plot_coherence': latest_score_data['plot_coherence'],
                    'writing_quality': latest_score_data['writing_quality'],
                    'dramatic_tension': latest_score_data['dramatic_tension'],
                    'overall_quality': latest_score_data['overall_quality'],
                    'feedback': latest_score_data['feedback'],
                    'strengths': latest_score_data['strengths'],
                    'weaknesses': latest_score_data['weaknesses']
                }
            else:
                event_dict['latest_score'] = None
            
            events_with_scores.append(event_dict)
        
        return events_with_scores
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/events/plot/{plot_outline_id}/acts")
async def get_plot_acts(plot_outline_id: str):
    """获取剧情大纲的幕次信息"""
    try:
        plot_outline = plot_database.get_plot_outline(plot_outline_id)
        if not plot_outline:
            raise HTTPException(status_code=404, detail="剧情大纲不存在")
        
        # 返回幕次信息
        acts = []
        if hasattr(plot_outline, 'acts') and plot_outline.acts:
            for act in plot_outline.acts:
                acts.append({
                    "act_number": act.act_number,
                    "act_name": act.act_name,
                    "core_mission": act.core_mission,
                    "daily_events": act.daily_events,
                    "conflict_events": act.conflict_events,
                    "special_events": act.special_events,
                    "major_events": act.major_events,
                    "stage_result": act.stage_result
                })
        
        return {
            "plot_title": plot_outline.title,
            "story_tone": getattr(plot_outline, 'story_tone', ''),
            "narrative_structure": getattr(plot_outline, 'narrative_structure', ''),
            "acts": acts
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 注意：这个路由需要在更具体的路由之后定义，避免路径冲突
# @router.get("/events/{plot_outline_id}/{chapter_number}", response_model=List[Event])
# async def get_events_by_chapter(plot_outline_id: str, chapter_number: int):
#     """根据剧情大纲ID和章节号获取事件列表"""
#     try:
#         events = event_database.get_events_by_chapter(chapter_number, plot_outline_id)
#         return events
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


@router.put("/events/{event_id}")
async def update_event(event_id: str, event_data: dict):
    """更新事件"""
    try:
        # 检查事件是否存在
        existing_event = event_database.get_event(event_id)
        if not existing_event:
            raise HTTPException(status_code=404, detail="事件不存在")
        
        # 过滤掉不应该更新的字段，只允许更新描述和结果
        filtered_data = {}
        allowed_fields = ['description', 'outcome']
        
        for field, value in event_data.items():
            if field in allowed_fields and value is not None:
                filtered_data[field] = value
        
        if not filtered_data:
            raise HTTPException(status_code=400, detail="没有有效的更新字段")
        
        # 更新事件
        success = event_database.update_event(event_id, filtered_data)
        if success:
            return {"success": True, "message": "事件更新成功"}
        else:
            raise HTTPException(status_code=500, detail="事件更新失败")
    except HTTPException:
        raise
    except Exception as e:
        print(f"更新事件异常: {e}")
        raise HTTPException(status_code=500, detail=f"事件更新失败: {str(e)}")


@router.delete("/events/{event_id}")
async def delete_event(event_id: str, version: Optional[int] = None):
    """删除事件
    - 如果指定版本号：只删除该版本
    - 如果未指定版本号：删除整个事件的所有版本
    """
    try:
        success = event_database.delete_event_version(event_id, version)
        if success:
            if version:
                return {"success": True, "message": f"事件版本 v{version} 删除成功"}
            else:
                return {"success": True, "message": "事件删除成功"}
        else:
            raise HTTPException(status_code=404, detail="事件不存在")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 新增：增强的事件API ====================

@router.post("/events/enhanced", response_model=EventResponse)
async def create_enhanced_events(request: EnhancedEventRequest):
    """生成增强事件（支持重要性分级和章节关联）"""
    start_time = time.time()
    
    try:
        # 1. 获取剧情大纲信息
        plot_outline = plot_database.get_plot_outline(request.plot_outline_id)
        if not plot_outline:
            raise HTTPException(status_code=404, detail="剧情大纲不存在")
        
        # 2. 获取世界观信息
        world_view = None
        if request.worldview_id:
            world_view = worldview_database.get_worldview(request.worldview_id)
            if not world_view:
                raise HTTPException(status_code=404, detail="世界观不存在")
        else:
            # 如果没有指定世界观ID，从剧情大纲中获取
            worldview_id = plot_outline.worldview_id
            world_view = worldview_database.get_worldview(worldview_id)
            if not world_view:
                raise HTTPException(status_code=404, detail=f"剧情大纲关联的世界观不存在: {worldview_id}")
        
        # 3. 获取角色信息（支持指定角色或自动分配）
        characters = []
        if request.character_ids:
            # 使用指定的角色ID列表
            characters = character_database.get_characters_by_ids(request.character_ids)
        elif world_view:
            # 自动分配世界观下的角色
            if isinstance(world_view, dict):
                worldview_id = world_view.get("worldview_id", "")
            else:
                worldview_id = getattr(world_view, "worldview_id", "")
            characters = character_database.get_characters_by_worldview(worldview_id)
        
        for i, char in enumerate(characters):
            if isinstance(char, dict):
                name = char.get('name', '未知角色')
                role_type = char.get('role_type', '未知')
            else:
                name = getattr(char, 'name', '未知角色')
                role_type = getattr(char, 'role_type', '未知')
        
        # 4. 设置重要性分布
        importance_distribution = request.importance_distribution or {
            "重大事件": 3,
            "重要事件": 5, 
            "普通事件": 10,
            "特殊事件": 2
        }
        
        # 5. 生成增强事件
        events = await event_generator.generate_enhanced_events(
            plot_outline=plot_outline,
            world_view=world_view or {},
            characters=characters,
            importance_distribution=importance_distribution,
            event_requirements=request.event_requirements,
            generate_chapter_integration=request.generate_chapter_integration,
            selected_act=request.selected_act,
            story_tone=request.story_tone or getattr(plot_outline, 'story_tone', ''),
            narrative_structure=request.narrative_structure or getattr(plot_outline, 'narrative_structure', ''),
            save_to_database=True
        )
        
        generation_time = time.time() - start_time
        
        return EventResponse(
            success=True,
            events=events,
            message=f"成功生成{len(events)}个增强事件",
            generation_time=generation_time
        )
        
    except Exception as e:
        generation_time = time.time() - start_time
        return EventResponse(
            success=False,
            events=[],
            message=f"增强事件生成失败: {str(e)}",
            generation_time=generation_time
        )


@router.get("/events/by-importance/{plot_outline_id}")
async def get_events_by_importance(plot_outline_id: str):
    """根据剧情大纲ID按重要性分组获取事件"""
    try:
        # 检查剧情大纲是否存在
        plot_outline = plot_database.get_plot_outline(plot_outline_id)
        if not plot_outline:
            raise HTTPException(status_code=404, detail="剧情大纲不存在")
        
        # 获取按重要性分组的事件
        events_by_importance = event_database.get_events_by_importance_group(plot_outline_id)
        
        return {
            "plot_outline_id": plot_outline_id,
            "plot_title": plot_outline.get("title", ""),
            "events_by_importance": events_by_importance,
            "total_events": sum(len(events) for events in events_by_importance.values())
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/events/stats/{plot_outline_id}")
async def get_event_statistics(plot_outline_id: str):
    """获取事件统计信息"""
    try:
        stats = event_database.get_event_statistics(plot_outline_id)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/events/{plot_outline_id}/chapter-integration")
async def get_events_with_chapter_integration(plot_outline_id: str):
    """获取带有章节融入信息的事件列表"""
    try:
        events = event_database.get_events_with_chapter_integration(plot_outline_id)
        return events
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/events/generate-with-act", response_model=EventResponse)
async def generate_events_with_act_selection(request: EnhancedEventRequest):
    """根据选中的幕次生成事件（优化版）"""
    start_time = time.time()
    
    try:
        # 1. 获取剧情大纲信息
        plot_outline = plot_database.get_plot_outline(request.plot_outline_id)
        if not plot_outline:
            raise HTTPException(status_code=404, detail="剧情大纲不存在")
        
        # 2. 获取世界观信息
        world_view = None
        if request.worldview_id:
            world_view = worldview_database.get_worldview(request.worldview_id)
            if not world_view:
                raise HTTPException(status_code=404, detail="世界观不存在")
        else:
            # 如果没有指定世界观ID，从剧情大纲中获取
            worldview_id = plot_outline.worldview_id
            world_view = worldview_database.get_worldview(worldview_id)
            if not world_view:
                raise HTTPException(status_code=404, detail=f"剧情大纲关联的世界观不存在: {worldview_id}")
        
        # 3. 获取角色信息（支持指定角色或自动分配）
        characters = []
        if request.character_ids:
            characters = character_database.get_characters_by_ids(request.character_ids)
        elif world_view:
            characters = character_database.get_characters_by_worldview(world_view.get("worldview_id", ""))
        
        # 4. 设置重要性分布
        importance_distribution = request.importance_distribution or {
            "重大事件": 3,
            "重要事件": 5, 
            "普通事件": 10,
            "特殊事件": 2
        }
        
        # 5. 生成增强事件（支持幕次选择）
        events = await event_generator.generate_enhanced_events(
            plot_outline=plot_outline,
            world_view=world_view or {},
            characters=characters,
            importance_distribution=importance_distribution,
            event_requirements=request.event_requirements,
            generate_chapter_integration=request.generate_chapter_integration,
            selected_act=request.selected_act,
            save_to_database=True
        )
        
        generation_time = time.time() - start_time
        
        return EventResponse(
            success=True,
            events=events,
            message=f"成功生成{len(events)}个事件（幕次选择模式）",
            generation_time=generation_time
        )
        
    except Exception as e:
        generation_time = time.time() - start_time
        return EventResponse(
            success=False,
            events=[],
            message=f"事件生成失败: {str(e)}",
            generation_time=generation_time
        )


@router.post("/events/simple", response_model=SimpleEventResponse)
async def generate_simple_events(request: EnhancedEventRequest):
    """生成简化事件（仅包含标题、事件类型、描述、事件结果）"""
    start_time = time.time()
    
    try:
        # 1. 获取剧情大纲信息
        plot_outline = plot_database.get_plot_outline(request.plot_outline_id)
        if not plot_outline:
            raise HTTPException(status_code=404, detail="剧情大纲不存在")
        
        # 2. 获取世界观信息
        world_view = None
        if request.worldview_id:
            world_view = worldview_database.get_worldview(request.worldview_id)
            if not world_view:
                raise HTTPException(status_code=404, detail="世界观不存在")
        else:
            # 如果没有指定世界观ID，从剧情大纲中获取
            worldview_id = plot_outline.worldview_id
            world_view = worldview_database.get_worldview(worldview_id)
            if not world_view:
                raise HTTPException(status_code=404, detail=f"剧情大纲关联的世界观不存在: {worldview_id}")
        
        # 3. 获取角色信息（支持指定角色或自动分配）
        characters = []
        if request.character_ids:
            characters = character_database.get_characters_by_ids(request.character_ids)
        elif world_view:
            characters = character_database.get_characters_by_worldview(world_view.get("worldview_id", ""))
        
        # 4. 设置重要性分布
        importance_distribution = request.importance_distribution or {
            "重大事件": 3,
            "重要事件": 5, 
            "普通事件": 10,
            "特殊事件": 2
        }
        
        # 5. 生成简化事件
        events = await event_generator.generate_simple_events(
            plot_outline=plot_outline,
            world_view=world_view or {},
            characters=characters,
            importance_distribution=importance_distribution,
            event_requirements=request.event_requirements,
            selected_act=request.selected_act
        )
        
        generation_time = time.time() - start_time
        
        return SimpleEventResponse(
            success=True,
            events=events,
            message=f"成功生成{len(events)}个简化事件",
            generation_time=generation_time
        )
        
    except Exception as e:
        generation_time = time.time() - start_time
        return SimpleEventResponse(
            success=False,
            events=[],
            message=f"简化事件生成失败: {str(e)}",
            generation_time=generation_time
        )


# ==================== 简化事件CRUD API ====================

@router.get("/events/simple/{plot_outline_id}", response_model=List[SimpleEvent])
async def get_simple_events_by_plot(plot_outline_id: str):
    """根据剧情大纲ID获取简化事件列表"""
    try:
        events = event_database.get_events_by_plot_outline(plot_outline_id)
        # 转换为SimpleEvent格式
        simple_events = []
        for event in events:
            simple_events.append(SimpleEvent(
                title=event.title,
                event_type=event.event_type,
                description=event.description,
                outcome=event.outcome
            ))
        return simple_events
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/events/simple/single/{event_id}", response_model=SimpleEvent)
async def get_simple_event_by_id(event_id: str):
    """根据ID获取简化事件"""
    try:
        event = event_database.get_event_by_id(event_id)
        if not event:
            raise HTTPException(status_code=404, detail="简化事件不存在")
        return SimpleEvent(
            title=event.title,
            event_type=event.event_type,
            description=event.description,
            outcome=event.outcome
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/events/simple", response_model=dict)
async def create_simple_event(simple_event: SimpleEvent, plot_outline_id: str, chapter_number: int = None, sequence_order: int = None):
    """创建简化事件"""
    try:
        # 如果没有指定序号，自动获取下一个可用序号
        if sequence_order is None:
            sequence_order = event_database.get_next_sequence_order(plot_outline_id)
        
        # 创建Event对象
        event = Event(
            id=f"event_{uuid.uuid4().hex[:8]}",
            title=simple_event.title,
            event_type=simple_event.event_type,
            description=simple_event.description,
            outcome=simple_event.outcome,
            plot_outline_id=plot_outline_id,
            chapter_number=chapter_number,
            sequence_order=sequence_order
        )
        
        success = event_database.save_event(event)
        if success:
            return {"success": True, "message": "简化事件创建成功"}
        else:
            raise HTTPException(status_code=500, detail="简化事件创建失败")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/events/simple/{event_id}", response_model=dict)
async def update_simple_event(event_id: str, simple_event: SimpleEvent):
    """更新简化事件"""
    try:
        # 检查事件是否存在
        existing_event = simple_event_database.get_simple_event_by_id(event_id)
        if not existing_event:
            raise HTTPException(status_code=404, detail="简化事件不存在")
        
        success = simple_event_database.update_simple_event(event_id, simple_event)
        if success:
            return {"success": True, "message": "简化事件更新成功"}
        else:
            raise HTTPException(status_code=500, detail="简化事件更新失败")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/events/simple/{event_id}", response_model=dict)
async def delete_simple_event(event_id: str):
    """删除简化事件"""
    try:
        success = simple_event_database.delete_simple_event(event_id)
        if success:
            return {"success": True, "message": "简化事件删除成功"}
        else:
            raise HTTPException(status_code=404, detail="简化事件不存在")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/events/simple/{plot_outline_id}/paginated")
async def get_simple_events_paginated(plot_outline_id: str, page: int = 1, page_size: int = 20):
    """分页获取简化事件列表"""
    try:
        result = simple_event_database.get_simple_events_paginated(plot_outline_id, page, page_size)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/events/simple/{plot_outline_id}/search")
async def search_simple_events(plot_outline_id: str, q: str):
    """搜索简化事件"""
    try:
        events = simple_event_database.search_simple_events(plot_outline_id, q)
        return {
            "events": events,
            "total": len(events),
            "search_term": q
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/events/simple/{plot_outline_id}/stats")
async def get_simple_events_stats(plot_outline_id: str):
    """获取简化事件统计信息"""
    try:
        stats = event_database.get_simple_events_stats(plot_outline_id)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 事件评分与进化API ====================

class EventScoreResponse(BaseModel):
    """事件评分响应"""
    success: bool
    score: Optional[dict] = None  # 改为dict类型以包含id字段
    message: str = ""


class EventEvolutionResponse(BaseModel):
    """事件进化响应"""
    success: bool
    evolved_event: Optional[Event] = None
    message: str = ""


class EvolutionHistoryResponse(BaseModel):
    """进化历史响应"""
    success: bool
    history: List[dict] = []
    message: str = ""


@router.post("/events/{event_id}/score", response_model=EventScoreResponse)
async def score_event(event_id: str):
    """对指定事件进行评分（自动获取最新版本）"""
    try:
        print(f"🎯 开始对事件 {event_id} 进行评分...")
        
        # 1. 获取事件详情（优先显示最新进化版本）
        event_detail_response = await get_event_detail(event_id)
        latest_event = event_detail_response["event"]
        
        print(f"📊 将对最新版本进行评分: {latest_event.title}")
        
        # 2. 调用评分智能体对最新版本进行评分（直接传入事件对象）
        score = await scoring_agent.score_event(latest_event)
        
        # 3. 将EventScore对象转换为字典
        score_dict = {
            "protagonist_involvement": score.protagonist_involvement,
            "plot_coherence": score.plot_coherence,
            "writing_quality": score.writing_quality,
            "dramatic_tension": score.dramatic_tension,
            "overall_quality": score.overall_quality,
            "feedback": score.feedback,
            "strengths": score.strengths,
            "weaknesses": score.weaknesses
        }
        
        return EventScoreResponse(
            success=True,
            score=score_dict,
            message="事件评分完成"
        )
    except Exception as e:
        print(f"❌ 事件评分失败: {e}")
        raise HTTPException(status_code=500, detail=f"事件评分失败: {str(e)}")


@router.get("/events/{event_id}/scores", response_model=List[EventScore])
async def get_event_scores(event_id: str):
    """获取事件的所有评分历史"""
    try:
        scores = scoring_agent.get_event_scores(event_id)
        return scores
    except Exception as e:
        print(f"❌ 获取事件评分历史失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取评分历史失败: {str(e)}")


@router.get("/events/{event_id}/latest-score", response_model=EventScoreResponse)
async def get_latest_event_score(event_id: str):
    """获取事件的最新评分"""
    try:
        score_data = scoring_agent.get_latest_score_with_id(event_id)
        if score_data:
            return EventScoreResponse(
                success=True,
                score=score_data,
                message="获取最新评分成功"
            )
        else:
            return EventScoreResponse(
                success=False,
                score=None,
                message="该事件暂无评分记录"
            )
    except Exception as e:
        print(f"❌ 获取最新评分失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取最新评分失败: {str(e)}")

@router.get("/events/{event_id}")
async def get_event(event_id: str):
    """获取单个事件（兼容性API）"""
    try:
        # 直接调用get_event_detail，返回事件对象
        event_detail_response = await get_event_detail(event_id)
        return event_detail_response["event"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/events/{event_id}/detail")
async def get_event_detail(event_id: str):
    """获取事件详情，优先显示最新进化内容"""
    try:
        # 1. 获取事件的最新版本
        latest_event = event_database.get_latest_event_version(event_id)
        if not latest_event:
            raise HTTPException(status_code=404, detail="事件不存在")
        
        # 2. 获取进化次数
        all_versions = event_database.get_event_all_versions(event_id)
        evolution_count = max(0, len(all_versions) - 1)  # 确保不为负数
        
        # 3. 判断是否为进化版本
        is_evolved = evolution_count > 0
        
        return {
            "event": latest_event,
            "is_evolved": is_evolved,
            "original_event_id": event_id,
            "evolution_count": evolution_count,
            "current_version": latest_event.version if hasattr(latest_event, 'version') else 1
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/events/{event_id}/evolution-history")
async def get_evolution_history(event_id: str):
    """获取事件进化历史，用于对比展示"""
    try:
        # 1. 获取原始事件
        original_event = event_database.get_event_by_id(event_id)
        if not original_event:
            raise HTTPException(status_code=404, detail="事件不存在")
        
        # 2. 获取所有进化版本
        evolution_versions = event_database.get_event_all_evolution_versions(event_id)
        
        # 3. 构建版本链：原始版本 + 进化版本
        versions = []
        
        # 添加原始版本（版本0）
        original_event.metadata = original_event.metadata or {}
        original_event.metadata.update({
            'version': 0,
            'is_original': True,
            'evolution_id': None,
            'evolution_reason': None,
            'score_id': None,
            'parent_version_id': None
        })
        versions.append(original_event)
        
        # 添加进化版本
        for evolution_event in evolution_versions:
            versions.append(evolution_event)
        
        # 按版本号排序
        versions.sort(key=lambda x: x.metadata.get('version', 0))
        
        # 4. 构建对比数据
        comparison_data = {
            "original_event_id": event_id,
            "versions": versions,
            "total_versions": len(versions),
            "has_evolution": len(evolution_versions) > 0
        }
        
        # 5. 如果有进化版本，提供最新版本和上一版本的对比
        if len(evolution_versions) > 0:
            latest_version = versions[-1]  # 最新版本
            previous_version = versions[-2] if len(versions) > 1 else versions[0]  # 上一版本（如果没有上一版本，取原始版本）
            
            comparison_data.update({
                "latest_version": latest_version,
                "previous_version": previous_version,
                "can_compare": True
            })
        else:
            comparison_data.update({
                "latest_version": original_event,
                "previous_version": None,
                "can_compare": False
            })
        
        return comparison_data
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ 获取进化历史失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取进化历史失败: {str(e)}")


@router.post("/events/{event_id}/evolve", response_model=EventEvolutionResponse)
async def evolve_event(event_id: str, score_id: int = Query(...), custom_description: str = Query("")):
    """根据评分结果进化事件"""
    try:
        print(f"🔄 开始进化事件 {event_id}，基于评分 {score_id}...")
        
        # 1. 获取原始事件
        original_event = event_database.get_event(event_id)
        if not original_event:
            raise HTTPException(status_code=404, detail="原始事件不存在")
        
        # 2. 调用进化智能体
        evolved_event = await evolution_agent.evolve_event(event_id, score_id, custom_description)
        
        # 3. 保存进化历史
        event_database.save_evolution_history(event_id, evolved_event.id, score_id)
        
        return EventEvolutionResponse(
            success=True,
            evolved_event=evolved_event,
            message="事件进化完成"
        )
    except Exception as e:
        print(f"❌ 事件进化失败: {e}")
        raise HTTPException(status_code=500, detail=f"事件进化失败: {str(e)}")


@router.get("/events/{event_id}/evolution-history", response_model=EvolutionHistoryResponse)
async def get_event_evolution_history(event_id: str):
    """获取事件的进化历史"""
    try:
        history = evolution_agent.get_evolution_history(event_id)
        return EvolutionHistoryResponse(
            success=True,
            history=history,
            message="获取进化历史成功"
        )
    except Exception as e:
        print(f"❌ 获取进化历史失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取进化历史失败: {str(e)}")


@router.post("/events/{original_event_id}/accept-evolution/{evolved_event_id}")
async def accept_evolution(original_event_id: str, evolved_event_id: str):
    """接受进化结果，将进化后的事件替换原始事件"""
    try:
        print(f"✅ 接受进化结果: {original_event_id} -> {evolved_event_id}")
        
        success = evolution_agent.accept_evolution(original_event_id, evolved_event_id)
        
        if success:
            return {"success": True, "message": "进化结果已接受，事件已更新"}
        else:
            return {"success": False, "message": "接受进化结果失败"}
    except Exception as e:
        print(f"❌ 接受进化结果失败: {e}")
        raise HTTPException(status_code=500, detail=f"接受进化结果失败: {str(e)}")


@router.post("/events/{evolved_event_id}/reject-evolution")
async def reject_evolution(evolved_event_id: str):
    """拒绝进化结果，删除进化后的事件"""
    try:
        print(f"❌ 拒绝进化结果: {evolved_event_id}")
        
        success = evolution_agent.reject_evolution(evolved_event_id)
        
        if success:
            return {"success": True, "message": "进化结果已拒绝，进化后的事件已删除"}
        else:
            return {"success": False, "message": "拒绝进化结果失败"}
    except Exception as e:
        print(f"❌ 拒绝进化结果失败: {e}")
        raise HTTPException(status_code=500, detail=f"拒绝进化结果失败: {str(e)}")


@router.get("/events/scoring-statistics")
async def get_scoring_statistics():
    """获取评分统计信息"""
    try:
        stats = event_database.get_scoring_statistics()
        return {"success": True, "statistics": stats}
    except Exception as e:
        print(f"❌ 获取评分统计信息失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取评分统计信息失败: {str(e)}")


@router.get("/events/evolution-statistics")
async def get_evolution_statistics():
    """获取进化统计信息"""
    try:
        stats = event_database.get_evolution_statistics()
        return {"success": True, "statistics": stats}
    except Exception as e:
        print(f"❌ 获取进化统计信息失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取进化统计信息失败: {str(e)}")
