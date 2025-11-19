"""
事件评分智能体
负责对生成的事件进行多维度评分，识别优缺点并提供改进建议
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from app.utils.llm_client import get_llm_client
from app.utils.prompt_manager import PromptManager


@dataclass
class EventScore:
    """事件评分结果"""
    protagonist_involvement: float  # 主角参与度 (0-10)
    plot_coherence: float          # 剧情逻辑性 (0-10)
    writing_quality: float         # 文笔质量 (0-10)
    dramatic_tension: float        # 戏剧张力 (0-10)
    overall_quality: float         # 综合质量 (0-10)
    feedback: str                  # 改进建议
    strengths: List[str]           # 优点
    weaknesses: List[str]          # 缺点


class EventScoringAgent:
    """事件评分智能体"""
    
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
    
    async def score_event(self, event_or_id) -> EventScore:
        """对指定事件进行评分，支持传入事件对象或事件ID"""
        try:
            # 判断传入的是事件对象还是事件ID
            if isinstance(event_or_id, str):
                # 传入的是事件ID
                event_id = event_or_id
                print(f"🎯 开始对事件 {event_id} 进行评分...")
                
                # 1. 获取事件信息
                event = self.event_database.get_event(event_id)
                if not event:
                    raise ValueError(f"事件 {event_id} 不存在")
            else:
                # 传入的是事件对象
                event = event_or_id
                print(f"🎯 开始对事件对象 {event.title} 进行评分...")
            
            # 2. 获取相关角色和世界观信息
            characters = self.character_database.get_characters_by_worldview(
                event.plot_outline_id
            )
            world_info = self.worldview_database.get_worldview(
                event.plot_outline_id
            )
            plot_info = self.plot_database.get_plot_outline(
                event.plot_outline_id
            )
            
            print(f"📊 获取到 {len(characters)} 个角色信息")
            print(f"📊 世界观信息类型: {type(world_info)}")
            print(f"📊 剧情信息类型: {type(plot_info)}")
            
            # 3. 生成评分prompt
            try:
                prompt = self.prompt_manager.get_event_scoring_prompt(
                    event, characters, world_info, plot_info
                )
                print(f"📝 评分prompt生成成功，长度: {len(prompt)}")
            except Exception as e:
                print(f"❌ 生成评分prompt失败: {e}")
                raise
            
            # 4. 调用LLM进行评分
            print("🤖 调用LLM进行事件评分...")
            try:
                response = await self.llm_client.generate_text(prompt)
                print(f"🤖 LLM响应长度: {len(response)}")
            except Exception as e:
                print(f"❌ LLM调用失败: {e}")
                raise
            
            # 5. 解析评分结果
            try:
                score_data = self._parse_score_response(response)
                print(f"📊 评分数据解析成功: {score_data}")
            except Exception as e:
                print(f"❌ 解析评分结果失败: {e}")
                raise
            
            # 6. 保存评分结果
            score = EventScore(**score_data)
            self.event_database.save_event_score(event.id, score)
            
            print(f"✅ 事件评分完成，综合质量: {score.overall_quality}/10")
            return score
            
        except Exception as e:
            print(f"❌ 事件评分失败: {e}")
            raise
    
    def _parse_score_response(self, response: str) -> Dict[str, Any]:
        """解析评分响应"""
        import json
        import re
        
        try:
            # 尝试直接解析JSON
            if response.strip().startswith('{'):
                return json.loads(response)
            
            # 如果响应不是纯JSON，尝试提取JSON部分
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                return json.loads(json_str)
            
            # 如果无法解析JSON，返回默认评分
            print("⚠️ 无法解析评分响应，使用默认评分")
            return {
                "protagonist_involvement": 5.0,
                "plot_coherence": 5.0,
                "writing_quality": 5.0,
                "dramatic_tension": 5.0,
                "overall_quality": 5.0,
                "feedback": "评分解析失败，请重新评分",
                "strengths": ["无法解析"],
                "weaknesses": ["评分解析失败"]
            }
            
        except Exception as e:
            print(f"❌ 解析评分响应失败: {e}")
            return {
                "protagonist_involvement": 5.0,
                "plot_coherence": 5.0,
                "writing_quality": 5.0,
                "dramatic_tension": 5.0,
                "overall_quality": 5.0,
                "feedback": f"评分解析失败: {str(e)}",
                "strengths": ["解析失败"],
                "weaknesses": [f"解析错误: {str(e)}"]
            }
    
    def get_event_scores(self, event_id: str) -> List[EventScore]:
        """获取事件的评分历史"""
        try:
            scores = self.event_database.get_event_scores(event_id)
            # 转换旧格式的评分为新格式
            converted_scores = []
            for score in scores:
                if hasattr(score, 'character_development'):
                    # 旧格式，需要转换
                    converted_score = EventScore(
                        protagonist_involvement=getattr(score, 'protagonist_involvement', 5.0),
                        plot_coherence=getattr(score, 'plot_coherence', 5.0),
                        writing_quality=getattr(score, 'emotional_impact', 5.0),  # 用情感冲击代替文笔质量
                        dramatic_tension=getattr(score, 'dramatic_tension', 5.0),
                        overall_quality=getattr(score, 'overall_quality', 5.0),
                        feedback=getattr(score, 'feedback', '旧格式评分'),
                        strengths=getattr(score, 'strengths', []),
                        weaknesses=getattr(score, 'weaknesses', [])
                    )
                    converted_scores.append(converted_score)
                else:
                    # 新格式，直接使用
                    converted_scores.append(score)
            return converted_scores
        except Exception as e:
            print(f"❌ 获取评分历史失败: {e}")
            return []
    
    def get_latest_score_with_id(self, event_id: str) -> Optional[dict]:
        """获取事件的最新评分（包含ID）"""
        try:
            return self.event_database.get_latest_event_score_with_id(event_id)
        except Exception as e:
            print(f"❌ 获取最新评分失败: {e}")
            return None
