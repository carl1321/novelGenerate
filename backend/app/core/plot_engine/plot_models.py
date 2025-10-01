"""
剧情大纲数据模型
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum


class PlotStatus(str, Enum):
    """剧情状态枚举"""
    DRAFT = "草稿"
    PLANNING = "规划中"
    WRITING = "写作中"
    REVIEWING = "审核中"
    COMPLETED = "已完成"


class PlotStructure(str, Enum):
    """剧情结构枚举"""
    THREE_ACT = "三幕式"
    FIVE_ACT = "五幕式"
    HERO_JOURNEY = "英雄之旅"
    FREEFORM = "自由形式"


class PlotOutline(BaseModel):
    """剧情大纲模型"""
    id: str = Field(..., description="剧情大纲ID")
    title: str = Field(..., description="剧情标题")
    description: str = Field(..., description="剧情描述")
    
    # 关联信息
    worldview_id: str = Field(..., description="关联的世界观ID")
    character_ids: List[str] = Field(default_factory=list, description="主要角色ID列表")
    
    # 剧情结构
    structure_type: PlotStructure = Field(PlotStructure.THREE_ACT, description="剧情结构类型")
    total_chapters: int = Field(20, description="总章节数")
    target_word_count: int = Field(100000, description="目标字数")
    
    # 剧情内容
    main_conflict: str = Field(..., description="主要冲突")
    theme: str = Field(..., description="主题思想")
    tone: str = Field(..., description="故事基调")
    
    # 章节大纲
    chapters: List['ChapterOutline'] = Field(default_factory=list, description="章节大纲列表")
    
    # 角色发展
    character_arcs: Dict[str, str] = Field(default_factory=dict, description="角色发展弧线")
    
    # 元数据
    status: PlotStatus = Field(PlotStatus.DRAFT, description="状态")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    created_by: Optional[str] = Field(None, description="创建者")
    
    class Config:
        use_enum_values = True


class ChapterOutline(BaseModel):
    """章节大纲模型"""
    id: str = Field(..., description="章节ID")
    plot_outline_id: str = Field(..., description="所属剧情大纲ID")
    chapter_number: int = Field(..., description="章节编号")
    title: str = Field(..., description="章节标题")
    
    # 章节内容
    summary: str = Field(..., description="章节概要")
    main_events: List[str] = Field(default_factory=list, description="主要事件")
    key_scenes: List[str] = Field(default_factory=list, description="关键场景")
    
    # 角色参与
    participating_characters: List[str] = Field(default_factory=list, description="参与角色")
    character_development: Dict[str, str] = Field(default_factory=dict, description="角色发展")
    
    # 剧情推进
    conflict_escalation: str = Field(..., description="冲突升级")
    plot_advancement: str = Field(..., description="剧情推进")
    foreshadowing: List[str] = Field(default_factory=list, description="伏笔设置")
    
    # 元数据
    estimated_word_count: int = Field(5000, description="预计字数")
    estimated_reading_time: int = Field(20, description="预计阅读时间（分钟）")
    created_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        use_enum_values = True


class PlotOutlineRequest(BaseModel):
    """剧情大纲生成请求"""
    worldview_id: str = Field(..., description="世界观ID")
    character_ids: List[str] = Field(..., description="主要角色ID列表")
    title: str = Field(..., description="剧情标题")
    description: str = Field(..., description="剧情描述")
    structure_type: PlotStructure = Field(PlotStructure.THREE_ACT, description="剧情结构类型")
    total_chapters: int = Field(20, description="总章节数")
    target_word_count: int = Field(100000, description="目标字数")
    main_conflict: str = Field(..., description="主要冲突")
    theme: str = Field(..., description="主题思想")
    tone: str = Field(..., description="故事基调")
    additional_requirements: Optional[str] = Field(None, description="额外要求")


class PlotOutlineResponse(BaseModel):
    """剧情大纲生成响应"""
    success: bool = Field(..., description="是否成功")
    plot_outline: Optional[PlotOutline] = Field(None, description="生成的剧情大纲")
    message: str = Field(..., description="响应消息")
    generation_time: float = Field(0, description="生成耗时（秒）")


# 更新模型引用
PlotOutline.model_rebuild()
ChapterOutline.model_rebuild()