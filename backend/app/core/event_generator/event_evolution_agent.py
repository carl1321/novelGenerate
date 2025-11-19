"""
事件进化智能体
负责根据评分结果优化事件，修复识别出的问题，提升事件质量
"""

from typing import Dict, List, Any, Optional
from app.utils.llm_client import get_llm_client
from app.utils.prompt_manager import PromptManager
from app.core.event_generator.event_models import Event


class EventEvolutionAgent:
    """事件进化智能体"""
    
    def __init__(self, llm_client):
        self.llm_client = llm_client
        self.prompt_manager = PromptManager()
        self._event_database = None
        self._character_database = None
        self._worldview_database = None
        self._plot_database = None
    
    @property
    def event_database(self):
        if self._event_database is None:
            from app.core.event_generator.event_database import EventDatabase
            self._event_database = EventDatabase()
        return self._event_database
    
    @property
    def character_database(self):
        if self._character_database is None:
            from app.core.character.database import CharacterDatabase
            self._character_database = CharacterDatabase()
        return self._character_database
    
    @property
    def worldview_database(self):
        if self._worldview_database is None:
            from app.core.world.database import WorldViewDatabase
            self._worldview_database = WorldViewDatabase()
        return self._worldview_database
    
    @property
    def plot_database(self):
        if self._plot_database is None:
            from app.core.plot_engine.plot_database import PlotOutlineDatabase
            self._plot_database = PlotOutlineDatabase()
        return self._plot_database
    
    async def evolve_event(self, event_id: str, score_id: int, custom_description: str = "") -> Event:
        """根据评分结果进化事件（使用版本管理）"""
        try:
            print(f"🔄 开始进化事件 {event_id}，基于评分 {score_id}...")
            
            # 1. 获取原始事件和评分
            event = self.event_database.get_event(event_id)
            if not event:
                raise ValueError(f"事件 {event_id} 不存在")
            
            score = self.event_database.get_event_score_by_id(score_id)
            if not score:
                raise ValueError(f"评分 {score_id} 不存在")
            
            # 2. 获取相关角色和世界观信息
            characters = self.character_database.get_characters_by_worldview(
                event.plot_outline_id
            )
            world_info = self.worldview_database.get_worldview(
                event.plot_outline_id
            )
            
            print(f"📊 获取到 {len(characters)} 个角色信息")
            
            # 3. 生成进化prompt
            prompt = self.prompt_manager.get_event_evolution_prompt(
                event, score, characters, world_info, custom_description
            )
            
            # 4. 调用LLM进行进化
            print("🤖 调用LLM进行事件进化...")
            response = await self.llm_client.generate_text(prompt)
            
            # 5. 解析进化结果
            evolved_event_data = self._parse_evolution_response(response, event)
            
            # 6. 使用版本管理创建新版本
            print(f"💾 创建事件新版本...")
            
            # 处理event_type
            event_type_str = str(evolved_event_data.event_type)
            if hasattr(evolved_event_data.event_type, 'value'):
                event_type_str = evolved_event_data.event_type.value
            
            print(f"📊 创建版本参数:")
            print(f"  - event_id: {event_id}")
            print(f"  - title: {evolved_event_data.title}")
            print(f"  - event_type: {event_type_str}")
            print(f"  - description长度: {len(evolved_event_data.description)}")
            print(f"  - outcome长度: {len(evolved_event_data.outcome)}")
            
            new_evolution_id = self.event_database.create_event_version(
                event_id,  # 使用相同的事件ID
                evolved_event_data.title,
                event_type_str,
                evolved_event_data.description,
                evolved_event_data.outcome,
                f"基于评分 {score_id} 的进化优化",  # 进化原因
                score_id  # 评分ID
            )
            
            if not new_evolution_id:
                raise ValueError("创建事件进化版本失败")
            
            # 7. 获取新创建的事件对象（最新版本）
            evolved_event = self.event_database.get_latest_event_version(event_id)
            if not evolved_event:
                raise ValueError(f"获取新创建的事件失败: {event_id}")
            
            # 8. 保存进化历史（记录评分关联）
            self.event_database.save_evolution_history(
                event_id, event_id, score_id  # 使用相同的事件ID
            )
            
            print(f"✅ 事件进化完成，新进化版本ID: {new_evolution_id}")
            return evolved_event
            
        except Exception as e:
            print(f"❌ 事件进化失败: {e}")
            raise
    
    def _parse_evolution_response(self, response: str, original_event: Event) -> Event:
        """解析进化响应"""
        import json
        import re
        import uuid
        from datetime import datetime
        
        try:
            # 尝试直接解析JSON
            if response.strip().startswith('{'):
                data = json.loads(response)
            else:
                # 如果响应不是纯JSON，尝试提取JSON部分
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    json_str = json_match.group()
                    data = json.loads(json_str)
                else:
                    raise ValueError("无法找到JSON格式的响应")
            
            # 创建新事件对象，保持与原始事件完全相同的格式
            evolved_event = Event(
                id=f"event_{uuid.uuid4().hex[:8]}",
                plot_outline_id=original_event.plot_outline_id,
                chapter_number=original_event.chapter_number,
                sequence_order=original_event.sequence_order,
                title=data.get('title', original_event.title),
                event_type=data.get('event_type', original_event.event_type),
                description=data.get('description', original_event.description),
                outcome=data.get('outcome', original_event.outcome),
                setting=original_event.setting,  # 保持原始设置
                participants=original_event.participants,  # 保持原始参与者
                duration=original_event.duration,  # 保持原始持续时间
                plot_impact=original_event.plot_impact,  # 保持原始剧情影响
                foreshadowing_elements=original_event.foreshadowing_elements,  # 保持原始伏笔
                dramatic_tension=original_event.dramatic_tension,  # 保持原始戏剧张力
                emotional_impact=original_event.emotional_impact,  # 保持原始情感冲击
                story_position=original_event.story_position,  # 保持原始故事位置
                character_impact=original_event.character_impact,  # 保持原始角色影响
                conflict_core=original_event.conflict_core,  # 保持原始冲突核心
                logical_consistency=original_event.logical_consistency,  # 保持原始逻辑一致性
                realistic_elements=original_event.realistic_elements,  # 保持原始现实元素
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            return evolved_event
            
        except Exception as e:
            print(f"❌ 解析进化响应失败: {e}")
            # 如果解析失败，返回原始事件的副本
            evolved_event = Event(
                id=f"event_{uuid.uuid4().hex[:8]}",
                plot_outline_id=original_event.plot_outline_id,
                chapter_number=original_event.chapter_number,
                sequence_order=original_event.sequence_order,
                title=f"{original_event.title} (进化失败)",
                event_type=original_event.event_type,
                description=original_event.description,
                outcome=f"{original_event.outcome}\n\n[进化失败: {str(e)}]",
                setting=original_event.setting,
                participants=original_event.participants,
                duration=original_event.duration,
                plot_impact=original_event.plot_impact,
                foreshadowing_elements=original_event.foreshadowing_elements,
                dramatic_tension=original_event.dramatic_tension,
                emotional_impact=original_event.emotional_impact,
                story_position=original_event.story_position,
                character_impact=original_event.character_impact,
                conflict_core=original_event.conflict_core,
                logical_consistency=original_event.logical_consistency,
                realistic_elements=original_event.realistic_elements,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            return evolved_event
    
    def get_evolution_history(self, event_id: str) -> List[Dict[str, Any]]:
        """获取事件的进化历史"""
        try:
            history = self.event_database.get_evolution_history(event_id)
            return history
        except Exception as e:
            print(f"❌ 获取进化历史失败: {e}")
            return []
    
    def accept_evolution(self, original_event_id: str, evolved_event_id: str) -> bool:
        """接受进化结果，将进化后的事件替换原始事件"""
        try:
            print(f"✅ 接受进化结果: {original_event_id} -> {evolved_event_id}")
            
            # 获取进化后的事件
            evolved_event = self.event_database.get_event(evolved_event_id)
            if not evolved_event:
                raise ValueError(f"进化后的事件 {evolved_event_id} 不存在")
            
            # 更新原始事件
            success = self.event_database.update_event(original_event_id, evolved_event)
            
            if success:
                print(f"✅ 事件更新成功")
                return True
            else:
                print(f"❌ 事件更新失败")
                return False
                
        except Exception as e:
            print(f"❌ 接受进化结果失败: {e}")
            return False
    
    def reject_evolution(self, evolved_event_id: str) -> bool:
        """拒绝进化结果，删除进化后的事件"""
        try:
            print(f"❌ 拒绝进化结果: {evolved_event_id}")
            
            success = self.event_database.delete_event(evolved_event_id)
            
            if success:
                print(f"✅ 进化后的事件已删除")
                return True
            else:
                print(f"❌ 删除进化后的事件失败")
                return False
                
        except Exception as e:
            print(f"❌ 拒绝进化结果失败: {e}")
            return False
