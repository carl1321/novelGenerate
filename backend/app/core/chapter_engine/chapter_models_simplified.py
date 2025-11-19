"""
章节大纲模型 - 简化版（基于事件驱动）
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum


class PlotFunction(str, Enum):
    """剧情功能枚举"""
    EXPOSITION = "背景介绍"
    INCITING_INCIDENT = "引发事件"
    RISING_ACTION = "上升行动"
    CLIMAX = "高潮"
    FALLING_ACTION = "回落行动"
    RESOLUTION = "结局"
    CHARACTER_DEVELOPMENT = "角色发展"
    WORLD_BUILDING = "世界观构建"
    FORESHADOWING = "伏笔设置"
    CALLBACK = "呼应前文"
    TRANSITION = "过渡"


class ChapterStatus(str, Enum):
    """章节状态枚举"""
    OUTLINE = "大纲"
    DRAFT = "草稿"
    COMPLETED = "已完成"


class Scene(BaseModel):
    """场景模型 - 精简版"""
    scene_title: str = Field(default="", description="场景标题")
    scene_description: str = Field(default="", description="场景描述")


class ChapterOutline(BaseModel):
    """章节大纲模型 - 事件驱动版"""
    id: str = Field(..., description="章节ID")
    plot_outline_id: str = Field(..., description="关联的剧情大纲ID")
    chapter_number: int = Field(..., description="章节编号")
    title: str = Field(..., description="章节标题")
    
    # 章节定位
    act_belonging: str = Field(..., description="所属幕次")
    
    # 章节内容
    chapter_summary: str = Field(..., description="章节概要")
    core_event: str = Field(default="", description="核心事件ID")
    key_scenes: List[Scene] = Field(default_factory=list, description="关键场景")
    
    # 元数据
    status: ChapterStatus = Field(ChapterStatus.OUTLINE, description="章节状态")
    
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        use_enum_values = True


class ChapterOutlineRequest(BaseModel):
    """章节大纲生成请求"""
    plot_outline_id: str = Field(..., description="剧情大纲ID")
    worldview_id: Optional[str] = Field(None, description="世界观ID")
    character_ids: Optional[List[str]] = Field(None, description="角色ID列表")
    event_integration_mode: str = Field("auto", description="事件整合模式")
    chapter_count: int = Field(5, description="章节数量")
    start_chapter: int = Field(1, description="起始章节")
    act_belonging: Optional[str] = Field(None, description="所属幕次")
    additional_requirements: str = Field("", description="额外要求")
    generate_event_mappings: bool = Field(True, description="是否生成事件-章节映射")


class EnhancedChapterRequest(BaseModel):
    """增强章节大纲生成请求"""
    plot_outline_id: str = Field(..., description="剧情大纲ID")
    worldview_id: Optional[str] = Field(None, description="世界观ID")
    character_ids: Optional[List[str]] = Field(None, description="角色ID列表")
    event_integration_mode: str = Field("auto", description="事件整合模式")
    chapter_count: int = Field(5, description="章节数量")
    start_chapter: int = Field(1, description="起始章节")
    act_belonging: Optional[str] = Field(None, description="所属幕次")
    additional_requirements: str = Field("", description="额外要求")
    generate_event_mappings: bool = Field(True, description="是否生成事件-章节映射")


class ChapterOutlineResponse(BaseModel):
    """章节大纲生成响应"""
    success: bool = Field(..., description="是否成功")
    chapters: List[ChapterOutline] = Field(default_factory=list, description="生成的章节列表")
    message: str = Field(..., description="响应消息")
    generation_time: float = Field(0.0, description="生成耗时（秒）")
