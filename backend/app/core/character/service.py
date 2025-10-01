"""
角色管理服务层
"""
import json
import time
import uuid
from typing import Dict, List, Any, Optional
import asyncio
from datetime import datetime

from app.core.character.models import (
    Character, CharacterCard, CharacterTemplate, CharacterGroup, 
    GrowthNode, Relationship, PersonalityTrait, RelationshipType,
    CharacterRoleType, CharacterBatchCreateRequest, CharacterBatchCreateResponse,
    Gender
)
# GrowthPlanner已删除
from app.core.character.relationship_manager import RelationshipManager
from app.utils.llm_generator import universal_llm_generator
# KnowledgeGraph已移除，使用PostgreSQL存储
from app.core.character.database import CharacterDatabase
from app.utils.file_writer import FileWriter
from app.utils.dynamic_parser import dynamic_parser


class CharacterService:
    """角色管理服务类"""
    
    def __init__(self):
        self.relationship_manager = RelationshipManager()
        # 使用通用LLM生成器
        # KnowledgeGraph已移除，使用PostgreSQL存储
        self.file_writer = FileWriter()
        self.character_db = CharacterDatabase()
        self.dynamic_parser = dynamic_parser
        
        # 角色模板库
        self.character_templates = self._load_default_templates()
    
    def _load_default_templates(self) -> List[CharacterTemplate]:
        """加载默认角色模板"""
        templates = [
            CharacterTemplate(
                id="template_young_disciple",
                name="年轻弟子",
                description="初入修炼之路的年轻修士",
                base_personality=[PersonalityTrait.NAIVE, PersonalityTrait.AMBITIOUS, PersonalityTrait.CAUTIOUS],
                common_goals=[{"type": "CULTIVATION", "description": "提升修炼境界"}],
                typical_background="出身平凡，机缘巧合踏上修炼之路",
                suggested_stats={"attack": 3, "defense": 3, "speed": 4, "intelligence": 5}
            ),
            CharacterTemplate(
                id="template_sect_elder",
                name="宗门长老",
                description="宗门中的资深长老",
                base_personality=[PersonalityTrait.WISE, PersonalityTrait.STRICT, PersonalityTrait.LOYAL],
                common_goals=[{"type": "POWER", "description": "维护宗门地位"}],
                typical_background="在宗门中修炼数百年，地位崇高",
                suggested_stats={"attack": 8, "defense": 8, "speed": 6, "intelligence": 9}
            ),
            CharacterTemplate(
                id="template_demon_cultivator",
                name="魔道修士",
                description="修炼魔道功法的修士",
                base_personality=[PersonalityTrait.ARROGANT, PersonalityTrait.VENGEFUL, PersonalityTrait.GREEDY],
                common_goals=[{"type": "POWER", "description": "获得强大力量"}],
                typical_background="因仇恨或欲望走上魔道",
                suggested_stats={"attack": 9, "defense": 6, "speed": 7, "intelligence": 6}
            )
        ]
        return templates
    
    async def create_character(self, world_view_id: str, 
                             character_requirements: Dict[str, Any]) -> Character:
        """创建角色"""
        try:
            # 获取世界观信息
            world_view = await self._get_world_view(world_view_id)
            if not world_view:
                raise Exception("世界观不存在")
            
            # 使用通用LLM生成器生成角色
            from app.utils.llm_generator import universal_llm_generator
            character_data = await universal_llm_generator.generate_character(
                world_name=world_view.get("name", "未知世界观"),
                world_description=world_view.get("description", ""),
                power_system=str(world_view.get("power_system", {})),
                culture=str(world_view.get("culture", {})),
                character_requirements=json.dumps(character_requirements, ensure_ascii=False, indent=2)
            )
            
            # 解析角色数据
            character = await self._parse_character_from_data(character_data, world_view_id)
            
            # 存储到PostgreSQL数据库
            character_db_data = character.model_dump()
            character_db_data["worldview_id"] = world_view_id
            
            # 调试信息
            print(f"存储到数据库的数据 - name: {character_db_data.get('name')}")
            print(f"存储到数据库的数据 - age: {character_db_data.get('age')}")
            print(f"存储到数据库的数据 - gender: {character_db_data.get('gender')}")
            print(f"存储到数据库的数据 - role_type: {character_db_data.get('role_type')}")
            print(f"存储到数据库的数据 - background: {character_db_data.get('background')}")
            print(f"存储到数据库的数据 - personality_traits: {character_db_data.get('personality_traits')}")
            
            character_id = self.character_db.insert_character(character_db_data, created_by="system")
            if not character_id:
                raise Exception("存储角色到数据库失败")
            print(f"角色生成成功: {character.name}, ID: {character_id}")
            
            # 更新角色的ID和worldview_id
            character.id = character_id
            character.worldview_id = world_view_id
            
            # 写入markdown文件
            character_dict = character.dict()
            file_path = self.file_writer.write_character_profile(character_dict)
            print(f"角色档案已保存到: {file_path}")
            
            # 返回LLM生成的角色数据，而不是从数据库查询的数据
            return character
            
        except Exception as e:
            print(f"创建角色失败: {e}")
            raise
    
    async def create_character_from_template(self, world_view_id: str, 
                                           template_id: str, 
                                           customizations: Optional[Dict[str, Any]] = None) -> Character:
        """从模板创建角色"""
        try:
            # 获取模板
            template = next((t for t in self.character_templates if t.id == template_id), None)
            if not template:
                raise Exception("模板不存在")
            
            # 获取世界观信息
            world_view = await self._get_world_view(world_view_id)
            if not world_view:
                raise Exception("世界观不存在")
            
            # 构建角色要求
            character_requirements = {
                "template": template.name,
                "personality": [trait.value for trait in template.base_personality],
                "goals": template.common_goals,
                "background": template.typical_background,
                "stats": template.suggested_stats
            }
            
            # 应用自定义设置
            if customizations:
                character_requirements.update(customizations)
            
            # 生成角色
            character = await self.llm_generator.generate_character(
                world_view, character_requirements
            )
            
            # 存储到知识图谱
            # 存储到PostgreSQL数据库
            character_data = character.model_dump()
            character_data["worldview_id"] = world_view_id
            character_id = self.character_db.insert_character(character_data, created_by="system")
            if not character_id:
                raise Exception("存储角色到数据库失败")
            print(f"角色生成成功: {character.name}, ID: {character_id}")
            
            return character
            
        except Exception as e:
            print(f"从模板创建角色失败: {e}")
            raise
    
    async def generate_character_card(self, character_id: str) -> CharacterCard:
        """生成角色卡片"""
        try:
            # 获取角色信息
            character = await self.get_character(character_id)
            if not character:
                raise Exception("角色不存在")
            
            # 生成角色卡片
            character_card = await self.llm_generator.generate_character_card(character)
            
            return character_card
            
        except Exception as e:
            print(f"生成角色卡片失败: {e}")
            raise
    
    async def plan_character_growth(self, character_id: str, 
                                  target_level: Optional[str] = None) -> List[GrowthNode]:
        """规划角色成长轨迹"""
        try:
            # 获取角色信息
            character = await self.get_character(character_id)
            if not character:
                raise Exception("角色不存在")
            
            # 规划成长轨迹
            if target_level:
                from app.core.world.models import CultivationLevel
                target_cultivation_level = CultivationLevel(target_level)
            else:
                target_cultivation_level = None
            
            growth_nodes = self.growth_planner.plan_character_growth(
                character, target_cultivation_level
            )
            
            return growth_nodes
            
        except Exception as e:
            print(f"规划角色成长失败: {e}")
            raise
    
    async def create_relationship(self, character1_id: str, character2_id: str,
                                relationship_type: str, 
                                intimacy_level: int = 5, 
                                trust_level: int = 5) -> Relationship:
        """创建角色关系"""
        try:
            # 获取角色信息
            character1 = await self.get_character(character1_id)
            character2 = await self.get_character(character2_id)
            
            if not character1 or not character2:
                raise Exception("角色不存在")
            
            # 创建关系
            relationship = self.relationship_manager.create_relationship(
                character1, character2, RelationshipType(relationship_type),
                intimacy_level, trust_level
            )
            
            return relationship
            
        except Exception as e:
            print(f"创建角色关系失败: {e}")
            raise
    
    async def get_character_network(self, character_id: str, depth: int = 2) -> Dict[str, Any]:
        """获取角色关系网络"""
        try:
            # 获取角色信息
            character = await self.get_character(character_id)
            if not character:
                raise Exception("角色不存在")
            
            # TODO: 从PostgreSQL获取关系网络
            # network = await self.knowledge_graph.get_character_network(character_id, depth)
            network = {"nodes": [], "edges": []}
            
            return network
            
        except Exception as e:
            print(f"获取角色网络失败: {e}")
            raise
    
    async def get_character(self, character_id: str) -> Optional[Character]:
        """获取角色信息"""
        try:
            # 从PostgreSQL查询角色
            char_data = self.character_db.get_character(character_id)
            if char_data:
                return self._parse_character_from_db_data(char_data)
            return None
            
        except Exception as e:
            print(f"获取角色信息失败: {e}")
            return None
    
    async def delete_character(self, character_id: str) -> bool:
        """删除角色"""
        try:
            # 使用PostgreSQL删除角色（软删除）
            return self.character_db.delete_character(character_id)
        except Exception as e:
            print(f"删除角色失败: {e}")
            return False
    
    async def search_characters(self, keyword: str, filters: Optional[Dict[str, Any]] = None) -> List[Character]:
        """搜索角色"""
        try:
            # 使用PostgreSQL搜索角色
            worldview_id = filters.get("worldview_id") if filters else None
            role_type = filters.get("role_type") if filters else None
            
            results = self.character_db.search_characters(
                keyword=keyword,
                worldview_id=worldview_id,
                role_type=role_type
            )
            
            characters = []
            for char_data in results:
                # 调试信息：检查数据库返回的原始数据
                import logging
                logger = logging.getLogger(__name__)
                logger.debug(f"数据库原始数据 - character_id: {char_data.get('character_id')}")
                logger.debug(f"数据库原始数据 - worldview_id: {char_data.get('worldview_id')}")
                logger.debug(f"数据库原始数据 - name: {char_data.get('name')}")
                
                character = self._parse_character_from_db_data(char_data)
                
                # 调试信息：检查解析后的角色对象
                logger.debug(f"解析后角色对象 - id: {character.id}")
                logger.debug(f"解析后角色对象 - worldview_id: {character.worldview_id}")
                logger.debug(f"解析后角色对象 - name: {character.name}")
                
                characters.append(character)
            
            return characters
            
        except Exception as e:
            print(f"搜索角色失败: {e}")
            return []
    
    async def delete_character(self, character_id: str) -> bool:
        """删除角色"""
        try:
            success = self.character_db.delete_character(character_id)
            return success
            
        except Exception as e:
            print(f"删除角色失败: {e}")
            return False
    
    async def get_character_templates(self) -> List[CharacterTemplate]:
        """获取角色模板列表"""
        return self.character_templates
    
    async def create_character_group(self, group_name: str, character_ids: List[str],
                                   group_type: str = "custom") -> CharacterGroup:
        """创建角色组"""
        try:
            group = CharacterGroup(
                id=f"group_{hash(group_name)}_{int(datetime.now().timestamp())}",
                name=group_name,
                description=f"{group_type}类型的角色组",
                character_ids=character_ids,
                group_type=group_type
            )
            
            return group
            
        except Exception as e:
            print(f"创建角色组失败: {e}")
            raise
    
    async def analyze_character_consistency(self, character_id: str, 
                                          situation: str, action: str) -> Dict[str, Any]:
        """分析角色行为一致性"""
        try:
            # 获取角色信息
            character = await self.get_character(character_id)
            if not character:
                raise Exception("角色不存在")
            
            # 分析一致性
            analysis = await self.llm_generator.analyze_character_consistency(
                character, situation, action
            )
            
            return analysis
            
        except Exception as e:
            print(f"分析角色一致性失败: {e}")
            raise
    
    async def generate_character_dialogue(self, character_id: str, 
                                        situation: str) -> List[str]:
        """生成角色对话"""
        try:
            # 获取角色信息
            character = await self.get_character(character_id)
            if not character:
                raise Exception("角色不存在")
            
            # 生成对话
            dialogue = await self.llm_generator.generate_character_dialogue(
                character, situation
            )
            
            return dialogue
            
        except Exception as e:
            print(f"生成角色对话失败: {e}")
            raise
    
    async def expand_character_background(self, character_id: str, 
                                        expansion_type: str) -> Dict[str, Any]:
        """扩展角色背景"""
        try:
            # 获取角色信息
            character = await self.get_character(character_id)
            if not character:
                raise Exception("角色不存在")
            
            # 扩展背景
            expansion = await self.llm_generator.expand_character_background(
                character, expansion_type
            )
            
            return expansion
            
        except Exception as e:
            print(f"扩展角色背景失败: {e}")
            raise
    
    async def simulate_character_growth(self, character_id: str, 
                                      growth_nodes: List[GrowthNode], 
                                      years: int) -> Dict[str, Any]:
        """模拟角色成长过程"""
        try:
            # 获取角色信息
            character = await self.get_character(character_id)
            if not character:
                raise Exception("角色不存在")
            
            # 模拟成长
            simulation = self.growth_planner.simulate_growth(
                character, growth_nodes, years
            )
            
            return simulation
            
        except Exception as e:
            print(f"模拟角色成长失败: {e}")
            raise
    
    async def get_growth_suggestions(self, character_id: str) -> List[str]:
        """获取成长建议"""
        try:
            # 获取角色信息
            character = await self.get_character(character_id)
            if not character:
                raise Exception("角色不存在")
            
            # 获取建议
            suggestions = self.growth_planner.get_growth_suggestions(character)
            
            return suggestions
            
        except Exception as e:
            print(f"获取成长建议失败: {e}")
            raise
    
    async def create_characters_batch(self, request: CharacterBatchCreateRequest) -> CharacterBatchCreateResponse:
        """批量创建角色"""
        try:
            # 获取世界观信息
            world_view = await self._get_world_view(request.worldview_id)
            if not world_view:
                raise Exception("世界观不存在")
            
            # 使用通用LLM生成器批量生成角色
            from app.utils.llm_generator import universal_llm_generator
            characters_data = await universal_llm_generator.generate_characters_batch(
                world_name=world_view.get("name", "未知世界观"),
                world_description=world_view.get("description", ""),
                power_system=str(world_view.get("power_system", {})),
                culture=str(world_view.get("culture", {})),
                character_description=request.description,
                character_count=request.character_count,
                role_types=[role_type.value for role_type in request.role_types]
            )
            
            # 解析角色数据
            characters = []
            if "characters" in characters_data:
                for char_data in characters_data["characters"]:
                    character = await self._parse_character_from_data(char_data, request.worldview_id)
                    characters.append(character)
            
            # 存储角色到PostgreSQL数据库
            created_characters = []
            for character in characters:
                character_db_data = character.model_dump()
                character_db_data["worldview_id"] = request.worldview_id
                character_id = self.character_db.insert_character(character_db_data, created_by="system")
                if character_id:
                    # 更新角色的ID和worldview_id
                    character.id = character_id
                    character.worldview_id = request.worldview_id
                    created_characters.append(character)
                    # 写入markdown文件
                    character_dict = character.dict()
                    file_path = self.file_writer.write_character_profile(character_dict)
                    print(f"角色档案已保存到: {file_path}")
            
            return CharacterBatchCreateResponse(
                success=True,
                characters=created_characters,
                message=f"成功创建{len(created_characters)}个角色",
                total_count=len(created_characters)
            )
            
        except Exception as e:
            print(f"批量创建角色失败: {e}")
            return CharacterBatchCreateResponse(
                success=False,
                characters=[],
                message=f"批量创建角色失败: {str(e)}",
                total_count=0
            )
    
    async def _parse_character_from_data(self, character_data: Dict[str, Any], worldview_id: str = None) -> Character:
        """从LLM返回的数据解析角色对象"""
        try:
            # 生成唯一ID
            character_id = f"char_{uuid.uuid4().hex[:12]}"
            
            # 解析基本属性 - 支持嵌套结构
            basic_info = character_data.get("basic_info", {})
            name = basic_info.get("name") or character_data.get("name") or "未命名角色"
            age = basic_info.get("age") or character_data.get("age") or 20
            # 使用动态解析器解析性别
            gender_str = basic_info.get("gender") or character_data.get("gender") or "男"
            gender = await self.dynamic_parser.parse_gender(gender_str)
            # 使用动态解析器解析角色类型
            role_type_str = basic_info.get("role_type") or character_data.get("role_type") or "正义伙伴"
            role_type = await self.dynamic_parser.parse_role_type(role_type_str)
            
            # 调试信息
            print(f"解析调试 - basic_info: {basic_info}")
            print(f"解析调试 - name: {name}")
            print(f"解析调试 - age: {age}")
            print(f"解析调试 - gender: {gender}")
            print(f"解析调试 - role_type: {role_type}")
            
            # 解析外貌信息
            appearance = basic_info.get("appearance", "")
            
            # 解析性格特质
            personality = character_data.get("personality", {})
            personality_traits_raw = personality.get("traits", [])
            # 转换为字典格式
            personality_traits = [{"trait": trait, "level": 5} for trait in personality_traits_raw]
            values = personality.get("values", "")
            fears = personality.get("fears", "")
            desires = personality.get("desires", "")
            
            # 解析能力设定
            abilities = character_data.get("abilities", {})
            skills = abilities.get("skills", [])
            weaknesses = abilities.get("weaknesses", [])
            growth_potential = abilities.get("growth_potential", "")
            
            # 解析社会关系
            relationships_data = character_data.get("relationships", {})
            family = relationships_data.get("family", "")
            master = relationships_data.get("master", "")
            friends = relationships_data.get("friends", [])
            enemies = relationships_data.get("enemies", [])
            
            # 解析成长弧线
            character_arc = character_data.get("character_arc", {})
            initial_state = character_arc.get("initial_state", "")
            turning_point = character_arc.get("turning_point", "")
            final_goal = character_arc.get("final_goal", "")
            
            # 构建背景信息（整合多个维度）
            background_parts = []
            if family:
                background_parts.append(f"出身：{family}")
            if master:
                background_parts.append(f"师门：{master}")
            if initial_state:
                background_parts.append(f"初始状态：{initial_state}")
            background = "；".join(background_parts) if background_parts else ""
            
            # 构建目标信息
            goals = []
            if final_goal:
                goals.append({"goal": final_goal, "type": "长期目标"})
            if desires:
                goals.append({"goal": desires, "type": "欲望"})
            
            # 构建关系信息
            relationships = {
                "family": family,
                "master": master,
                "friends": friends,
                "enemies": enemies
            }
            
            # 构建技能和法宝信息
            techniques = [{"name": skill, "level": "初级"} for skill in skills]
            artifacts = [{"name": weakness, "type": "弱点"} for weakness in weaknesses]
            
            # 构建资源和统计信息
            resources = {
                "growth_potential": growth_potential,
                "values": values,
                "fears": fears
            }
            
            stats = {
                "turning_point": turning_point
            }
            
            metadata = {
                "appearance": appearance
            }
            
            # 设置默认值
            cultivation_level = ""
            element_type = ""
            current_location = ""
            organization_id = ""
            
            # 创建角色对象
            character = Character(
                id=character_id,
                worldview_id=worldview_id or "unknown",  # 使用传入的worldview_id或默认值
                name=name,
                age=age,
                gender=gender,
                role_type=role_type,
                cultivation_level=cultivation_level,
                element_type=element_type,
                background=background,
                current_location=current_location,
                organization_id=organization_id,
                personality_traits=personality_traits,
                goals=goals,
                relationships=relationships,
                techniques=techniques,
                artifacts=artifacts,
                resources=resources,
                stats=stats,
                metadata=metadata
            )
            
            return character
            
        except Exception as e:
            print(f"解析角色数据失败: {e}")
            raise
    
    def _parse_character_from_db_data(self, char_data: Dict[str, Any]) -> Character:
        """从数据库数据解析角色对象"""
        try:
            # 解析基本属性
            character_id = char_data.get("character_id")
            worldview_id = char_data.get("worldview_id")
            name = char_data.get("name", "未命名角色")
            age = char_data.get("age", 20)
            gender = Gender(char_data.get("gender", "男"))
            role_type = CharacterRoleType(char_data.get("role_type", "配角"))
            
            # 解析修炼相关属性
            cultivation_level = char_data.get("cultivation_level", "")
            element_type = char_data.get("element_type", "")
            
            # 解析背景和位置
            background = char_data.get("background", "")
            current_location = char_data.get("current_location", "")
            organization_id = char_data.get("organization_id", "")
            
            # 解析复杂属性（JSONB存储）
            personality_traits = char_data.get("personality_traits", [])
            goals = char_data.get("goals", [])
            relationships = char_data.get("relationships", {})
            techniques = char_data.get("techniques", [])
            artifacts = char_data.get("artifacts", [])
            resources = char_data.get("resources", {})
            stats = char_data.get("stats", {})
            metadata = char_data.get("metadata", {})
            
            # 创建角色对象
            character = Character(
                id=character_id,
                worldview_id=worldview_id,
                name=name,
                age=age,
                gender=gender,
                role_type=role_type,
                cultivation_level=cultivation_level,
                element_type=element_type,
                background=background,
                current_location=current_location,
                organization_id=organization_id,
                personality_traits=personality_traits,
                goals=goals,
                relationships=relationships,
                techniques=techniques,
                artifacts=artifacts,
                resources=resources,
                stats=stats,
                metadata=metadata
            )
            
            return character
            
        except Exception as e:
            print(f"解析数据库角色数据失败: {e}")
            raise
    
    async def _get_world_view(self, world_view_id: str) -> Optional[Dict[str, Any]]:
        """获取世界观信息"""
        try:
            # 从PostgreSQL数据库获取世界观信息
            from app.core.world.database import worldview_db
            world_data = worldview_db.get_worldview(world_view_id)
            if world_data:
                return world_data
            return None
        except Exception as e:
            print(f"获取世界观信息失败: {e}")
            return None
    
    async def update_character(self, character_id: str, updates: Dict[str, Any]) -> bool:
        """更新角色信息"""
        try:
            # 直接从数据库获取现有角色数据
            char_data = self.character_db.get_character(character_id)
            if not char_data:
                return False
            
            # 构建更新数据
            update_data = {
                "name": char_data.get("name"),
                "age": char_data.get("age"),
                "gender": char_data.get("gender"),
                "role_type": char_data.get("role_type"),
                "cultivation_level": char_data.get("cultivation_level"),
                "element_type": char_data.get("element_type"),
                "background": char_data.get("background"),
                "current_location": char_data.get("current_location"),
                "organization_id": char_data.get("organization_id"),
                "personality_traits": char_data.get("personality_traits"),
                "goals": char_data.get("goals"),
                "relationships": char_data.get("relationships"),
                "techniques": char_data.get("techniques"),
                "artifacts": char_data.get("artifacts"),
                "resources": char_data.get("resources"),
                "stats": char_data.get("stats"),
                "metadata": char_data.get("metadata"),
                "status": char_data.get("status")
            }
            
            # 应用更新
            if "description" in updates:
                update_data["background"] = updates["description"]
            if "role_type" in updates:
                update_data["role_type"] = updates["role_type"]
            if "worldview_id" in updates:
                update_data["worldview_id"] = updates["worldview_id"]
            if "name" in updates:
                update_data["name"] = updates["name"]
            if "age" in updates:
                update_data["age"] = updates["age"]
            if "gender" in updates:
                update_data["gender"] = updates["gender"]
            
            # 更新数据库
            success = self.character_db.update_character(character_id, update_data)
            return success
            
        except Exception as e:
            print(f"更新角色失败: {e}")
            return False
    
    async def delete_character(self, character_id: str) -> bool:
        """删除角色"""
        try:
            success = self.character_db.delete_character(character_id)
            print(f"删除角色结果: {success}")
            return success
            
        except Exception as e:
            print(f"删除角色失败: {e}")
            raise e  # 重新抛出异常，让API层处理

    def close(self):
        """关闭服务"""
        # self.knowledge_graph.close()
