#!/usr/bin/env python3
"""
简化的API服务器 - 只包含世界观生成接口
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import sys
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加backend路径到sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# 导入真正的服务
from app.core.world.service import WorldService
from app.core.world.database import worldview_db

app = FastAPI(title="小说生成API", version="1.0.0")

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 创建服务实例
world_service = WorldService()

class WorldViewCreateRequest(BaseModel):
    """创建世界观请求"""
    core_concept: str
    description: Optional[str] = None
    additional_requirements: Optional[Dict[str, Any]] = None

class WorldViewUpdateRequest(BaseModel):
    """更新世界观请求"""
    core_concept: Optional[str] = None
    description: Optional[str] = None
    additional_requirements: Optional[Dict[str, Any]] = None
    update_options: Optional[Dict[str, bool]] = None  # 指定要更新的维度

class WorldViewPartialUpdateRequest(BaseModel):
    """部分更新世界观请求"""
    update_dimensions: List[str] = Field(..., description="要更新的维度")
    update_description: str = Field(..., description="更新描述")
    additional_context: Optional[Dict[str, Any]] = Field(None, description="额外上下文")
    
    # 可选：允许同时更新基本信息
    core_concept: Optional[str] = None
    description: Optional[str] = None

# API端点
@app.post("/api/v1/world/create")
async def create_world_view(request: WorldViewCreateRequest):
    """创建世界观"""
    try:
        world_view = await world_service.create_world_view(
            request.core_concept,
            request.description,
            request.additional_requirements
        )
        return world_view.model_dump()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/world/list")
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


@app.get("/api/v1/world/search")
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


@app.get("/api/v1/world/{world_view_id}")
async def get_world_view(world_view_id: str):
    """获取单个世界观详情"""
    try:
        world_view = worldview_db.get_worldview(world_view_id)
        if not world_view:
            raise HTTPException(status_code=404, detail="世界观不存在")
        return world_view
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/v1/world/{world_view_id}")
async def update_world_view(world_view_id: str, request: WorldViewUpdateRequest):
    """更新世界观"""
    try:
        # 检查世界观是否存在
        existing_world_view = worldview_db.get_worldview(world_view_id)
        if not existing_world_view:
            raise HTTPException(status_code=404, detail="世界观不存在")
        
        # 获取更新选项，默认为只更新基本信息
        update_options = request.update_options or {
            "power_system": False,
            "geography": False, 
            "culture": False,
            "history": False
        }
        
        # 检查是否需要重新生成内容
        need_regenerate = any(update_options.values())
        
        if need_regenerate:
            # 需要重新生成部分或全部内容
            core_concept = request.core_concept or existing_world_view.get('core_concept', '')
            description = request.description or existing_world_view.get('description', '')
            additional_requirements = request.additional_requirements or {}
            
            # 使用LLM生成新的世界观内容
            world_view = await world_service.create_world_view(
                core_concept,
                description,
                additional_requirements
            )
            
            # 合并新旧数据：保留不需要更新的维度
            world_view_dict = world_view.model_dump()
            world_view_dict['worldview_id'] = world_view_id
            
            # 如果某个维度不需要更新，保留原有数据
            if not update_options.get("power_system", False):
                world_view_dict['power_system'] = existing_world_view.get('power_system', {})
            if not update_options.get("geography", False):
                world_view_dict['geography'] = existing_world_view.get('geography', {})
            if not update_options.get("culture", False):
                world_view_dict['culture'] = existing_world_view.get('culture', {})
            if not update_options.get("history", False):
                world_view_dict['history'] = existing_world_view.get('history', {})
                
        else:
            # 只更新基本信息，不重新生成内容
            world_view_dict = existing_world_view.copy()
            if request.core_concept is not None:
                world_view_dict['core_concept'] = request.core_concept
            if request.description is not None:
                world_view_dict['description'] = request.description
        
        # 更新数据库
        success = worldview_db.update_worldview(world_view_id, world_view_dict)
        
        if not success:
            raise HTTPException(status_code=500, detail="更新世界观失败")
        
        return world_view_dict
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/v1/world/{world_view_id}")
async def delete_world_view(world_view_id: str):
    """删除世界观"""
    try:
        # 检查世界观是否存在
        existing_world_view = worldview_db.get_worldview(world_view_id)
        if not existing_world_view:
            raise HTTPException(status_code=404, detail="世界观不存在")
        
        # 删除世界观（硬删除，同时删除关联的子表数据）
        success = worldview_db.delete_worldview(world_view_id, soft_delete=False)
        
        if not success:
            raise HTTPException(status_code=500, detail="删除世界观失败")
        
        return {"message": "世界观删除成功", "worldview_id": world_view_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/v1/world/{world_view_id}/partial")
async def partial_update_world_view(
    world_view_id: str,
    request: WorldViewPartialUpdateRequest
):
    """部分更新世界观"""
    try:
        # 1. 获取现有世界观
        existing_worldview = worldview_db.get_worldview(world_view_id)
        if not existing_worldview:
            raise HTTPException(status_code=404, detail="世界观不存在")
        
        # 2. 创建部分更新器
        from app.core.world.part_world_update import PartialWorldUpdateService
        updater = PartialWorldUpdateService()
        
        # 3. 执行部分更新
        updated_data = await updater.update_partial_worldview(
            existing_worldview=existing_worldview,
            update_dimensions=request.update_dimensions,
            update_description=request.update_description,
            additional_context=request.additional_context
        )
        
        # 4. 更新基本信息（如果提供）
        if request.core_concept:
            updated_data['core_concept'] = request.core_concept
        if request.description:
            updated_data['description'] = request.description
        
        # 5. 保存到数据库
        success = worldview_db.update_worldview(world_view_id, updated_data)
        
        if not success:
            raise HTTPException(status_code=500, detail="更新世界观失败")
        
        # 6. 生成更新后的MD文件
        try:
            print(f"开始生成MD文件，世界观名称: {updated_data.get('name', '世界观设计')}")
            from app.utils.file_writer import FileWriter
            file_writer = FileWriter()
            md_content = file_writer._format_world_view(updated_data)
            print(f"MD内容生成成功，长度: {len(md_content)}")
            
            # 使用原有的文件名格式，但更新内容
            import os
            from datetime import datetime
            
            # 获取原有的文件名（如果存在）
            novel_dir = "novel"
            if not os.path.exists(novel_dir):
                os.makedirs(novel_dir)
                print(f"创建novel目录: {novel_dir}")
            
            # 根据世界观ID查找对应的MD文件
            worldview_id = world_view_id
            existing_files = [f for f in os.listdir(novel_dir) if f.startswith("世界观设计_") and f.endswith(".md")]
            print(f"找到现有MD文件: {existing_files}")
            
            # 尝试找到包含该世界观ID的文件
            target_file = None
            for file in existing_files:
                if worldview_id in file:
                    target_file = file
                    print(f"找到包含世界观ID的文件: {file}")
                    break
            
            if target_file:
                # 更新现有文件
                file_path = os.path.join(novel_dir, target_file)
                print(f"将更新现有文件: {file_path}")
            else:
                # 如果没有找到对应文件，创建新的（包含世界观ID）
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                file_path = os.path.join(novel_dir, f"世界观设计_{worldview_id}_{timestamp}.md")
                print(f"将创建新文件: {file_path}")
            
            # 写入更新后的内容
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(md_content)
            
            print(f"MD文件已更新: {file_path}")
        except Exception as e:
            print(f"生成MD文件失败: {e}")
            import traceback
            traceback.print_exc()
            # 不影响主要功能，继续执行
        
        return updated_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "message": "API服务器运行正常"}

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "小说生成API服务器",
        "version": "1.0.0",
        "endpoints": {
            "create_worldview": "/api/v1/world/create",
            "health": "/health",
            "docs": "/docs"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)