"""
世界观数据模型
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum


class CultivationLevel(str, Enum):
    """修仙境界枚举"""
    MORTAL = "凡人"
    QI_REFINING = "练气"
    FOUNDATION = "筑基"
    GOLDEN_CORE = "金丹"
    NASCENT_SOUL = "元婴"
    SPIRIT_TRANSFORMATION = "化神"
    SPIRIT_FUSION = "合体"
    GREAT_ACCOMPLISHMENT = "大乘"
    IMMORTAL = "仙人"


class ElementType(str, Enum):
    """灵根属性枚举"""
    GOLD = "金"
    WOOD = "木"
    WATER = "水"
    FIRE = "火"
    EARTH = "土"
    WIND = "风"
    THUNDER = "雷"
    ICE = "冰"
    DARK = "暗"
    LIGHT = "光"


class OrganizationType(str, Enum):
    """组织类型枚举"""
    SECT = "宗门"
    CLAN = "家族"
    GUILD = "商会"
    KINGDOM = "王朝"
    ALLIANCE = "联盟"
    DEMON_CLAN = "妖族"
    GHOST_CLAN = "鬼族"


class LocationType(str, Enum):
    """地点类型枚举"""
    CONTINENT = "大陆"
    KINGDOM = "王国"
    CITY = "城市"
    SECT = "宗门"
    FOREST = "森林"
    MOUNTAIN = "山脉"
    LAKE = "湖泊"
    DESERT = "沙漠"
    SECRET_REALM = "秘境"
    RUINS = "遗迹"


class WorldElement(BaseModel):
    """世界元素基类"""
    id: str = Field(..., description="唯一标识符")
    name: str = Field(..., description="名称")
    description: str = Field(..., description="描述")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict, description="扩展元数据")


class Location(WorldElement):
    """地点模型"""
    location_type: LocationType = Field(..., description="地点类型")
    parent_id: Optional[str] = Field(None, description="父级地点ID")
    coordinates: Optional[Dict[str, float]] = Field(None, description="坐标信息")
    climate: Optional[str] = Field(None, description="气候")
    resources: List[str] = Field(default_factory=list, description="资源列表")
    dangers: List[str] = Field(default_factory=list, description="危险因素")
    population: Optional[int] = Field(None, description="人口数量")
    power_level: Optional[int] = Field(None, description="整体实力等级")


class Organization(WorldElement):
    """组织模型"""
    org_type: OrganizationType = Field(..., description="组织类型")
    location_id: Optional[str] = Field(None, description="所在位置ID")
    leader_id: Optional[str] = Field(None, description="领导者ID")
    member_count: Optional[int] = Field(None, description="成员数量")
    power_level: Optional[int] = Field(None, description="实力等级")
    reputation: Optional[int] = Field(None, description="声望值")
    resources: List[str] = Field(default_factory=list, description="资源列表")
    techniques: List[str] = Field(default_factory=list, description="功法列表")
    enemies: List[str] = Field(default_factory=list, description="敌对势力")
    allies: List[str] = Field(default_factory=list, description="盟友势力")


class CultivationTechnique(WorldElement):
    """功法模型"""
    level_requirement: CultivationLevel = Field(..., description="修炼要求境界")
    element_type: ElementType = Field(..., description="灵根属性要求")
    difficulty: int = Field(..., ge=1, le=10, description="修炼难度(1-10)")
    power_level: int = Field(..., ge=1, le=10, description="威力等级(1-10)")
    cultivation_speed: int = Field(..., ge=1, le=10, description="修炼速度(1-10)")
    side_effects: List[str] = Field(default_factory=list, description="副作用")
    prerequisites: List[str] = Field(default_factory=list, description="前置功法")
    creator: Optional[str] = Field(None, description="创造者")
    origin_org: Optional[str] = Field(None, description="来源组织")


class Artifact(WorldElement):
    """法宝模型"""
    artifact_type: str = Field(..., description="法宝类型")
    grade: int = Field(..., ge=1, le=10, description="品级(1-10)")
    power_level: int = Field(..., ge=1, le=10, description="威力等级(1-10)")
    special_abilities: List[str] = Field(default_factory=list, description="特殊能力")
    usage_conditions: List[str] = Field(default_factory=list, description="使用条件")
    creator: Optional[str] = Field(None, description="创造者")
    origin_org: Optional[str] = Field(None, description="来源组织")
    current_owner: Optional[str] = Field(None, description="当前持有者")


class Pill(WorldElement):
    """丹药模型"""
    pill_type: str = Field(..., description="丹药类型")
    grade: int = Field(..., ge=1, le=10, description="品级(1-10)")
    effects: List[str] = Field(..., description="效果列表")
    side_effects: List[str] = Field(default_factory=list, description="副作用")
    ingredients: List[str] = Field(..., description="材料列表")
    difficulty: int = Field(..., ge=1, le=10, description="炼制难度(1-10)")
    creator: Optional[str] = Field(None, description="创造者")


class WorldRule(BaseModel):
    """世界规则模型"""
    id: str = Field(..., description="规则ID")
    name: str = Field(..., description="规则名称")
    category: str = Field(..., description="规则分类")
    content: str = Field(..., description="规则内容")
    priority: int = Field(default=1, description="优先级")
    is_active: bool = Field(default=True, description="是否激活")
    created_at: datetime = Field(default_factory=datetime.now)


class WorldView(BaseModel):
    """世界观模型"""
    id: str = Field(..., description="世界观ID")
    name: str = Field(..., description="世界观名称")
    description: str = Field(..., description="世界观描述")
    core_concept: str = Field(..., description="核心概念")
    power_system: Any = Field(default_factory=dict, description="力量体系")
    geography: Any = Field(default_factory=dict, description="地理设定")
    history: Any = Field(default_factory=dict, description="历史背景")
    culture: Any = Field(default_factory=dict, description="文化设定")
    rules: List[Dict[str, Any]] = Field(default_factory=list, description="世界规则")
    locations: List[Dict[str, Any]] = Field(default_factory=list, description="地点列表")
    organizations: List[Dict[str, Any]] = Field(default_factory=list, description="组织列表")
    techniques: List[Dict[str, Any]] = Field(default_factory=list, description="功法列表")
    artifacts: List[Dict[str, Any]] = Field(default_factory=list, description="法宝列表")
    pills: List[Dict[str, Any]] = Field(default_factory=list, description="丹药列表")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
