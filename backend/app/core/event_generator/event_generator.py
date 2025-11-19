"""
事件生成器
"""
import json
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.utils import llm_client
from app.core.event_generator.event_models import Event, EventType, EventImportance, EventCategory, SimpleEvent
from app.core.event_generator.event_database import EventDatabase
from app.utils.prompt_manager import PromptManager


class EventGenerator:
    """事件生成器"""
    
    def __init__(self):
        self.prompt_manager = PromptManager()
        self.event_database = EventDatabase()
    
    async def generate_event(self, 
                           world_view: Dict[str, Any],
                           characters: List[Dict[str, Any]],
                           event_requirements: List[str],
                           event_type: EventType = "日常事件") -> Event:
        """生成单个事件"""
        try:
            # 构建prompt
            prompt = self._build_event_prompt(
                world_view, characters, event_requirements, event_type
            )
            
            # 调用LLM
            print(f"🤖 开始调用LLM生成事件...")
            print(f"📤 发送给LLM的prompt长度: {len(prompt)} 字符")
            
            content = await llm_client.generate_chat(
                messages=[
                    {"role": "system", "content": "你是一个专业的小说事件设计师，擅长创造引人入胜的事件。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=20000
            )
            
            print(f"📥 LLM响应长度: {len(content)} 字符")
            print(f"📥 LLM响应内容: {content[:500]}...")
            
            # 解析JSON
            try:
                event_data = json.loads(content)
            except json.JSONDecodeError as e:
                print(f"事件JSON解析失败: {e}")
                # 尝试提取JSON部分
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    json_str = json_match.group()
                    event_data = json.loads(json_str)
                else:
                    raise ValueError(f"无法从LLM响应中提取有效的JSON: {content[:100]}...")
            
            # 创建Event对象
            event = Event(
                id=f"event_{uuid.uuid4().hex[:8]}",
                title=event_data.get("title", "未命名事件"),
                description=event_data.get("description", ""),
                event_type=event_data.get("event_type", "日常事件"),
                setting=event_data.get("setting", ""),
                participants=event_data.get("participants", []),
                duration=event_data.get("duration", ""),
                outcome=event_data.get("outcome", ""),
                plot_impact=event_data.get("plot_impact", ""),
                character_impact=event_data.get("character_impact", {}),
                foreshadowing_elements=event_data.get("foreshadowing_elements", []),
                conflict_core=event_data.get("conflict_core", ""),
                dramatic_tension=event_data.get("dramatic_tension", 5),
                emotional_impact=event_data.get("emotional_impact", 5),
                logical_consistency=event_data.get("logical_consistency", ""),
                realistic_elements=event_data.get("realistic_elements", ""),
                sequence_order=event_data.get("sequence_order", 0)
            )
            
            return event
            
        except Exception as e:
            print(f"生成事件失败: {e}")
            raise
    
    async def generate_enhanced_events(self,
                                     plot_outline: Dict[str, Any],
                                     world_view: Dict[str, Any],
                                     characters: List[Dict[str, Any]],
                                     importance_distribution: Dict[str, int],
                                     event_requirements: str = "",
                                     generate_chapter_integration: bool = True,
                                     selected_act: Optional[Dict[str, Any]] = None,
                                     story_tone: str = "",
                                     narrative_structure: str = "",
                                     save_to_database: bool = True) -> List[Event]:
        """生成增强事件（支持重要性分级和章节关联）"""
        try:
            # 计算总事件数
            total_events = sum(importance_distribution.values())
            
            # 构建增强prompt
            prompt = self._build_enhanced_event_prompt(
                world_view, characters, plot_outline, importance_distribution, 
                event_requirements, generate_chapter_integration, selected_act,
                story_tone, narrative_structure
            )
            
            # 调用LLM
            content = await llm_client.generate_chat(
                messages=[
                    {"role": "system", "content": "你是一个专业的小说事件设计师，擅长创造引人入胜的事件序列，支持重要性分级和章节关联。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=20000
            )
            
            # 解析JSON
            try:
                batch_data = json.loads(content)
            except json.JSONDecodeError as e:
                print(f"增强事件JSON解析失败: {e}")
                print(f"LLM响应内容: {content[:500]}...")
                # 尝试提取JSON部分
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    json_str = json_match.group()
                    try:
                        batch_data = json.loads(json_str)
                        print("成功从响应中提取JSON")
                    except json.JSONDecodeError as e2:
                        print(f"提取的JSON仍然无效: {e2}")
                        print(f"提取的JSON内容: {json_str[:200]}...")
                        raise ValueError(f"无法从LLM响应中提取有效的JSON: {content[:100]}...")
                else:
                    raise ValueError(f"无法从LLM响应中提取有效的JSON: {content[:100]}...")
            
            events_data = batch_data.get("events", [])
            
            if len(events_data) == 0:
                return []
            
            events = []
            plot_outline_id = plot_outline.get('id', '') if isinstance(plot_outline, dict) else getattr(plot_outline, 'id', '')
            
            # 获取下一个可用的序号
            next_sequence_order = self.event_database.get_next_sequence_order(plot_outline_id)
            
            for i, event_data in enumerate(events_data):
                try:
                    # 安全地获取事件类型和重要性
                    event_type_str = event_data.get("event_type", "日常事件")
                    importance_str = event_data.get("importance", "中")
                    
                    # 直接使用字符串，不再进行枚举转换
                    event_type = event_type_str
                    
                    event = Event(
                        id=f"event_{uuid.uuid4().hex[:8]}",
                        title=event_data.get("title", f"未命名事件{i+1}"),
                        event_type=event_type,
                        description=event_data.get("description", ""),
                        outcome=event_data.get("outcome", ""),
                        setting=event_data.get("setting", ""),
                        participants=event_data.get("participants", []),
                        duration=event_data.get("duration", ""),
                        plot_impact=event_data.get("plot_impact", ""),
                        foreshadowing_elements=event_data.get("foreshadowing_elements", []),
                        dramatic_tension=event_data.get("dramatic_tension", 5),
                        emotional_impact=event_data.get("emotional_impact", 5),
                        sequence_order=next_sequence_order + i,  # 使用连续的序号
                        # 兼容字段
                        character_impact=event_data.get("character_impact", {}),
                        conflict_core=event_data.get("conflict_core", ""),
                        logical_consistency=event_data.get("logical_consistency", ""),
                        realistic_elements=event_data.get("realistic_elements", ""),
                        created_at=datetime.now()
                    )
                    
                    # 添加增强字段
                    if generate_chapter_integration:
                        event.story_position = event_data.get("story_position")
                    
                    # 添加剧情大纲ID
                    event.plot_outline_id = plot_outline_id
                    
                    # 保存到数据库
                    if save_to_database:
                        self.event_database.save_event(event)
                    
                    events.append(event)
                except Exception as e:
                    continue
            
            return events
            
        except Exception as e:
            print(f"生成增强事件失败: {e}")
            raise

    async def generate_simple_events(self,
                                   plot_outline: Dict[str, Any],
                                   world_view: Dict[str, Any],
                                   characters: List[Dict[str, Any]],
                                   importance_distribution: Dict[str, int],
                                   event_requirements: str = "",
                                   selected_act: Optional[Dict[str, Any]] = None,
                                   save_to_database: bool = True) -> List[SimpleEvent]:
        """生成简化事件（仅包含标题、事件类型、描述、事件结果）"""
        try:
            # 计算总事件数
            total_events = sum(importance_distribution.values())
            
            # 构建增强prompt
            prompt = self._build_enhanced_event_prompt(
                world_view, characters, plot_outline, importance_distribution, 
                event_requirements, False, selected_act, "", ""
            )
            
            # 调用LLM
            content = await llm_client.generate_chat(
                messages=[
                    {"role": "system", "content": "你是一个专业的小说事件设计师，擅长创造引人入胜的事件序列。请严格按照JSON格式输出，只包含标题、事件类型、描述、事件结果四个字段。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=20000
            )
            
            # 解析JSON
            try:
                batch_data = json.loads(content)
            except json.JSONDecodeError as e:
                print(f"简化事件JSON解析失败: {e}")
                # 尝试提取JSON部分
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    json_str = json_match.group()
                    try:
                        batch_data = json.loads(json_str)
                        print("成功从响应中提取JSON")
                    except json.JSONDecodeError as e2:
                        print(f"提取的JSON仍然无效: {e2}")
                        raise ValueError(f"无法从LLM响应中提取有效的JSON: {content[:100]}...")
                else:
                    raise ValueError(f"无法从LLM响应中提取有效的JSON: {content[:100]}...")
            
            events_data = batch_data.get("events", [])
            
            if len(events_data) == 0:
                return []
            
            simple_events = []
            
            for i, event_data in enumerate(events_data):
                try:
                    simple_event = SimpleEvent(
                        title=event_data.get("title", f"未命名事件{i+1}"),
                        event_type=event_data.get("event_type", "日常事件"),
                        description=event_data.get("description", ""),
                        outcome=event_data.get("outcome", "")
                    )
                    
                    simple_events.append(simple_event)
                except Exception as e:
                    continue
            
            # 保存到数据库
            if save_to_database and simple_events:
                plot_outline_id = plot_outline.get('id', '') if isinstance(plot_outline, dict) else getattr(plot_outline, 'id', '')
                if plot_outline_id:
                    # 转换为Event对象并保存
                    events = []
                    # 获取下一个可用的序号
                    next_sequence_order = self.event_database.get_next_sequence_order(plot_outline_id)
                    
                    for i, simple_event in enumerate(simple_events):
                        event = Event(
                            id=f"event_{uuid.uuid4().hex[:8]}",
                            title=simple_event.title,
                            event_type=simple_event.event_type,
                            description=simple_event.description,
                            outcome=simple_event.outcome,
                            plot_outline_id=plot_outline_id,
                            sequence_order=next_sequence_order + i  # 使用连续的序号
                        )
                        events.append(event)
                    
                    # 批量保存
                    success_count = 0
                    for event in events:
                        if self.event_database.save_event(event):
                            success_count += 1
                    
                    # 批量保存完成
                    pass
            
            return simple_events
            
        except Exception as e:
            print(f"生成简化事件失败: {e}")
            raise

    def _build_enhanced_event_prompt(self,
                                   world_view: Dict[str, Any],
                                   characters: List[Dict[str, Any]],
                                   plot_outline: Dict[str, Any],
                                   importance_distribution: Dict[str, int],
                                   event_requirements: str,
                                   generate_chapter_integration: bool,
                                   selected_act: Optional[Dict[str, Any]] = None,
                                   story_tone: str = "",
                                   narrative_structure: str = "") -> str:
        """构建增强事件生成prompt（根据事件要求是否为空选择不同的生成策略）"""
        
        # 检查事件要求是否为空
        if event_requirements and event_requirements.strip():
            print(f"🎯 事件要求不为空，使用简化提示词策略")
            print(f"📝 事件要求内容: {event_requirements}")
            
            # 使用简化的事件要求提示词
            return self._build_simple_event_requirements_prompt(
                event_requirements, importance_distribution, characters, world_view, plot_outline
            )
        else:
            print(f"🎯 事件要求为空，使用完整提示词策略")
            
            # 格式化世界观信息
            world_info = self._format_world_view_dict(world_view)
            
            # 格式化剧情大纲信息
            plot_info = self._format_plot_outline_dict(plot_outline)
            
            # 确保world_info和plot_info是字典
            if not isinstance(world_info, dict):
                world_info = {}
            if not isinstance(plot_info, dict):
                plot_info = {}
            
            try:
                print(f"🔍 开始生成事件生成prompt...")
                print(f"📊 传入参数:")
                print(f"  - core_concept: {world_info.get('core_concept', '')}")
                print(f"  - world_description: {world_info.get('description', '')}")
                geography_setting = world_info.get('geography', '')
                if isinstance(geography_setting, str):
                    print(f"  - geography_setting: {geography_setting[:200]}...")
                else:
                    print(f"  - geography_setting: {str(geography_setting)[:200]}...")
                print(f"  - characters: {len(characters)} 个角色")
                print(f"  - story_tone: {story_tone or plot_info.get('story_tone', '')}")
                print(f"  - narrative_structure: {narrative_structure or plot_info.get('narrative_structure', '')}")
                print(f"  - title: {plot_info.get('title', '')}")
                print(f"  - importance_distribution: {importance_distribution}")
                print(f"  - event_requirements: {event_requirements}")
                print(f"  - selected_act: {selected_act}")
                
                result = self.prompt_manager.get_enhanced_event_generation_prompt(
                    core_concept=world_info.get('core_concept', ''),
                    world_description=world_info.get('description', ''),
                    geography_setting=world_info.get('geography', ''),
                    characters=characters,
                    story_tone=story_tone or plot_info.get('story_tone', ''),
                    narrative_structure=narrative_structure or plot_info.get('narrative_structure', ''),
                    title=plot_info.get('title', ''),
                    importance_distribution=importance_distribution,
                    event_requirements=event_requirements,
                    selected_act=selected_act
                )
                
                print(f"📝 生成的完整prompt:")
                print("=" * 80)
                print(result)
                print("=" * 80)
                print(f"📏 prompt长度: {len(result)} 字符")
                
                return result
            except Exception as e:
                raise
    
    def _build_simple_event_requirements_prompt(self,
                                             event_requirements: str,
                                             importance_distribution: Dict[str, int],
                                             characters: List[Dict[str, Any]],
                                             world_view: Dict[str, Any],
                                             plot_outline: Dict[str, Any]) -> str:
        """构建基于事件要求的简化提示词（只传递事件要求和角色信息）"""
        
        # 格式化角色信息
        characters_info = self._format_characters(characters)
        
        # 构建重要性分布文本
        distribution_text = "\n".join([f"- {k}: {v}个" for k, v in importance_distribution.items()])
        
        prompt = f"""你是一位资深的小说事件设计师，专门根据用户的具体要求生成事件。

## 🚨 用户事件要求 🚨
**{event_requirements}**

**⚠️ 重要提醒**: 请严格按照上述用户要求生成事件，这是最重要的生成标准！所有生成的事件都必须符合用户要求！

## 角色信息
{characters_info}

## 生成任务
**重要性分布**: 
{distribution_text}

**重要提醒**: 请严格按照用户要求生成事件，确保每个事件都符合用户的具体需求。

## 生成要求

1. **严格按照用户要求生成事件**：
   - 所有事件都必须符合用户的具体要求
   - 用户要求是最高优先级，必须严格遵守

2. **严格按照重要性分布生成事件数量**：
   - 重大事件: {importance_distribution.get('重大事件', 0)}个
   - 冲突事件: {importance_distribution.get('冲突事件', 0)}个
   - 特殊事件: {importance_distribution.get('特殊事件', 0)}个
   - 日常事件: {importance_distribution.get('日常事件', 0)}个

3. **事件描述必须简洁明了且符合逻辑**：
   - 事件标题要简洁有力，体现事件核心
   - 事件描述要简洁明了，不超过200字
   - 要包含事件的起因、经过、结果，逻辑链条要清晰
   - 简要描述主角与其他角色的关键对话和互动
   - 简要体现环境氛围
   - 简要展现角色的关键心理变化

4. **主角参与度要求**：
   - **重大、冲突、特殊事件**：主角必须作为主人翁，是事件的核心推动者和主要参与者
   - **日常事件**：主角可以参与，但不强制要求主导地位
   - **主角视角**：从主角的视角描述事件，体现主角的感受和反应

## 输出格式
请严格按照以下JSON格式输出，不要添加任何其他文字或解释：
{{
  "events": [
    {{
      "title": "事件标题（简洁有力，体现事件核心）",
      "event_type": "事件类型（重大事件、冲突事件、特殊事件、日常事件）",
      "description": "事件描述（不超过200字，简洁描述事件过程）",
      "outcome": "事件结果（简洁描述：1）对主角的具体影响；2）对剧情发展的作用；3）为后续埋下的伏笔）"
    }}
  ]
}}

**🚫 再次提醒**: 请严格按照用户要求生成事件！用户要求是最高优先级！"""
        
        print(f"🎯 使用简化事件要求提示词策略")
        print(f"📝 事件要求内容: {event_requirements}")
        print(f"📝 生成的简化事件要求prompt:")
        print("=" * 80)
        print(prompt)
        print("=" * 80)
        print(f"📏 prompt长度: {len(prompt)} 字符")
        
        return prompt
    
    def _build_event_prompt(self,
                          world_view: Dict[str, Any],
                          characters: List[Dict[str, Any]],
                          event_requirements: List[str],
                          event_type: EventType) -> str:
        """构建事件生成prompt"""
        return self.prompt_manager.build_prompt(
            "event_generation",
            event_type=event_type.value,
            world_name=world_view.get('name', '未知世界观'),
            world_description=world_view.get('description', ''),
            power_system=world_view.get('power_system', ''),
            characters_info=self._format_characters(characters),
            event_requirements=chr(10).join(f"- {req}" for req in event_requirements)
        )
    
    def _format_characters(self, characters: List[Dict[str, Any]]) -> str:
        """格式化角色信息"""
        if not characters:
            return "无角色信息"
        
        formatted = []
        for char in characters:
            if isinstance(char, dict):
                name = char.get('name', '未知角色')
                background = char.get('background', '无背景信息')
                current_location = char.get('current_location', '未知位置')
                current_region = char.get('current_region', '')
                role_type = char.get('role_type', '未知类型')
                cultivation_level = char.get('cultivation_level', '未知境界')
                
                # 组合地理位置信息
                location_info = self._combine_location_info(current_region, current_location)
                
                # 构建角色信息，包含地理位置
                char_info = f"- {name} ({role_type}, {cultivation_level}): {background}"
                if location_info and location_info != '未知位置':
                    char_info += f" | 当前位置: {location_info}"
                
                formatted.append(char_info)
            else:
                name = getattr(char, 'name', '未知角色')
                background = getattr(char, 'background', '无背景信息')
                current_location = getattr(char, 'current_location', '未知位置')
                current_region = getattr(char, 'current_region', '')
                role_type = getattr(char, 'role_type', '未知类型')
                cultivation_level = getattr(char, 'cultivation_level', '未知境界')
                
                # 组合地理位置信息
                location_info = self._combine_location_info(current_region, current_location)
                
                char_info = f"- {name} ({role_type}, {cultivation_level}): {background}"
                if location_info and location_info != '未知位置':
                    char_info += f" | 当前位置: {location_info}"
                
                formatted.append(char_info)
        
        return "\n".join(formatted)
    
    def _combine_location_info(self, current_region: str, current_location: str) -> str:
        """组合地理位置信息"""
        if current_region and current_location:
            return f"{current_region} - {current_location}"
        elif current_region:
            return current_region
        elif current_location:
            return current_location
        else:
            return "未知位置"
    
    def _format_plot_outline(self, plot_outline) -> str:
        """格式化剧情大纲信息"""
        if not plot_outline:
            return "无剧情大纲信息"
        
        formatted = []
        
        # 处理PlotOutline对象或字典
        if hasattr(plot_outline, 'title'):
            # PlotOutline对象
            formatted.append(f"标题: {plot_outline.title}")
            formatted.append(f"描述: {getattr(plot_outline, 'description', '无描述')}")
            formatted.append(f"核心概念: {getattr(plot_outline, 'core_concept', '无核心概念')}")
            
            # 添加幕次信息
            acts = getattr(plot_outline, 'acts', [])
            if acts:
                formatted.append("幕次结构:")
                for act in acts:
                    if isinstance(act, dict):
                        formatted.append(f"  - {act.get('act_name', '未知幕次')}: {act.get('description', '无描述')}")
                    else:
                        formatted.append(f"  - {getattr(act, 'act_name', '未知幕次')}: {getattr(act, 'description', '无描述')}")
        else:
            # 字典格式
            formatted.append(f"标题: {plot_outline.get('title', '未知标题')}")
            formatted.append(f"描述: {plot_outline.get('description', '无描述')}")
            formatted.append(f"核心概念: {plot_outline.get('core_concept', '无核心概念')}")
            
            # 添加幕次信息
            acts = plot_outline.get('acts', [])
            if acts:
                formatted.append("幕次结构:")
                for act in acts:
                    if isinstance(act, dict):
                        formatted.append(f"  - {act.get('act_name', '未知幕次')}: {act.get('description', '无描述')}")
                    else:
                        act_name = getattr(act, 'act_name', '未知幕次')
                        description = getattr(act, 'description', '无描述')
                        formatted.append(f"  - {act_name}: {description}")
        
        return "\n".join(formatted)
    
    def _format_plot_outline_dict(self, plot_outline) -> Dict[str, Any]:
        """将PlotOutline对象转换为字典"""
        if isinstance(plot_outline, dict):
            return plot_outline
        
        # 处理PlotOutline对象
        return {
            'id': getattr(plot_outline, 'id', ''),
            'title': getattr(plot_outline, 'title', '未知标题'),
            'description': getattr(plot_outline, 'description', '无描述'),
            'core_concept': getattr(plot_outline, 'core_concept', '无核心概念'),
            'story_tone': getattr(plot_outline, 'story_tone', '未知'),
            'narrative_structure': getattr(plot_outline, 'narrative_structure', '未知'),
            'story_structure': getattr(plot_outline, 'story_structure', '未知'),
            'acts': getattr(plot_outline, 'acts', [])
        }
    
    def _format_world_view_dict(self, world_view) -> Dict[str, Any]:
        """将WorldView对象转换为字典"""
        if isinstance(world_view, dict):
            return world_view
        
        # 处理WorldView对象
        return {
            'worldview_id': getattr(world_view, 'worldview_id', ''),
            'name': getattr(world_view, 'name', '未知世界观'),
            'description': getattr(world_view, 'description', '无描述'),
            'core_concept': getattr(world_view, 'core_concept', '无核心概念'),
            'power_system': getattr(world_view, 'power_system', ''),
            'culture': getattr(world_view, 'culture', ''),
            'geography': getattr(world_view, 'geography', ''),
            'history': getattr(world_view, 'history', ''),
            'organizations': getattr(world_view, 'organizations', [])
        }
