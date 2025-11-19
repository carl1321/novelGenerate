"""
章节大纲数据模型 - 独立模块
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum


class ChapterStatus(str, Enum):
    """章节状态枚举"""
    OUTLINE = "大纲"
    DRAFT = "草稿"
    REVISION = "修改中"
    REVIEW = "审核中"
    COMPLETED = "已完成"


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


class SceneType(str, Enum):
    """场景类型枚举"""
    ACTION = "动作场景"
    DIALOGUE = "对话场景"
    INTERNAL_MONOLOGUE = "内心独白"
    FLASHBACK = "回忆场景"
    DREAM = "梦境场景"
    BATTLE = "战斗场景"
    ROMANCE = "浪漫场景"
    COMEDY = "喜剧场景"
    SUSPENSE = "悬疑场景"
    ATMOSPHERIC = "氛围场景"


class EmotionalTone(str, Enum):
    """情感基调枚举"""
    TENSE = "紧张"
    RELAXED = "轻松"
    DRAMATIC = "戏剧性"
    MELANCHOLY = "忧郁"
    JOYFUL = "欢快"
    MYSTERIOUS = "神秘"
    ROMANTIC = "浪漫"
    HEROIC = "英雄主义"
    TRAGIC = "悲剧性"
    COMEDIC = "喜剧性"


class Scene(BaseModel):
    """场景模型 - 简化版"""
    scene_number: int = Field(..., description="场景编号")
    title: str = Field(..., description="场景标题")
    description: str = Field(..., description="场景描述")
    location: str = Field(..., description="场景地点")
    characters_present: List[str] = Field(default_factory=list, description="在场角色")
    purpose: str = Field(..., description="场景目的")
    related_events: List[str] = Field(default_factory=list, description="关联事件ID列表")


class CharacterDevelopment(BaseModel):
    """角色发展模型 - 简化版"""
    character_id: str = Field(..., description="角色ID")
    development_type: str = Field(..., description="发展类型")
    description: str = Field(..., description="发展描述")


class EventIntegration(BaseModel):
    """事件整合模型"""
    event_id: str = Field(..., description="事件ID")
    event_title: str = Field(..., description="事件标题")
    integration_type: str = Field(..., description="整合类型：主要事件/次要事件")
    chapter_position: float = Field(..., description="在章节中的位置比例 (0.0-1.0)")


class ForeshadowingItem(BaseModel):
    """伏笔项目模型"""
    content: str = Field(..., description="伏笔内容")
    type: str = Field(..., description="伏笔类型")
    expected_resolution_chapter: int = Field(..., description="预计回收章节")


class ChapterOutline(BaseModel):
    """章节大纲模型 - 简化版（基于事件驱动）"""
    id: str = Field(..., description="章节ID")
    plot_outline_id: str = Field(..., description="关联的剧情大纲ID")
    chapter_number: int = Field(..., description="章节编号")
    title: str = Field(..., description="章节标题")
    
    # 章节定位
    story_position: float = Field(..., description="在故事中的位置比例 (0.0-1.0)")
    act_belonging: str = Field(..., description="所属幕次")
    
    # 章节内容
    chapter_summary: str = Field(..., description="章节概要")
    key_scenes: List[Scene] = Field(default_factory=list, description="关键场景")
    character_appearances: List[str] = Field(default_factory=list, description="出场角色")
    
    # 剧情功能
    plot_function: PlotFunction = Field(..., description="剧情功能")
    conflict_development: str = Field(..., description="冲突发展")
    character_development: List[CharacterDevelopment] = Field(default_factory=list, description="角色发展")
    
    # 写作指导
    writing_notes: str = Field(..., description="写作指导")
    
    # 情感和氛围
    emotional_tone: EmotionalTone = Field(..., description="情感基调")
    atmosphere: str = Field(..., description="氛围描述")
    tension_level: int = Field(default=5, description="紧张程度 (1-10)")
    
    # 世界观元素
    worldview_elements: List[str] = Field(default_factory=list, description="涉及的世界观元素")
    
    # 事件整合
    event_integrations: List[EventIntegration] = Field(default_factory=list, description="事件整合信息")
    
    # 元数据
    estimated_word_count: int = Field(default=5000, description="预计字数")
    status: ChapterStatus = Field(ChapterStatus.OUTLINE, description="章节状态")
    
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        use_enum_values = True


class ChapterTemplate(BaseModel):
    """章节模板模型"""
    template_id: str = Field(..., description="模板ID")
    template_name: str = Field(..., description="模板名称")
    plot_function: PlotFunction = Field(..., description="适用剧情功能")
    structure: List[str] = Field(default_factory=list, description="结构要点")
    scene_types: List[SceneType] = Field(default_factory=list, description="推荐场景类型")
    emotional_tone: EmotionalTone = Field(..., description="推荐情感基调")
    writing_tips: List[str] = Field(default_factory=list, description="写作建议")


class ChapterOutlineRequest(BaseModel):
    """章节大纲生成请求 - 事件驱动版"""
    plot_outline_id: str = Field(..., description="剧情大纲ID")
    worldview_id: Optional[str] = Field(None, description="世界观ID")
    chapter_count: int = Field(default=5, description="要生成的章节数")
    start_chapter: int = Field(default=1, description="起始章节号")
    
    # 事件选择策略
    event_selection_strategy: str = Field(
        default="auto",
        description="事件选择策略：auto/手动指定"
    )
    selected_events: Optional[List[str]] = Field(
        default=None,
        description="指定的事件ID列表"
    )
    
    # 角色重点
    character_focus: Optional[List[str]] = Field(
        default=None,
        description="重点角色ID列表"
    )
    
    # 额外要求
    additional_requirements: Optional[str] = Field(
        default="",
        description="额外要求"
    )


class ChapterOutlineResponse(BaseModel):
    """章节大纲生成响应"""
    success: bool = Field(..., description="是否成功")
    chapters: List[ChapterOutline] = Field(default_factory=list, description="生成的章节大纲")
    message: str = Field(..., description="响应消息")
    generation_time: float = Field(0, description="生成耗时（秒）")


# 更新模型引用
ChapterOutline.model_rebuild()
Scene.model_rebuild()
CharacterDevelopment.model_rebuild()
