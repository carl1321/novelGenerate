"""
世界观服务层
"""
from typing import Dict, List, Any, Optional

from app.core.world.models import WorldView
from app.core.world.rule_engine import RuleEngine
from app.utils.llm_generator import universal_llm_generator
from app.core.world.database import worldview_db
from app.utils.file_writer import FileWriter


class WorldService:
    """世界观服务类"""
    
    def __init__(self):
        self.rule_engine = RuleEngine()
        # 使用通用LLM生成器
        self.file_writer = FileWriter()
    
    async def create_world_view(self, core_concept: str, 
                              description: Optional[str] = None,
                              additional_requirements: Optional[Dict[str, Any]] = None) -> WorldView:
        """创建世界观"""
        try:
            # 使用通用LLM生成器生成世界观
            world_data = await universal_llm_generator.generate_world_view(
                core_concept=core_concept,
                description=description,
                additional_requirements=str(additional_requirements) if additional_requirements else None
            )
            
            # 创建WorldView对象
            world_view = WorldView(
                id=f"world_{hash(core_concept)}",
                name=world_data.get("name", "未命名世界观"),
                description=world_data.get("description", ""),
                core_concept=core_concept,
                power_system=world_data.get("power_system", {}),
                geography=world_data.get("geography", {}),
                culture=world_data.get("society", {}),
                history=world_data.get("history_culture", {}),
                rules=world_data.get("rules", []),
                locations=world_data.get("locations", []),
                organizations=world_data.get("organizations", []),
                techniques=world_data.get("techniques", []),
                artifacts=world_data.get("artifacts", [])
            )
            
            # 存储到PostgreSQL数据库
            try:
                # 构造符合数据库期望格式的数据
                world_view_dict = {
                    'id': world_view.id,
                    'name': world_view.name,
                    'description': world_view.description,
                    'core_concept': world_view.core_concept,
                    'power_system': world_view.power_system,
                    'geography': world_view.geography,
                    'culture': world_view.culture,
                    'history': world_view.history
                }
                worldview_id = worldview_db.insert_worldview(world_view_dict, created_by="system")
                print(f"世界观数据已保存到数据库: {worldview_id}")
            except Exception as db_error:
                print(f"数据库存储失败: {db_error}")
                # 继续执行，不中断流程
            
 
            # 写入markdown文件
            world_view_dict = world_view.model_dump()
            file_path = self.file_writer.write_world_view(world_view_dict)
            print(f"世界观设计已保存到: {file_path}")
            
            return world_view
            
        except Exception as e:
            print(f"创建世界观失败: {e}")
            raise
    
   
    async def get_world_view(self, world_view_id: str) -> Optional[WorldView]:
        """获取世界观"""
        try:
            # 直接从PostgreSQL数据库获取世界观数据
            world_data = worldview_db.get_worldview(world_view_id)
            if world_data:
                return WorldView(
                    id=world_data["worldview_id"],
                    name=world_data["name"],
                    description=world_data["description"],
                    core_concept=world_data["core_concept"],
                    power_system=world_data.get("power_system", {}),
                    geography=world_data.get("geography", {}),
                    history=world_data.get("history", {}),
                    culture=world_data.get("culture", {})
                )
            return None
            
        except Exception as e:
            print(f"获取世界观失败: {e}")
            return None
    
    async def get_world_view_list(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """获取世界观列表"""
        try:
            # 从数据库获取世界观列表
            worldviews = worldview_db.get_worldview_list(limit=limit, offset=offset)
            return worldviews
        except Exception as e:
            print(f"获取世界观列表失败: {e}")
            return []

