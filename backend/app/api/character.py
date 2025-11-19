"""
角色管理API路由 - 简化版
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from app.core.character.service import CharacterService
from app.core.character.models import (
    Character, CharacterCard, CharacterTemplate, CharacterGroup,
    CharacterBatchCreateRequest, CharacterBatchCreateResponse, CharacterRoleType
)
from app.core.world.database import WorldViewDatabase
from datetime import datetime

router = APIRouter()

# 创建服务实例
character_service = CharacterService()
worldview_db = WorldViewDatabase()


@router.get("/list", response_model=List[Character])
async def get_character_list(
    worldview_id: Optional[str] = Query(None, description="世界观ID"),
    role_type: Optional[str] = Query(None, description="角色类型"),
    keyword: str = Query("", description="搜索关键词"),
    limit: int = Query(100, description="限制数量"),
    offset: int = Query(0, description="偏移量")
):
    """获取角色列表"""
    try:
        filters = {}
        if worldview_id:
            filters["worldview_id"] = worldview_id
        if role_type:
            filters["role_type"] = role_type
            
        characters = await character_service.search_characters(
            keyword=keyword,
            filters=filters
        )
        
        return characters
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/geography/{worldview_id}")
async def get_worldview_geography(worldview_id: str):
    """获取世界观的地理设定信息"""
    try:
        geography = worldview_db.get_geography(worldview_id)
        if not geography:
            raise HTTPException(status_code=404, detail="世界观不存在或没有地理设定")
        
        # 解析地理设定，提取区域和地点信息
        regions = geography.get('main_regions', []) or geography.get('regions', [])
        locations = geography.get('special_locations', [])
        
        # 构建地理位置选项
        geography_options = {
            "regions": [],
            "locations": []
        }
        
        # 处理区域信息
        for region in regions:
            if isinstance(region, dict):
                geography_options["regions"].append({
                    "name": region.get("name", "未知区域"),
                    "description": region.get("description", ""),
                    "type": region.get("type", "区域")
                })
            elif isinstance(region, str):
                geography_options["regions"].append({
                    "name": region,
                    "description": "",
                    "type": "区域"
                })
        
        # 处理特殊地点信息
        for location in locations:
            if isinstance(location, dict):
                geography_options["locations"].append({
                    "name": location.get("name", "未知地点"),
                    "description": location.get("description", ""),
                    "type": location.get("type", "地点")
                })
            elif isinstance(location, str):
                geography_options["locations"].append({
                    "name": location,
                    "description": "",
                    "type": "地点"
                })
        
        return geography_options
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class CharacterCreateRequest(BaseModel):
    """角色创建请求"""
    name: str = Field(..., description="角色姓名")
    age: int = Field(..., description="年龄")
    gender: str = Field(..., description="性别")
    role_type: str = Field(..., description="角色类型")
    worldview_id: str = Field(..., description="世界观ID")
    background: str = Field(default="", description="背景故事")
    personality_traits: List[str] = Field(default=[], description="性格特质")
    cultivation_level: str = Field(default="未知", description="修炼境界")
    element_type: str = Field(default="未知", description="灵根属性")
    current_location: str = Field(default="未知", description="当前位置")


class CharacterGenerateRequest(BaseModel):
    """基于描述生成角色请求"""
    worldview_id: str = Field(..., description="世界观ID")
    description: str = Field(..., description="角色描述")
    role_type: str = Field(..., description="角色类型")
    additional_requirements: Optional[str] = Field(None, description="额外要求")


@router.post("/generate", response_model=Character)
async def generate_character(request: CharacterGenerateRequest):
    """基于描述生成角色"""
    try:
        # 构建角色需求字典
        character_requirements = {
            "description": request.description,
            "role_type": request.role_type,
            "additional_requirements": request.additional_requirements or ""
        }
        
        character = await character_service.create_character(
            world_view_id=request.worldview_id,
            character_requirements=character_requirements
        )
        
        return character
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/create", response_model=Character)
async def create_character(request: CharacterCreateRequest):
    """创建角色"""
    try:
        # 构建角色需求字典
        character_requirements = {
            "name": request.name,
            "age": request.age,
            "gender": request.gender,
            "role_type": request.role_type,
            "background": request.background,
            "personality_traits": request.personality_traits,
            "cultivation_level": request.cultivation_level,
            "element_type": request.element_type,
            "current_location": request.current_location
        }
        
        character = await character_service.create_character(
            world_view_id=request.worldview_id,
            character_requirements=character_requirements
        )
        
        return character
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{character_id}", response_model=Character)
async def get_character(character_id: str):
    """获取角色详情"""
    try:
        character = await character_service.get_character(character_id)
        if not character:
            raise HTTPException(status_code=404, detail="角色不存在")
        
        return character
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class CharacterUpdateRequest(BaseModel):
    """角色更新请求"""
    name: Optional[str] = Field(None, description="角色姓名")
    age: Optional[int] = Field(None, description="年龄")
    gender: Optional[str] = Field(None, description="性别")
    role_type: Optional[str] = Field(None, description="角色类型")
    worldview_id: Optional[str] = Field(None, description="世界观ID")
    background: Optional[str] = Field(None, description="背景故事")
    personality_traits: Optional[str] = Field(None, description="性格特质")
    main_goals: Optional[str] = Field(None, description="主要目标")
    short_term_goals: Optional[str] = Field(None, description="短期目标")
    cultivation_level: Optional[str] = Field(None, description="修炼境界")
    element_type: Optional[str] = Field(None, description="灵根属性")
    current_location: Optional[str] = Field(None, description="当前位置")
    organization_id: Optional[str] = Field(None, description="所属组织")
    weaknesses: Optional[str] = Field(None, description="弱点")
    appearance: Optional[str] = Field(None, description="外貌")
    turning_point: Optional[str] = Field(None, description="转折点")
    relationship_text: Optional[str] = Field(None, description="个人关系视角")
    values: Optional[str] = Field(None, description="价值观")
    techniques: Optional[List[Dict[str, Any]]] = Field(None, description="技能")
    metadata: Optional[Dict[str, Any]] = Field(None, description="元数据")
    status: Optional[str] = Field(None, description="状态")


@router.put("/{character_id}", response_model=Character)
async def update_character(character_id: str, request: CharacterUpdateRequest):
    """更新角色"""
    try:
        # 构建更新数据
        updates = {}
        for field, value in request.dict(exclude_unset=True).items():
            if value is not None:
                updates[field] = value
        
        if not updates:
            raise HTTPException(status_code=400, detail="没有提供更新数据")
        
        success = await character_service.update_character(character_id, updates)
        if not success:
            raise HTTPException(status_code=404, detail="角色不存在或更新失败")
        
        # 返回更新后的角色
        character = await character_service.get_character(character_id)
        return character
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{character_id}")
async def delete_character(character_id: str):
    """删除角色"""
    try:
        success = await character_service.delete_character(character_id)
        if not success:
            raise HTTPException(status_code=404, detail="角色不存在")
        
        return {"success": True, "message": "角色删除成功"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch", response_model=CharacterBatchCreateResponse)
async def batch_create_characters(request: CharacterBatchCreateRequest):
    """批量创建角色"""
    try:
        result = await character_service.batch_create_characters(
            world_view_id=request.world_view_id,
            character_description=request.character_description,
            character_count=request.character_count,
            role_types=request.role_types
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/card/{character_id}", response_model=CharacterCard)
async def get_character_card(character_id: str):
    """获取角色卡片"""
    try:
        card = await character_service.generate_character_card(character_id)
        if not card:
            raise HTTPException(status_code=404, detail="角色不存在")
        
        return card
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/template/list", response_model=List[CharacterTemplate])
async def get_character_templates():
    """获取角色模板列表"""
    try:
        templates = await character_service.get_character_templates()
        return templates
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/template/create", response_model=Character)
async def create_character_from_template(template_id: str, worldview_id: str):
    """从模板创建角色"""
    try:
        character = await character_service.create_character_from_template(template_id, worldview_id)
        if not character:
            raise HTTPException(status_code=404, detail="模板不存在")
        
        return character
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/group/list", response_model=List[CharacterGroup])
async def get_character_groups():
    """获取角色组列表"""
    try:
        groups = await character_service.get_character_groups()
        return groups
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/group/create")
async def create_character_group(name: str, description: str, character_ids: List[str]):
    """创建角色组"""
    try:
        group = await character_service.create_character_group(name, description, character_ids)
        return group
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/consistency/{character_id}")
async def check_character_consistency(character_id: str):
    """检查角色一致性"""
    try:
        analysis = await character_service.analyze_character_consistency(character_id)
        return analysis
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/dialogue/{character_id}")
async def generate_character_dialogue(character_id: str, context: str, other_characters: List[str]):
    """生成角色对话"""
    try:
        dialogue = await character_service.generate_character_dialogue(character_id, context, other_characters)
        return {"dialogue": dialogue}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/background/expand/{character_id}")
async def expand_character_background(character_id: str, expansion_requirements: str):
    """扩展角色背景"""
    try:
        expanded_background = await character_service.expand_character_background(character_id, expansion_requirements)
        return {"expanded_background": expanded_background}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/growth/simulate/{character_id}")
async def simulate_character_growth(character_id: str, growth_scenario: str):
    """模拟角色成长"""
    try:
        growth_result = await character_service.simulate_character_growth(character_id, growth_scenario)
        return growth_result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/growth/suggestions/{character_id}")
async def get_growth_suggestions(character_id: str):
    """获取角色成长建议"""
    try:
        suggestions = await character_service.get_character_growth_suggestions(character_id)
        return {"suggestions": suggestions}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


