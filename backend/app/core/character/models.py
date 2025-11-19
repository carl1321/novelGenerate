"""
角色数据模型
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum

from app.core.world.models import CultivationLevel, ElementType


class Gender(str, Enum):
    """性别枚举"""
    MALE = "男"
    FEMALE = "女"
    OTHER = "其他"
    NON_BINARY = "非二元"
    UNKNOWN = "未知"


class PersonalityTrait(str, Enum):
    """性格特质枚举"""
    BRAVE = "勇敢"
    CAUTIOUS = "谨慎"
    ARROGANT = "傲慢"
    HUMBLE = "谦逊"
    GREEDY = "贪婪"
    GENEROUS = "慷慨"
    LOYAL = "忠诚"
    TREACHEROUS = "背叛"
    WISE = "智慧"
    NAIVE = "天真"
    AMBITIOUS = "野心勃勃"
    CONTENT = "知足常乐"
    VENGEFUL = "复仇心重"
    FORGIVING = "宽恕"
    MYSTERIOUS = "神秘"
    OPEN = "坦率"
    PATIENT = "耐心"
    IMPATIENT = "急躁"
    DISCIPLINED = "自律"
    STRICT = "严格"
    LAZY = "懒惰"
    CARELESS = "粗心"
    KIND = "善良"
    COLD = "冷酷"
    OPTIMISTIC = "乐观"
    PESSIMISTIC = "悲观"
    CURIOUS = "好奇"
    IMPULSIVE = "冲动"
    CALM = "冷静"
    HONEST = "诚实"
    DECEPTIVE = "欺骗"


class RelationshipType(str, Enum):
    """关系类型枚举"""
    FRIEND = "朋友"
    ENEMY = "敌人"
    MENTOR = "师父"
    DISCIPLE = "徒弟"
    FAMILY = "家人"
    LOVER = "恋人"
    RIVAL = "对手"
    ALLY = "盟友"
    NEUTRAL = "中立"
    UNKNOWN = "未知"


class GoalType(str, Enum):
    """目标类型枚举"""
    CULTIVATION = "修炼目标"
    REVENGE = "复仇"
    POWER = "权力"
    WEALTH = "财富"
    LOVE = "爱情"
    KNOWLEDGE = "求知"
    PROTECTION = "保护"
    EXPLORATION = "探索"
    CREATION = "创造"
    DESTRUCTION = "毁灭"


class CharacterRoleType(str, Enum):
    """角色类型枚举（简化版）"""
    PROTAGONIST = "主角"           # 故事中心角色
    SUPPORTING = "配角"            # 配角
    JUSTICE_COMPANION = "正义伙伴"  # 支持主角的正面角色
    ANTAGONIST = "反派"            # 与主角对立的反面角色  
    LOVER = "情人"                # 与主角有情感关系的角色
    OTHER = "其他"                 # 其他类型角色
    SPECIAL = "特殊"               # 特殊身份角色


class Character(BaseModel):
    """角色模型（简化版）"""
    id: str = Field(..., description="角色ID")
    worldview_id: str = Field(..., description="所属世界观ID")
    name: str = Field(..., description="姓名")
    age: int = Field(..., ge=0, description="年龄")
    gender: Gender = Field(..., description="性别")
    role_type: CharacterRoleType = Field(default=CharacterRoleType.JUSTICE_COMPANION, description="角色类型")
    cultivation_level: Optional[str] = Field(None, description="修炼境界")
    element_type: Optional[str] = Field(None, description="灵根属性")
    background: str = Field(..., description="背景故事")
    current_location: Optional[str] = Field(None, description="当前位置")
    organization_id: Optional[str] = Field(None, description="所属组织")
    
    # 使用文本存储的字段
    personality_traits: str = Field(default="", description="性格特质描述")
    main_goals: str = Field(default="", description="主要目标")
    short_term_goals: str = Field(default="", description="短期目标")
    weaknesses: str = Field(default="", description="弱点和限制")
    appearance: str = Field(default="", description="外貌描述")
    turning_point: str = Field(default="", description="重要转折点")
    relationship_text: str = Field(default="", description="个人关系视角")
    values: str = Field(default="", description="价值观和信念")
    
    # 使用JSONB存储的字段
    techniques: List[Dict[str, Any]] = Field(default_factory=list, description="掌握的功法")
    stats: Dict[str, Any] = Field(default_factory=dict, description="属性数值")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="扩展元数据")
    
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    created_by: Optional[str] = Field(None, description="创建者")
    status: str = Field(default="active", description="状态")


class CharacterCard(BaseModel):
    """角色卡片模型"""
    character: Character = Field(..., description="角色信息")
    appearance: str = Field(..., description="外貌描述")
    voice: str = Field(..., description="声音特点")
    habits: List[str] = Field(default_factory=list, description="习惯行为")
    fears: List[str] = Field(default_factory=list, description="恐惧")
    motivations: List[str] = Field(default_factory=list, description="动机")
    secrets: List[str] = Field(default_factory=list, description="秘密")
    catchphrases: List[str] = Field(default_factory=list, description="口头禅")


class GrowthNode(BaseModel):
    """成长节点模型"""
    id: str = Field(..., description="节点ID")
    character_id: str = Field(..., description="角色ID")
    level: CultivationLevel = Field(..., description="目标境界")
    estimated_time: int = Field(..., description="预计时间（年）")
    requirements: List[str] = Field(default_factory=list, description="达成条件")
    key_events: List[str] = Field(default_factory=list, description="关键事件")
    rewards: List[str] = Field(default_factory=list, description="奖励")
    risks: List[str] = Field(default_factory=list, description="风险")
    created_at: datetime = Field(default_factory=datetime.now)


class Relationship(BaseModel):
    """关系模型"""
    id: str = Field(..., description="关系ID")
    character1_id: str = Field(..., description="角色1ID")
    character2_id: str = Field(..., description="角色2ID")
    relationship_type: RelationshipType = Field(..., description="关系类型")
    intimacy_level: int = Field(..., ge=1, le=10, description="亲密度(1-10)")
    trust_level: int = Field(..., ge=1, le=10, description="信任度(1-10)")
    description: str = Field(..., description="关系描述")
    history: List[str] = Field(default_factory=list, description="关系历史")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class CharacterTemplate(BaseModel):
    """角色模板模型"""
    id: str = Field(..., description="模板ID")
    name: str = Field(..., description="模板名称")
    description: str = Field(..., description="模板描述")
    base_personality: List[PersonalityTrait] = Field(..., description="基础性格")
    common_goals: List[Dict[str, Any]] = Field(default_factory=list, description="常见目标")
    typical_background: str = Field(..., description="典型背景")
    suggested_stats: Dict[str, int] = Field(default_factory=dict, description="建议属性")
    created_at: datetime = Field(default_factory=datetime.now)


class CharacterGroup(BaseModel):
    """角色组模型"""
    id: str = Field(..., description="组ID")
    name: str = Field(..., description="组名称")
    description: str = Field(..., description="组描述")
    character_ids: List[str] = Field(..., description="角色ID列表")
    group_type: str = Field(..., description="组类型")
    common_goals: List[Dict[str, Any]] = Field(default_factory=list, description="共同目标")
    internal_conflicts: List[str] = Field(default_factory=list, description="内部冲突")
    external_enemies: List[str] = Field(default_factory=list, description="外部敌人")
    created_at: datetime = Field(default_factory=datetime.now)


class CharacterBatchCreateRequest(BaseModel):
    """批量角色创建请求"""
    worldview_id: str = Field(..., description="世界观ID")
    description: str = Field(..., description="角色描述（一句话）")
    character_count: int = Field(..., ge=1, le=20, description="角色数量")
    role_types: List[CharacterRoleType] = Field(..., description="角色类型列表")
    additional_requirements: Optional[str] = Field(None, description="额外要求")


class CharacterBatchCreateResponse(BaseModel):
    """批量角色创建响应"""
    success: bool = Field(..., description="是否成功")
    characters: List[Character] = Field(..., description="创建的角色列表")
    message: str = Field(..., description="响应消息")
    total_count: int = Field(..., description="总创建数量")
