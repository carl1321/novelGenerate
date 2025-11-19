"""
剧情大纲生成引擎 - 专注于故事框架设计
"""
import json
import uuid
import time
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.utils.llm_client import get_llm_client
from app.utils.prompt_manager import PromptManager
from app.utils.markdown_generator import MarkdownGenerator
from app.utils.logger import debug_log, error_log, info_log
from .plot_database import PlotOutlineDatabase
import sys
import os

# 添加prompts目录到Python路径
# 直接使用项目根目录的prompts路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../'))
prompts_path = os.path.join(project_root, 'prompts')
if prompts_path not in sys.path:
    sys.path.insert(0, prompts_path)

try:
    debug_log("plot_outline_generation 导入成功")
except ImportError as e:
    error_log("plot_outline_generation 导入失败", e)
    error_log("当前sys.path", sys.path[:3])
    error_log("prompts路径", prompts_path)
    error_log("prompts目录存在", os.path.exists(prompts_path))
    # 如果导入失败，使用默认的prompt函数
    def get_plot_outline_prompt(*args, **kwargs):
        return "生成剧情大纲的prompt"
from .plot_models import (
    PlotOutline, PlotOutlineRequest, PlotOutlineResponse,
    StoryFramework, CharacterPosition, PlotBlock,
    StoryFlow, Act, TurningPoint, PlotPoint, EmotionalBeat,
    PlotStatus, PlotStructure, ConflictType, NarrativeStructure
)


