"""
多维度评分服务
"""
from typing import Dict, List, Any, Optional
import asyncio
from openai import AsyncAzureOpenAI

from app.core.config import settings
from app.utils import llm_client
from app.utils.prompt_manager import prompt_manager


class ScoringService:
    """多维度评分服务类"""
    
    def __init__(self):
        pass
        self.weights = settings.SCORING_WEIGHTS
    
    async def score_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """对内容进行多维度评分"""
        try:
            # 逻辑自洽性评分
            logic_score = await self._score_logic_consistency(content)
            
            # 戏剧冲突性评分
            conflict_score = await self._score_dramatic_conflict(content)
            
            # 角色一致性评分
            character_score = await self._score_character_consistency(content)
            
            # 文笔流畅度评分
            writing_score = await self._score_writing_quality(content)
            
            # 创新性评分
            innovation_score = await self._score_innovation(content)
            
            # 计算加权总分
            total_score = (
                logic_score * self.weights["logic_consistency"] +
                conflict_score * self.weights["dramatic_conflict"] +
                character_score * self.weights["character_consistency"] +
                writing_score * self.weights["writing_quality"] +
                innovation_score * self.weights["innovation"]
            )
            
            return {
                "total_score": total_score,
                "scores": {
                    "logic_consistency": logic_score,
                    "dramatic_conflict": conflict_score,
                    "character_consistency": character_score,
                    "writing_quality": writing_score,
                    "innovation": innovation_score
                },
                "weights": self.weights
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    async def _score_logic_consistency(self, content: Dict[str, Any]) -> float:
        """评分逻辑自洽性"""
        try:
            prompt = prompt_manager.build_prompt(
                "scoring_criteria",
                content=content,
                dimension="逻辑自洽性"
            )
            
            response = await self.client.chat.completions.create(
                model=settings.AZURE_OPENAI_DEPLOYMENT_NAME,
                messages=[
                    {"role": "system", "content": prompt_manager.get_scoring_criteria_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=20000
            )
            
            score = float(response.strip())
            return max(1, min(10, score))
            
        except Exception as e:
            return 5.0  # 默认分数
    
    async def _score_dramatic_conflict(self, content: Dict[str, Any]) -> float:
        """评分戏剧冲突性"""
        try:
            prompt = f"""
请对以下内容的戏剧冲突性进行评分（1-10分）：

内容：{content}

评分标准：
- 10分：冲突激烈，张力十足
- 8-9分：冲突明显，有张力
- 6-7分：冲突一般
- 4-5分：冲突较弱
- 1-3分：缺乏冲突

请只返回数字分数。
"""
            
            response = await self.client.chat.completions.create(
                model=settings.AZURE_OPENAI_DEPLOYMENT_NAME,
                messages=[
                    {"role": "system", "content": "你是一个专业的戏剧冲突评分员。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=20000
            )
            
            score = float(response.strip())
            return max(1, min(10, score))
            
        except Exception as e:
            return 5.0
    
    async def _score_character_consistency(self, content: Dict[str, Any]) -> float:
        """评分角色一致性"""
        try:
            prompt = f"""
请对以下内容的角色一致性进行评分（1-10分）：

内容：{content}

评分标准：
- 10分：角色行为完全一致
- 8-9分：角色行为基本一致
- 6-7分：角色行为有轻微不一致
- 4-5分：角色行为不一致较多
- 1-3分：角色行为混乱

请只返回数字分数。
"""
            
            response = await self.client.chat.completions.create(
                model=settings.AZURE_OPENAI_DEPLOYMENT_NAME,
                messages=[
                    {"role": "system", "content": "你是一个专业的角色一致性评分员。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=20000
            )
            
            score = float(response.strip())
            return max(1, min(10, score))
            
        except Exception as e:
            return 5.0
    
    async def _score_writing_quality(self, content: Dict[str, Any]) -> float:
        """评分文笔流畅度"""
        try:
            prompt = f"""
请对以下内容的文笔流畅度进行评分（1-10分）：

内容：{content}

评分标准：
- 10分：文笔优美，流畅自然
- 8-9分：文笔较好，基本流畅
- 6-7分：文笔一般，有改进空间
- 4-5分：文笔较差，不够流畅
- 1-3分：文笔混乱，难以理解

请只返回数字分数。
"""
            
            response = await self.client.chat.completions.create(
                model=settings.AZURE_OPENAI_DEPLOYMENT_NAME,
                messages=[
                    {"role": "system", "content": "你是一个专业的文笔评分员。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=20000
            )
            
            score = float(response.strip())
            return max(1, min(10, score))
            
        except Exception as e:
            return 5.0
    
    async def _score_innovation(self, content: Dict[str, Any]) -> float:
        """评分创新性"""
        try:
            prompt = f"""
请对以下内容的创新性进行评分（1-10分）：

内容：{content}

评分标准：
- 10分：极具创新，突破常规
- 8-9分：有创新，有特色
- 6-7分：创新一般
- 4-5分：创新较少
- 1-3分：缺乏创新，俗套

请只返回数字分数。
"""
            
            response = await self.client.chat.completions.create(
                model=settings.AZURE_OPENAI_DEPLOYMENT_NAME,
                messages=[
                    {"role": "system", "content": "你是一个专业的创新性评分员。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=20000
            )
            
            score = float(response.strip())
            return max(1, min(10, score))
            
        except Exception as e:
            return 5.0
