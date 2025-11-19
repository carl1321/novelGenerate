"""
事件数据模型
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum


# EventType 改为字符串类型，不再使用枚举
EventType = str


class EventImportance(str, Enum):
    """事件重要性枚举 - 增强版"""
    NORMAL = "普通事件"      # 日常情节，角色塑造
    IMPORTANT = "重要事件"   # 影响角色关系或局部情节发展
    MAJOR = "重大事件"       # 影响故事主线，推动主角命运转折
    SPECIAL = "特殊事件"     # 独特情节元素，如奇遇、发现等
    # 保留原有枚举值以兼容
    LOW = "低"
    MEDIUM = "中"
    HIGH = "高"
    CRITICAL = "关键"
    
    # 新增LLM返回的重要性级别
    MAJOR_SIMPLE = "重大"
    IMPORTANT_SIMPLE = "重要"


# EventCategory 改为字符串类型，不再使用枚举
EventCategory = str


class Event(BaseModel):
    """事件模型 - 优化版（支持新的输入输出格式）"""
    id: str = Field(..., description="事件ID")
    title: str = Field(..., description="事件标题")
    event_type: EventType = Field(..., description="事件类型")
    description: str = Field(..., description="事件描述")
    outcome: str = Field(..., description="事件结果，包含角色影响和核心分歧的详细描述")
    
    # 版本管理字段
    version: int = Field(default=1, description="事件版本号")
    is_current_version: bool = Field(default=True, description="是否为当前版本")
    
    # 事件内容
    setting: str = Field(..., description="事件发生地点")
    participants: List[str] = Field(default_factory=list, description="参与角色")
    duration: str = Field(..., description="事件持续时间")
    
    # 剧情相关
    plot_impact: str = Field(..., description="对剧情的影响")
    foreshadowing_elements: List[str] = Field(default_factory=list, description="伏笔元素")
    
    # 核心字段
    dramatic_tension: int = Field(..., description="戏剧张力 (1-10)")
    emotional_impact: int = Field(..., description="情感冲击 (1-10)")
    
    # 时间信息
    chapter_number: Optional[int] = Field(None, description="所属章节")
    sequence_order: int = Field(0, description="事件顺序")
    plot_outline_id: Optional[str] = Field(None, description="所属剧情大纲ID")
    story_position: Optional[float] = Field(None, description="在整体故事中的位置比例 (0-1)")
    
    # 兼容字段（保留以支持现有代码）
    character_impact: Optional[Dict[str, Any]] = Field(None, description="角色影响（兼容字段）")
    conflict_core: Optional[str] = Field(None, description="核心矛盾（兼容字段）")
    logical_consistency: Optional[str] = Field(None, description="逻辑一致性（兼容字段）")
    realistic_elements: Optional[str] = Field(None, description="现实元素（兼容字段）")
    
    # 元数据字段
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="扩展元数据")
    
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = Field(None, description="更新时间")
    
    class Config:
        use_enum_values = True


class SimpleEvent(BaseModel):
    """简化事件模型 - 仅包含核心字段"""
    title: str = Field(..., description="事件标题")
    event_type: str = Field(..., description="事件类型")
    description: str = Field(..., description="事件描述")
    outcome: str = Field(..., description="事件结果")
    
    class Config:
        use_enum_values = True
