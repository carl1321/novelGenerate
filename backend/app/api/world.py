"""
世界观API路由
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from app.core.world.service import WorldService
from app.core.world.models import WorldView, Location, Organization, CultivationTechnique
from app.core.world.database import worldview_db

router = APIRouter()

# 创建服务实例
world_service = WorldService()


class WorldViewCreateRequest(BaseModel):
    """创建世界观请求"""
    core_concept: str
    description: Optional[str] = None
    additional_requirements: Optional[Dict[str, Any]] = None
    temperature: float = 0.7


class WorldViewExpandRequest(BaseModel):
    """扩展世界观请求"""
    expansion_type: str  # locations, organizations, techniques
    count: int = 5


class WorldElementSearchRequest(BaseModel):
    """世界元素搜索请求"""
    keyword: str
    element_types: Optional[List[str]] = None


@router.get("/list")
async def get_world_view_list(
    limit: int = Query(50, ge=1, le=100, description="限制数量"),
    offset: int = Query(0, ge=0, description="偏移量"),
    status: str = Query("active", description="状态过滤")
):
    """获取世界观列表"""
    try:
        worldviews = worldview_db.get_worldview_list(limit=limit, offset=offset, status=status)
        return worldviews
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/simple-list")
async def get_world_view_simple_list():
    """获取世界观简单列表（仅用于前端选择，超快响应）"""
    try:
        # 使用数据库管理器的连接方法
        worldviews = worldview_db.get_worldview_list(limit=100, offset=0)
        
        # 只返回简单字段
        simple_worldviews = [
            {
                'worldview_id': w.get('worldview_id'),
                'name': w.get('name'),
                'description': w.get('description')
            }
            for w in worldviews
        ]
                
        return {"worldviews": simple_worldviews}
    except Exception as e:
        print(f"获取世界观简单列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/create", response_model=WorldView)
async def create_world_view(request: WorldViewCreateRequest):
    """创建世界观"""
    try:
        world_view = await world_service.create_world_view(
            request.core_concept,
            request.description,
            request.additional_requirements,
            request.temperature
        )
        return world_view
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{world_view_id}/expand")
async def expand_world_view(world_view_id: str, request: WorldViewExpandRequest):
    """扩展世界观"""
    try:
        results = await world_service.expand_world_view(
            world_view_id,
            request.expansion_type,
            request.count
        )
        return {"message": "扩展成功", "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




@router.get("/{world_view_id}", response_model=WorldView)
async def get_world_view(world_view_id: str):
    """获取世界观"""
    world_view = await world_service.get_world_view(world_view_id)
    if not world_view:
        raise HTTPException(status_code=404, detail="世界观不存在")
    return world_view


@router.delete("/{world_view_id}")
async def delete_world_view(world_view_id: str):
    """删除世界观"""
    try:
        # 检查世界观是否存在
        world_view = await world_service.get_world_view(world_view_id)
        if not world_view:
            raise HTTPException(status_code=404, detail="世界观不存在")
        
        # 删除世界观（硬删除）
        success = worldview_db.delete_worldview(world_view_id, soft_delete=False)
        if not success:
            raise HTTPException(status_code=500, detail="删除世界观失败")
        
        return {"message": "世界观删除成功", "worldview_id": world_view_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search")
async def search_world_views(
    q: str = Query(..., description="搜索关键词"),
    limit: int = Query(20, ge=1, le=100, description="限制数量")
):
    """搜索世界观"""
    try:
        results = worldview_db.search_worldviews(query=q, limit=limit)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search")
async def search_world_elements(request: WorldElementSearchRequest):
    """搜索世界元素"""
    try:
        results = await world_service.search_world_elements(
            request.keyword,
            request.element_types
        )
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{world_view_id}/characters/{character_id}/network")
async def get_character_network(world_view_id: str, character_id: str, 
                               depth: int = Query(2, ge=1, le=5)):
    """获取角色关系网络"""
    try:
        network = await world_service.get_character_network(character_id, depth)
        return {"network": network}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{world_view_id}/validate")
async def validate_world_consistency(world_view_id: str):
    """验证世界观一致性"""
    try:
        validation_result = await world_service.validate_world_consistency(world_view_id)
        return validation_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{world_view_id}/statistics")
async def get_world_statistics(world_view_id: str):
    """获取世界观统计信息"""
    try:
        stats = await world_service.get_world_statistics(world_view_id)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{world_view_id}/export")
async def export_world_view(world_view_id: str):
    """导出世界观"""
    try:
        world_data = await world_service.export_world_view(world_view_id)
        return world_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/import")
async def import_world_view(world_data: Dict[str, Any]):
    """导入世界观"""
    try:
        world_view_id = await world_service.import_world_view(world_data)
        return {"message": "导入成功", "world_view_id": world_view_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{world_view_id}/elements/{element_type}/{element_id}")
async def update_world_element(world_view_id: str, element_type: str, 
                              element_id: str, updates: Dict[str, Any]):
    """更新世界元素"""
    try:
        success = await world_service.update_world_element(
            element_type, element_id, updates
        )
        if success:
            return {"message": "更新成功"}
        else:
            raise HTTPException(status_code=400, detail="更新失败")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{world_view_id}/elements/{element_type}/{element_id}")
async def delete_world_element(world_view_id: str, element_type: str, element_id: str):
    """删除世界元素"""
    try:
        success = await world_service.delete_world_element(element_type, element_id)
        if success:
            return {"message": "删除成功"}
        else:
            raise HTTPException(status_code=400, detail="删除失败")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{world_view_id}/locations")
async def get_locations(world_view_id: str):
    """获取所有地点"""
    try:
        locations = world_service.knowledge_graph.query_by_type("Location")
        return {"locations": locations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{world_view_id}/organizations")
async def get_organizations(world_view_id: str):
    """获取所有组织"""
    try:
        organizations = world_service.knowledge_graph.query_by_type("Organization")
        return {"organizations": organizations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{world_view_id}/techniques")
async def get_techniques(world_view_id: str):
    """获取所有功法"""
    try:
        techniques = world_service.knowledge_graph.query_by_type("Technique")
        return {"techniques": techniques}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class WorldViewPartialUpdateRequest(BaseModel):
    """世界观部分更新请求"""
    core_concept: Optional[str] = None
    description: Optional[str] = None
    update_dimensions: List[str]
    update_description: str


@router.put("/{world_view_id}")
async def update_worldview(world_view_id: str, request: Dict[str, Any]):
    """直接更新世界观基本信息"""
    try:
        # 获取现有世界观
        existing_worldview = worldview_db.get_worldview(world_view_id)
        if not existing_worldview:
            raise HTTPException(status_code=404, detail="世界观不存在")
        
        # 构建更新数据
        update_data = existing_worldview.copy()
        
        # 更新允许的字段
        if "name" in request:
            update_data["name"] = request["name"]
        if "core_concept" in request:
            update_data["core_concept"] = request["core_concept"]
        if "description" in request:
            update_data["description"] = request["description"]
        if "power_system" in request:
            update_data["power_system"] = request["power_system"]
        if "geography" in request:
            update_data["geography"] = request["geography"]
        if "social_structure" in request:
            update_data["culture"] = request["social_structure"]
        if "historical_culture" in request:
            update_data["history"] = request["historical_culture"]
        
        # 更新数据库
        success = worldview_db.update_worldview(world_view_id, update_data)
        if not success:
            raise HTTPException(status_code=500, detail="更新数据库失败")
        
        return {
            "message": "世界观更新成功",
            "worldview": update_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新失败: {str(e)}")


@router.put("/{world_view_id}/partial")
async def partial_update_worldview(world_view_id: str, request: WorldViewPartialUpdateRequest):
    """部分更新世界观"""
    try:
        # 获取现有世界观
        existing_worldview = worldview_db.get_worldview(world_view_id)
        if not existing_worldview:
            raise HTTPException(status_code=404, detail="世界观不存在")
        
        # 导入部分更新服务
        from app.core.world.part_world_update import PartialWorldUpdateService
        update_service = PartialWorldUpdateService()
        
        # 执行部分更新
        updated_data = await update_service.update_partial_worldview(
            existing_worldview=existing_worldview,
            update_dimensions=request.update_dimensions,
            update_description=request.update_description,
            additional_context={
                "core_concept": request.core_concept,
                "description": request.description
            }
        )
        
        # 更新数据库
        success = worldview_db.update_worldview(world_view_id, updated_data)
        if not success:
            raise HTTPException(status_code=500, detail="更新数据库失败")
        
        return {
            "message": "世界观部分更新成功",
            "updated_dimensions": request.update_dimensions,
            "worldview": updated_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"部分更新失败: {str(e)}")
