"""
角色管理API路由
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from app.core.character.service import CharacterService
from app.core.character.models import (
    Character, CharacterCard, CharacterTemplate, CharacterGroup,
    CharacterBatchCreateRequest, CharacterBatchCreateResponse, CharacterRoleType
)

router = APIRouter()

# 创建服务实例
character_service = CharacterService()


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
        
        # 调试信息：检查API返回的角色数据
        import logging
        logger = logging.getLogger(__name__)
        logger.debug(f"API返回角色数量: {len(characters)}")
        if characters:
            first_char = characters[0]
            logger.debug(f"第一个角色 - id: {first_char.id}")
            logger.debug(f"第一个角色 - worldview_id: {first_char.worldview_id}")
            logger.debug(f"第一个角色 - name: {first_char.name}")
        
        return characters
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class CharacterCreateRequest(BaseModel):
    """创建角色请求"""
    worldview_id: str
    description: str
    role_type: str
    additional_requirements: Optional[str] = None


class CharacterFromTemplateRequest(BaseModel):
    """从模板创建角色请求"""
    world_view_id: str
    template_id: str
    customizations: Optional[Dict[str, Any]] = None


class CharacterRelationshipRequest(BaseModel):
    """创建角色关系请求"""
    character1_id: str
    character2_id: str
    relationship_type: str
    intimacy_level: int = 5
    trust_level: int = 5


class CharacterGroupCreateRequest(BaseModel):
    """创建角色组请求"""
    group_name: str
    character_ids: List[str]
    group_type: str = "custom"


class CharacterConsistencyRequest(BaseModel):
    """角色一致性分析请求"""
    character_id: str
    situation: str
    action: str


class CharacterDialogueRequest(BaseModel):
    """角色对话生成请求"""
    character_id: str
    situation: str


class CharacterBackgroundExpansionRequest(BaseModel):
    """角色背景扩展请求"""
    character_id: str
    expansion_type: str


class CharacterGrowthSimulationRequest(BaseModel):
    """角色成长模拟请求"""
    character_id: str
    growth_nodes: List[Dict[str, Any]]
    years: int


@router.post("/create-from-template", response_model=Character)
async def create_character_from_template(request: CharacterFromTemplateRequest):
    """从模板创建角色"""
    try:
        character = await character_service.create_character_from_template(
            request.world_view_id,
            request.template_id,
            request.customizations
        )
        return character
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{character_id}", response_model=Character)
async def get_character(character_id: str):
    """获取角色信息"""
    character = await character_service.get_character(character_id)
    if not character:
        raise HTTPException(status_code=404, detail="角色不存在")
    return character


@router.put("/{character_id}")
async def update_character(character_id: str, updates: Dict[str, Any]):
    """更新角色信息"""
    try:
        success = await character_service.update_character(character_id, updates)
        if success:
            return {"message": "更新成功"}
        else:
            raise HTTPException(status_code=400, detail="更新失败")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{character_id}")
async def delete_character(character_id: str):
    """删除角色"""
    try:
        success = await character_service.delete_character(character_id)
        if success:
            return {"message": "删除成功"}
        else:
            raise HTTPException(status_code=400, detail="删除失败")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search")
async def search_characters(keyword: str, filters: Optional[Dict[str, Any]] = None):
    """搜索角色"""
    try:
        characters = await character_service.search_characters(keyword, filters)
        return {"characters": characters}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{character_id}/card", response_model=CharacterCard)
async def get_character_card(character_id: str):
    """获取角色卡片"""
    try:
        character_card = await character_service.generate_character_card(character_id)
        return character_card
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{character_id}/growth-plan")
async def get_character_growth_plan(character_id: str, 
                                  target_level: Optional[str] = None):
    """获取角色成长规划"""
    try:
        growth_nodes = await character_service.plan_character_growth(
            character_id, target_level
        )
        return {"growth_nodes": growth_nodes}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{character_id}/growth-simulation")
async def simulate_character_growth(request: CharacterGrowthSimulationRequest):
    """模拟角色成长过程"""
    try:
        simulation = await character_service.simulate_character_growth(
            request.character_id,
            request.growth_nodes,
            request.years
        )
        return simulation
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{character_id}/growth-suggestions")
async def get_growth_suggestions(character_id: str):
    """获取成长建议"""
    try:
        suggestions = await character_service.get_growth_suggestions(character_id)
        return {"suggestions": suggestions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/relationships")
async def create_relationship(request: CharacterRelationshipRequest):
    """创建角色关系"""
    try:
        relationship = await character_service.create_relationship(
            request.character1_id,
            request.character2_id,
            request.relationship_type,
            request.intimacy_level,
            request.trust_level
        )
        return relationship
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{character_id}/network")
async def get_character_network(character_id: str, 
                               depth: int = Query(2, ge=1, le=5)):
    """获取角色关系网络"""
    try:
        network = await character_service.get_character_network(character_id, depth)
        return {"network": network}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/consistency-analysis")
async def analyze_character_consistency(request: CharacterConsistencyRequest):
    """分析角色行为一致性"""
    try:
        analysis = await character_service.analyze_character_consistency(
            request.character_id,
            request.situation,
            request.action
        )
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/dialogue")
async def generate_character_dialogue(request: CharacterDialogueRequest):
    """生成角色对话"""
    try:
        dialogue = await character_service.generate_character_dialogue(
            request.character_id,
            request.situation
        )
        return {"dialogue": dialogue}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/background-expansion")
async def expand_character_background(request: CharacterBackgroundExpansionRequest):
    """扩展角色背景"""
    try:
        expansion = await character_service.expand_character_background(
            request.character_id,
            request.expansion_type
        )
        return expansion
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/templates", response_model=List[CharacterTemplate])
async def get_character_templates():
    """获取角色模板列表"""
    try:
        templates = await character_service.get_character_templates()
        return templates
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/groups")
async def create_character_group(request: CharacterGroupCreateRequest):
    """创建角色组"""
    try:
        group = await character_service.create_character_group(
            request.group_name,
            request.character_ids,
            request.group_type
        )
        return group
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{character_id}/stats")
async def get_character_stats(character_id: str):
    """获取角色统计信息"""
    try:
        character = await character_service.get_character(character_id)
        if not character:
            raise HTTPException(status_code=404, detail="角色不存在")
        
        stats = {
            "character_id": character.id,
            "name": character.name,
            "cultivation_level": character.cultivation_level.value,
            "element_type": character.element_type.value,
            "personality_traits": [trait.value for trait in character.personality],
            "technique_count": len(character.techniques),
            "artifact_count": len(character.artifacts),
            "goal_count": len(character.goals),
            "relationship_count": len(character.relationships),
            "created_at": character.created_at.isoformat(),
            "updated_at": character.updated_at.isoformat()
        }
        
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/create", response_model=Character)
async def create_character(request: CharacterCreateRequest):
    """创建单个角色"""
    try:
        # 构建角色需求
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


@router.post("/batch-create", response_model=CharacterBatchCreateResponse)
async def create_characters_batch(request: CharacterBatchCreateRequest):
    """批量创建角色"""
    try:
        response = await character_service.create_characters_batch(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{character_id}")
async def delete_character(character_id: str):
    """删除角色"""
    try:
        print(f"开始删除角色: {character_id}")
        success = await character_service.delete_character(character_id)
        print(f"删除角色结果: {success}")
        
        if success:
            return {"message": "角色删除成功"}
        else:
            raise HTTPException(status_code=404, detail="角色不存在")
    except HTTPException:
        raise
    except Exception as e:
        print(f"删除角色API错误: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")