class PlotOutlineEngine:
    """剧情大纲生成引擎 - 专注于故事框架"""
    
    def __init__(self):
        self.llm_client = get_llm_client()
        self.prompt_manager = PromptManager()
        self.markdown_generator = MarkdownGenerator()
        self.plot_database = PlotOutlineDatabase()
    
    async def generate_plot_outline(self, request: PlotOutlineRequest) -> PlotOutlineResponse:
        """生成剧情大纲 - 简化版故事驱动模式"""
        start_time = time.time()
        plot_id = f"plot_{uuid.uuid4().hex[:8]}"
        
        try:
            debug_log("开始生成剧情大纲", request.title)
            debug_log("剧情大纲ID", plot_id)
            
            # 1. 从数据库查询世界观信息
            worldview_info = await self._get_worldview_context(request.worldview_id)
            debug_log("获取世界观信息", worldview_info.get('name', '未知'))
            
            # 2. 从数据库查询主角信息
            protagonist_info = await self._get_protagonist_context(request.protagonist_character_id)
            debug_log("获取主角信息", protagonist_info.get('name', '未知'))
            
            # 3. 生成剧情大纲数据
            debug_log("开始调用LLM生成剧情大纲数据...")
            plot_outline_data = await self._generate_plot_outline_data(
                request, worldview_info, protagonist_info
            )
            debug_log("LLM生成完成，数据长度", len(str(plot_outline_data)))
            
            # 4. 创建剧情大纲对象
            plot_outline = await self._create_plot_outline(
                plot_id, request, worldview_info, protagonist_info, plot_outline_data
            )
            
            # 5. 保存到数据库
            try:
                save_success = self.plot_database.save_plot_outline(plot_outline)
                if save_success:
                    info_log("剧情大纲已保存到数据库", plot_id)
                else:
                    error_log("剧情大纲保存到数据库失败", plot_id)
            except Exception as e:
                error_log("数据库保存异常", e)
            
            # 6. 生成MD文件
            try:
                md_file_path = self.markdown_generator.generate_plot_outline_md(plot_outline.dict())
                info_log("剧情大纲MD文件已生成", md_file_path)
            except Exception as e:
                error_log("MD文件生成失败", e)
            
            end_time = time.time()
            generation_time = end_time - start_time
            
            return PlotOutlineResponse(
                success=True,
                plot_outline=plot_outline,
                message="剧情大纲生成成功",
                generation_time=generation_time
            )
            
        except Exception as e:
            error_log("剧情大纲生成异常", e)
            import traceback
            error_log("异常堆栈", traceback.format_exc())
            
            end_time = time.time()
            generation_time = end_time - start_time
            return PlotOutlineResponse(
                success=False,
                plot_outline=None,
                message=f"剧情大纲生成失败: {e}",
                generation_time=generation_time
            )
    
    async def _get_worldview_context(self, worldview_id: str) -> Dict[str, Any]:
        """从数据库获取世界观信息"""
        try:
            from app.core.world.database import worldview_db
            worldview_data = worldview_db.get_worldview(worldview_id)
            if not worldview_data:
                info_log("世界观不存在，使用默认数据", worldview_id)
                return self._get_default_worldview_context(worldview_id)
            
            debug_log("成功获取世界观", worldview_data.get('name', '未知'))
            return worldview_data
            
        except Exception as e:
            error_log("获取世界观信息失败", e)
            return self._get_default_worldview_context(worldview_id)
    
    def _get_default_worldview_context(self, worldview_id: str) -> Dict[str, Any]:
        """获取默认世界观信息（当数据库查询失败时使用）"""
        return {
            "id": worldview_id,
            "name": "默认世界观",
            "description": "一个修仙世界",
            "core_concept": "修仙修炼体系",
            "power_system": {
                "cultivation_realms": [
                    {"name": "练气期", "level": 1, "description": "初入修炼，感受灵气"},
                    {"name": "筑基期", "level": 2, "description": "奠定修炼基础"},
                    {"name": "金丹期", "level": 3, "description": "凝聚金丹，实力大增"}
                ],
                "energy_types": [
                    {"name": "灵气", "rarity": "常见", "description": "基础修炼能量"}
                ],
                "technique_categories": [
                    {"name": "心法", "description": "核心修炼功法", "difficulty": "中等"}
                ]
            },
            "geography": {
                "main_regions": [
                    {"name": "东域", "type": "大陆", "description": "修仙圣地，灵气浓郁"}
                ],
                "special_locations": [
                    {"name": "修炼洞府", "type": "秘境", "description": "修炼宝地"}
                ]
            },
            "history": {
                "historical_events": [
                    {"name": "修仙起源", "time_period": "远古", "description": "修仙体系的建立"}
                ],
                "cultural_features": [
                    {"region": "东域", "traditions": "修仙传统", "values": "追求长生", "lifestyle": "修炼为主"}
                ],
                "current_conflicts": [
                    {"name": "正邪之争", "description": "正派与邪派的冲突"}
                ]
            },
            "culture": {
                "organizations": [
                    {"name": "修仙宗门", "type": "宗门", "description": "修仙组织"}
                ],
                "social_system": {
                    "hierarchy": "以修为定地位",
                    "economy": "以灵石为货币",
                    "trading": "修炼资源交易"
                }
            }
        }
    
    async def _get_characters_context(self, worldview_id: str) -> List[Dict[str, Any]]:
        """从数据库获取角色信息"""
        try:
            from app.core.character.database import CharacterDatabase
            character_db = CharacterDatabase()
            characters = character_db.get_characters_by_worldview(worldview_id)
            
            if not characters:
                info_log("世界观没有角色，使用默认角色", worldview_id)
                return self._get_default_characters_context()
            
            # 转换角色数据格式（适配新的表结构）
            characters_info = []
            for char in characters:
                char_info = {
                    "id": char.get("character_id"),
                    "name": char.get("name", "未知角色"),
                    "role_type": char.get("role_type", "配角"),
                    "age": char.get("age"),
                    "gender": char.get("gender"),
                    "cultivation_level": char.get("cultivation_level", ""),
                    "element_type": char.get("element_type", ""),
                    "background": char.get("background", ""),
                    "current_location": char.get("current_location", ""),
                    "organization_id": char.get("organization_id", ""),
                    
                    # 新增的文本字段
                    "personality_traits": char.get("personality_traits", ""),
                    "main_goals": char.get("main_goals", ""),
                    "short_term_goals": char.get("short_term_goals", ""),
                    "weaknesses": char.get("weaknesses", ""),
                    "appearance": char.get("appearance", ""),
                    "turning_point": char.get("turning_point", ""),
                    "relationship_text": char.get("relationship_text", ""),
                    "values": char.get("values", ""),
                    
                    # JSONB字段
                    "techniques": char.get("techniques", []),
                    "stats": char.get("stats", {}),
                    "metadata": char.get("metadata", {})
                }
                characters_info.append(char_info)
            
            debug_log("成功获取角色数量", len(characters_info))
            return characters_info
            
        except Exception as e:
            error_log("获取角色信息失败", e)
            return self._get_default_characters_context()
    
    def _get_default_characters_context(self) -> List[Dict[str, Any]]:
        """获取默认角色信息（当数据库查询失败时使用）"""
        return [
            {
                "id": "default_protagonist",
                "name": "主角",
                "role_type": "主角",
                "age": 18,
                "gender": "男",
                "cultivation_level": "练气期",
                "element_type": "火",
                "background": "普通少年，意外获得修炼机会",
                "current_location": "青云宗",
                "organization_id": "青云宗",
                "personality_traits": "勇敢无畏，正义感强，但有时过于冲动",
                "main_goals": "成为绝世强者，保护重要的人",
                "short_term_goals": "突破到筑基期，学会新的剑法",
                "weaknesses": "经验不足，容易轻信他人",
                "appearance": "清秀少年，眼神坚毅",
                "turning_point": "意外获得神秘功法",
                "relationship_text": "与师父关系深厚，与同门师兄弟情同手足",
                "values": "坚持正义，保护弱小，追求武道极致",
                "techniques": [
                    {"name": "基础剑法", "level": "入门", "description": "青云宗基础剑法"},
                    {"name": "火系心法", "level": "初级", "description": "火属性修炼心法"}
                ],
                "stats": {"attack": 5, "defense": 4, "speed": 6},
                "metadata": {}
            },
            {
                "id": "default_antagonist",
                "name": "反派",
                "role_type": "反派",
                "age": 35,
                "gender": "男",
                "cultivation_level": "金丹期",
                "element_type": "暗",
                "background": "修炼多年的魔道修士",
                "current_location": "魔教总坛",
                "organization_id": "魔教",
                "personality_traits": "冷酷无情，野心勃勃，为达目的不择手段",
                "main_goals": "统治修仙界，获得无上力量",
                "short_term_goals": "突破到元婴期，消灭正道宗门",
                "weaknesses": "过于自负，轻视对手",
                "appearance": "阴森恐怖，眼神如毒蛇",
                "turning_point": "修炼魔功走火入魔",
                "relationship_text": "与魔教众人关系复杂，互相利用",
                "values": "力量至上，弱肉强食，不择手段",
                "techniques": [
                    {"name": "魔道心法", "level": "高级", "description": "邪恶的修炼功法"},
                    {"name": "暗系法术", "level": "中级", "description": "黑暗系攻击法术"}
                ],
                "stats": {"attack": 8, "defense": 7, "speed": 5},
                "metadata": {}
            }
        ]
    
    async def _generate_plot_outline_data(self, request: PlotOutlineRequest, 
                                        worldview_info: Dict[str, Any], 
                                        protagonist_info: Dict[str, Any]) -> Dict[str, Any]:
        """生成剧情大纲数据 - 简化版故事驱动模式"""
        debug_log("构建prompt开始...")
        debug_log("请求参数", f"title={request.title}, core_conflict={request.core_conflict}")
        debug_log("世界观信息", worldview_info)
        debug_log("主角信息", protagonist_info)
        
        # 构建prompt
        try:
            prompt = self.prompt_manager.get_plot_outline_prompt(
                core_concept=worldview_info.get("core_concept", "修仙世界"),
                world_description=worldview_info.get("description", "一个修仙世界"),
                geography_setting=self._format_geography(worldview_info.get("geography", {})),
                protagonist_name=protagonist_info.get("name", "主角"),
                protagonist_background=protagonist_info.get("background", ""),
                protagonist_personality=protagonist_info.get("personality_traits", ""),
                protagonist_goals=protagonist_info.get("main_goals", ""),
                core_conflict=request.core_conflict,
                story_tone=request.story_tone,
                narrative_structure=request.narrative_structure,
                story_structure=request.story_structure,
                theme=request.theme,
                target_word_count=request.target_word_count,
                estimated_chapters=request.estimated_chapters
            )
            debug_log("prompt构建成功")
        except Exception as e:
            error_log("prompt构建失败", e)
            raise
        
        debug_log("prompt长度", len(prompt))
        debug_log("prompt前200字符", prompt[:200])
        
        # 调用LLM生成
        debug_log("开始调用LLM...")
        response = await self.llm_client.generate_text(prompt)
        debug_log("LLM响应长度", len(response))
        debug_log("LLM响应前200字符", response[:200])
        
        # 解析响应
        try:
            debug_log("开始解析JSON...")
            debug_log("原始响应", response)
            
            # 尝试提取JSON部分
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                debug_log("提取的JSON字符串", json_str[:200])
                plot_outline_data = json.loads(json_str)
            else:
                # 如果没有找到JSON，尝试直接解析整个响应
                plot_outline_data = json.loads(response)
            
            debug_log("JSON解析成功，包含字段", list(plot_outline_data.keys()))
            
            # 验证和修复narrative_style字段
            if "story_framework" in plot_outline_data:
                story_framework = plot_outline_data["story_framework"]
                if "narrative_style" in story_framework:
                    narrative_style = story_framework["narrative_style"]
                    valid_styles = ["线性叙事", "非线性叙事", "多视角叙事", "书信体", "意识流"]
                    
                    if narrative_style not in valid_styles:
                        info_log("narrative_style值无效", narrative_style)
                        # 根据请求的narrative_structure映射到正确的枚举值
                        mapping = {
                            "线性叙事": "线性叙事",
                            "非线性叙事": "非线性叙事", 
                            "多视角叙事": "多视角叙事",
                            "书信体": "书信体",
                            "意识流": "意识流"
                        }
                        # 如果请求的narrative_structure在映射中，使用它；否则默认使用"线性叙事"
                        fixed_style = mapping.get(request.narrative_structure, "线性叙事")
                        story_framework["narrative_style"] = fixed_style
                        info_log("已修复narrative_style", fixed_style)
            
            return plot_outline_data
        except json.JSONDecodeError as e:
            # 输出原始响应用于调试
            error_log("LLM原始响应", response[:500])
            raise ValueError(f"LLM响应解析失败: {e}")
    
    async def _get_protagonist_context(self, character_id: str) -> Dict[str, Any]:
        """从数据库获取主角信息"""
        try:
            from app.core.character.database import CharacterDatabase
            character_db = CharacterDatabase()
            character_data = character_db.get_character(character_id)
            
            if not character_data:
                info_log("主角不存在，使用默认数据", character_id)
                return self._get_default_protagonist_context()
            
            # 转换角色数据格式
            protagonist_info = {
                "id": character_data.get("character_id"),
                "name": character_data.get("name", "未知角色"),
                "background": character_data.get("background", ""),
                "personality_traits": character_data.get("personality_traits", ""),
                "main_goals": character_data.get("main_goals", ""),
                "short_term_goals": character_data.get("short_term_goals", ""),
                "age": character_data.get("age"),
                "gender": character_data.get("gender"),
                "cultivation_level": character_data.get("cultivation_level", ""),
                "element_type": character_data.get("element_type", ""),
                "current_location": character_data.get("current_location", ""),
                "organization_id": character_data.get("organization_id", ""),
                "weaknesses": character_data.get("weaknesses", ""),
                "appearance": character_data.get("appearance", ""),
                "turning_point": character_data.get("turning_point", ""),
                "values": character_data.get("values", ""),
                "techniques": character_data.get("techniques", [])
            }
            
            debug_log("成功获取主角信息", protagonist_info.get('name', '未知'))
            return protagonist_info
            
        except Exception as e:
            error_log("获取主角信息失败", e)
            return self._get_default_protagonist_context()
    
    def _get_default_protagonist_context(self) -> Dict[str, Any]:
        """获取默认主角信息（当数据库查询失败时使用）"""
        return {
            "id": "default_protagonist",
            "name": "主角",
            "background": "普通少年，意外获得修炼机会",
            "personality_traits": "勇敢无畏，正义感强，但有时过于冲动",
            "main_goals": "成为绝世强者，保护重要的人",
            "short_term_goals": "突破到筑基期，学会新的剑法",
            "age": 18,
            "gender": "男",
            "cultivation_level": "练气期",
            "element_type": "火",
            "current_location": "青云宗",
            "organization_id": "青云宗",
            "weaknesses": "经验不足，容易轻信他人",
            "appearance": "清秀少年，眼神坚毅",
            "turning_point": "意外获得神秘功法",
            "values": "坚持正义，保护弱小，追求武道极致",
            "techniques": [
                {"name": "基础剑法", "level": "入门", "description": "青云宗基础剑法"},
                {"name": "火系心法", "level": "初级", "description": "火属性修炼心法"}
            ]
        }
    
    async def _create_plot_outline(self, plot_id: str, request: PlotOutlineRequest,
                                worldview_info: Dict[str, Any], protagonist_info: Dict[str, Any],
                                plot_data: Dict[str, Any]) -> PlotOutline:
        """创建剧情大纲对象"""
        try:
            from app.core.plot_engine.plot_models import ActStructure
            
            # 解析幕次数据
            acts = []
            if "acts" in plot_data and isinstance(plot_data["acts"], list):
                for act_data in plot_data["acts"]:
                    act = ActStructure(
                        act_number=act_data.get("act_number", 1),
                        act_name=act_data.get("act_name", "未知幕次"),
                        core_mission=act_data.get("core_mission", ""),
                        daily_events=act_data.get("daily_events", ""),
                        conflict_events=act_data.get("conflict_events", ""),
                        special_events=act_data.get("special_events", ""),
                        major_events=act_data.get("major_events", ""),
                        stage_result=act_data.get("stage_result", "")
                    )
                    acts.append(act)
            
            # 创建剧情大纲对象
            plot_outline = PlotOutline(
                id=plot_id,
                worldview_id=request.worldview_id,
                title=request.title,
                story_summary=plot_data.get("story_summary", ""),
                core_conflict=request.core_conflict,
                story_tone=request.story_tone,
                narrative_structure=request.narrative_structure,
                theme=request.theme,
                protagonist_name=protagonist_info.get("name", "主角"),
                protagonist_background=protagonist_info.get("background", ""),
                protagonist_personality=protagonist_info.get("personality_traits", ""),
                protagonist_goals=protagonist_info.get("main_goals", ""),
                core_concept=worldview_info.get("core_concept", "修仙世界"),
                world_description=worldview_info.get("description", "一个修仙世界"),
                geography_setting=self._format_geography(worldview_info.get("geography", {})),
                acts=acts,
                target_word_count=request.target_word_count,
                estimated_chapters=request.estimated_chapters
            )
            
            debug_log("剧情大纲对象创建成功", plot_outline.title)
            return plot_outline
            
        except Exception as e:
            error_log("创建剧情大纲对象失败", e)
            raise
    
    def _format_geography(self, geography_info: dict) -> str:
        """格式化地理设定信息 - 传递完整的地理设定"""
        if not geography_info:
            return "无地理设定"
        
        try:
            import json
            # 直接返回完整的JSON格式地理设定
            return json.dumps(geography_info, ensure_ascii=False, indent=2)
        except Exception as e:
            debug_log("地理设定格式化失败", e)
            # 如果JSON序列化失败，返回字符串表示
            return str(geography_info)
