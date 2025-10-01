"""
事件生成器
"""
import json
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.utils import llm_client
from app.core.event_generator.event_models import Event, EventType, EventImportance, EventCategory
from app.utils.prompt_manager import PromptManager


class EventGenerator:
    """事件生成器"""
    
    def __init__(self):
        self.prompt_manager = PromptManager()
    
    async def generate_event(self, 
                           world_view: Dict[str, Any],
                           characters: List[Dict[str, Any]],
                           event_requirements: List[str],
                           event_type: EventType = EventType.DAILY) -> Event:
        """生成单个事件"""
        try:
            # 构建prompt
            prompt = self._build_event_prompt(
                world_view, characters, event_requirements, event_type
            )
            
            # 调用LLM
            content = await llm_client.generate_chat(
                messages=[
                    {"role": "system", "content": "你是一个专业的小说事件设计师，擅长创造引人入胜的事件。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=20000
            )
            
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
                event_type=EventType(event_data.get("event_type", "日常事件")),
                importance=EventImportance(event_data.get("importance", "中")),
                category=EventCategory(event_data.get("category", "剧情推动")),
                setting=event_data.get("setting", ""),
                participants=event_data.get("participants", []),
                duration=event_data.get("duration", ""),
                outcome=event_data.get("outcome", ""),
                plot_impact=event_data.get("plot_impact", ""),
                character_impact=event_data.get("character_impact", {}),
                foreshadowing_elements=event_data.get("foreshadowing_elements", []),
                prerequisites=event_data.get("prerequisites", []),
                consequences=event_data.get("consequences", []),
                tags=event_data.get("tags", []),
                sequence_order=event_data.get("sequence_order", 0)
            )
            
            return event
            
        except Exception as e:
            print(f"生成事件失败: {e}")
            raise
    
    async def generate_event_sequence(self,
                                    world_view: Dict[str, Any],
                                    characters: List[Dict[str, Any]],
                                    plot_outline: Dict[str, Any],
                                    event_count: int = 10) -> List[Event]:
        """生成事件序列"""
        events = []
        
        # 根据剧情大纲生成不同类型的事件
        event_types = [
            EventType.DAILY,
            EventType.CONFLICT,
            EventType.TURNING_POINT,
            EventType.CULTIVATION,
            EventType.SOCIAL,
            EventType.DANGER,
            EventType.DISCOVERY,
            EventType.ROMANCE,
            EventType.MYSTERY,
            EventType.BATTLE
        ]
        
        for i in range(event_count):
            event_type = event_types[i % len(event_types)]
            
            requirements = [
                f"请生成一个{event_type.value}",
                f"这是第{i+1}个事件，请确保与剧情大纲协调",
                "事件要有明确的参与角色和结果",
                "考虑事件对角色成长的影响"
            ]
            
            event = await self.generate_event(
                world_view=world_view,
                characters=characters,
                event_requirements=requirements,
                event_type=event_type
            )
            
            event.sequence_order = i + 1
            events.append(event)
        
        return events
    
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
            formatted.append(f"- {char.get('name', '未知角色')}: {char.get('background', '无背景信息')}")
        
        return "\n".join(formatted)
