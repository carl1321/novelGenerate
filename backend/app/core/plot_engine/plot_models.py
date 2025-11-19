"""
剧情大纲数据模型 - 简化版故事驱动模式
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any, Union
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
    CIRCULAR = "环形结构"
    PARALLEL = "平行结构"


class ConflictType(str, Enum):
    """冲突类型枚举"""
    MAN_VS_MAN = "人与人"
    MAN_VS_NATURE = "人与自然"
    MAN_VS_SELF = "人与自我"
    MAN_VS_SOCIETY = "人与社会"
    MAN_VS_FATE = "人与命运"
    MAN_VS_TECHNOLOGY = "人与科技"


class NarrativeStructure(str, Enum):
    """叙事结构枚举"""
    LINEAR = "线性叙事"
    NON_LINEAR = "非线性叙事"
    MULTIPLE_POV = "多视角叙事"
    EPISTOLARY = "书信体"
    STREAM_OF_CONSCIOUSNESS = "意识流"


class EmotionalBeat(str, Enum):
    """情感节拍枚举"""
    TENSION = "紧张"
    RELIEF = "缓解"
    SHOCK = "震惊"
    SATISFACTION = "满足"
    MELANCHOLY = "忧郁"
    JOY = "喜悦"
    FEAR = "恐惧"
    HOPE = "希望"
    DETERMINATION = "决心"
    CONFUSION = "困惑"
    GROWTH = "成长"
    VICTORY = "胜利"
    EXCITEMENT = "兴奋"
    ANXIETY = "焦虑"
    PEACE = "平静"
    FRUSTRATION = "挫折"


# 新的数据模型类

class ActStructure(BaseModel):
    """幕次结构模型 - 6要素结构"""
    act_number: int = Field(..., description="幕次编号")
    act_name: str = Field(..., description="幕次名称")
    core_mission: str = Field(..., description="核心任务：主角在这一幕的主要目标")
    daily_events: str = Field(..., description="日常事件：主角日常行动，会获得什么")
    conflict_events: str = Field(..., description="冲突事件：主角服务于目标的关键行动，会有什么阻碍")
    special_events: str = Field(..., description="特殊事件：主角的转折事件或奇遇，获得什么关键提升")
    major_events: str = Field(..., description="重大事件：非主角发起的环境变化事件，如何推动剧情发展")
    stage_result: str = Field(..., description="阶段结果：主角获得了哪些成果，状态如何，拥有哪些资源，新目标是什么")


class CharacterPosition(BaseModel):
    """角色定位模型"""
    position: str
    function: str
    development_arc: str
    worldview_connection: str
    key_moments: List[str]




class PlotBlock(BaseModel):
    """剧情块模型"""
    plot_name: str
    description: str
    participating_characters: List[str]
    worldview_elements: List[str]
    emotional_tone: str
    plot_function: str
    estimated_chapters: int
    estimated_words: int
    key_events: List[str]
    foreshadowing: List[str]


class StoryFlow(BaseModel):
    """故事脉络模型"""
    overall_direction: str
    thematic_progression: str
    character_arcs: Dict[str, str]
    worldview_evolution: str
    conflict_progression: str
    emotional_journey: str




class Act(BaseModel):
    """幕次模型"""
    act_number: int = Field(..., description="幕次编号")
    act_name: str = Field(..., description="幕次名称")
    start_position: float = Field(..., description="开始位置比例 (0.0-1.0)")
    end_position: float = Field(..., description="结束位置比例 (0.0-1.0)")
    purpose: str = Field(..., description="幕次目的")
    key_events: List[str] = Field(default_factory=list, description="关键事件")
    emotional_tone: str = Field(..., description="情感基调")
    character_focus: str = Field(default="主角", description="角色焦点")
    worldview_elements: List[str] = Field(default_factory=list, description="世界观元素")
    estimated_chapters: int = Field(default=4, description="预估章节数")
    estimated_words: int = Field(default=20000, description="预估字数")


class TurningPoint(BaseModel):
    """转折点模型"""
    point_type: str = Field(..., description="转折点类型")
    position: float = Field(..., description="在故事中的位置比例")
    title: str = Field(..., description="转折点标题")
    description: str = Field(..., description="转折点描述")
    impact: str = Field(..., description="对故事的影响")
    character_involvement: List[str] = Field(default_factory=list, description="涉及角色")
    worldview_connection: str = Field(default="与世界观核心概念相关", description="世界观联系")


class StoryFramework(BaseModel):
    """故事框架模型"""
    structure_type: PlotStructure = Field(PlotStructure.THREE_ACT, description="结构类型")
    acts: List[Act] = Field(default_factory=list, description="幕次结构")
    turning_points: List[TurningPoint] = Field(default_factory=list, description="转折点")
    climax_position: float = Field(0.8, description="高潮位置比例")
    resolution_position: float = Field(0.9, description="结局位置比例")
    narrative_style: NarrativeStructure = Field(NarrativeStructure.LINEAR, description="叙事风格")


class CentralConflict(BaseModel):
    """核心冲突模型"""
    conflict_type: ConflictType = Field(..., description="冲突类型")
    protagonist_goal: str = Field(..., description="主角目标")
    antagonist_obstacle: str = Field(..., description="反派障碍")
    internal_conflict: str = Field(..., description="内心冲突")
    external_conflict: str = Field(..., description="外部冲突")
    conflict_escalation: List[str] = Field(default_factory=list, description="冲突升级过程")
    resolution_method: str = Field(..., description="解决方式")


class ArcPoint(BaseModel):
    """故事弧线节点"""
    position: float = Field(..., description="位置比例")
    title: str = Field(..., description="节点标题")
    description: str = Field(..., description="节点描述")
    emotional_state: EmotionalBeat = Field(..., description="情感状态")
    character_growth: str = Field(..., description="角色成长")
    plot_advancement: str = Field(..., description="剧情推进")


class StoryArc(BaseModel):
    """故事弧线模型"""
    beginning: ArcPoint = Field(..., description="开端")
    development: List[ArcPoint] = Field(default_factory=list, description="发展")
    climax: ArcPoint = Field(..., description="高潮")
    falling_action: ArcPoint = Field(..., description="回落")
    resolution: ArcPoint = Field(..., description="结局")
    emotional_journey: List[EmotionalBeat] = Field(default_factory=list, description="情感节拍")
    character_arcs: Dict[str, str] = Field(default_factory=dict, description="角色发展弧线")


class PlotPoint(BaseModel):
    """关键情节点模型"""
    id: str = Field(..., description="情节点ID")
    point_type: str = Field(..., description="情节点类型")
    position: float = Field(..., description="在故事中的位置比例")
    title: str = Field(..., description="情节点标题")
    description: str = Field(..., description="情节点描述")
    emotional_impact: EmotionalBeat = Field(..., description="情感影响")
    character_involvement: List[str] = Field(default_factory=list, description="涉及角色")
    plot_function: str = Field(..., description="剧情功能")
    foreshadowing: List[str] = Field(default_factory=list, description="伏笔设置")


class PlotOutline(BaseModel):
    """剧情大纲模型 - 简化版故事驱动模式"""
    id: str = Field(..., description="剧情大纲ID")
    title: str = Field(..., description="小说标题")
    
    # 关联信息
    worldview_id: str = Field(..., description="世界观ID")
    
    # 故事核心信息
    story_summary: str = Field(..., description="故事简介")
    core_conflict: str = Field(..., description="核心冲突")
    story_tone: str = Field(..., description="故事基调")
    narrative_structure: str = Field(..., description="叙事结构")
    theme: str = Field(..., description="主题思想")
    
    # 主角信息
    protagonist_name: str = Field(..., description="主角姓名")
    protagonist_background: str = Field(..., description="主角背景")
    protagonist_personality: str = Field(..., description="主角性格特质")
    protagonist_goals: str = Field(..., description="主角目标")
    
    # 世界观信息
    core_concept: str = Field(..., description="世界观核心概念")
    world_description: str = Field(..., description="世界观描述")
    geography_setting: str = Field(..., description="地理设定")
    
    # 幕次结构
    acts: List[ActStructure] = Field(..., description="幕次列表")
    
    # 技术参数
    target_word_count: int = Field(default=100000, description="目标字数")
    estimated_chapters: int = Field(default=20, description="预计章节数")
    
    # 状态信息
    status: PlotStatus = Field(default=PlotStatus.PLANNING, description="状态")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")
    created_by: str = Field(default="system", description="创建者")
    
    class Config:
        use_enum_values = True


class PlotOutlineRequest(BaseModel):
    """剧情大纲生成请求 - 简化版故事驱动模式"""
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


class PlotOutlineResponse(BaseModel):
    """剧情大纲生成响应"""
    success: bool = Field(..., description="是否成功")
    plot_outline: Optional[PlotOutline] = Field(None, description="生成的剧情大纲")
    message: str = Field(..., description="响应消息")
    generation_time: float = Field(0, description="生成耗时（秒）")


# 更新模型引用
PlotOutline.model_rebuild()
StoryFramework.model_rebuild()
CentralConflict.model_rebuild()
StoryArc.model_rebuild()
