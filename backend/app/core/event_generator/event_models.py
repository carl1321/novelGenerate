"""
事件数据模型
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum


class EventType(str, Enum):
    """事件类型枚举"""
    DAILY = "日常事件"
    CONFLICT = "冲突事件"
    TURNING_POINT = "转折事件"
    CULTIVATION = "修炼事件"
    SOCIAL = "社交事件"
    DANGER = "危险事件"
    DISCOVERY = "发现事件"
    ROMANCE = "感情事件"
    MYSTERY = "神秘事件"
    BATTLE = "战斗事件"


class EventImportance(str, Enum):
    """事件重要性枚举"""
    LOW = "低"
    MEDIUM = "中"
    HIGH = "高"
    CRITICAL = "关键"


class EventCategory(str, Enum):
    """事件分类枚举"""
    PLOT_DRIVING = "剧情推动"
    CHARACTER_DEVELOPMENT = "角色发展"
    WORLD_BUILDING = "世界观构建"
    RELATIONSHIP_BUILDING = "关系建立"
    CONFLICT_RESOLUTION = "冲突解决"
    FORESHADOWING = "伏笔埋设"


class Event(BaseModel):
    """事件模型"""
    id: str = Field(..., description="事件ID")
    title: str = Field(..., description="事件标题")
    description: str = Field(..., description="事件描述")
    event_type: EventType = Field(..., description="事件类型")
    importance: EventImportance = Field(..., description="事件重要性")
    category: EventCategory = Field(..., description="事件分类")
    
    # 事件内容
    setting: str = Field(..., description="事件发生地点")
    participants: List[str] = Field(default_factory=list, description="参与角色")
    duration: str = Field(..., description="事件持续时间")
    outcome: str = Field(..., description="事件结果")
    
    # 剧情相关
    plot_impact: str = Field(..., description="对剧情的影响")
    character_impact: Dict[str, str] = Field(default_factory=dict, description="对角色的影响")
    foreshadowing_elements: List[str] = Field(default_factory=list, description="伏笔元素")
    
    # 元数据
    prerequisites: List[str] = Field(default_factory=list, description="前置条件")
    consequences: List[str] = Field(default_factory=list, description="后续影响")
    tags: List[str] = Field(default_factory=list, description="标签")
    
    # 时间信息
    chapter_number: Optional[int] = Field(None, description="所属章节")
    sequence_order: int = Field(0, description="事件顺序")
    created_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        use_enum_values = True
