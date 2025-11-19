"""
叙事逻辑与反思引擎服务
"""
from typing import Dict, List, Any, Optional
import asyncio

from app.utils.llm_client import get_llm_client
from app.utils.prompt_manager import PromptManager
from app.core.logic.engine import LogicCheckEngine
from app.core.logic.models import LogicCheckResult, LogicStatus


class LogicReflectionService:
    """叙事逻辑与反思引擎服务类"""
    
    def __init__(self):
        self.llm_client = get_llm_client()
        self.prompt_manager = PromptManager()
        self.logic_engine = LogicCheckEngine()
    
    async def check_logic_consistency(self, content: str) -> Dict[str, Any]:
        """检查逻辑一致性（兼容旧接口）"""
        try:
            result = await self.logic_engine.check_logic(content)
            return {
                "status": "success", 
                "analysis": result.summary,
                "logic_result": result.dict()
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def check_logic_detailed(self, content: str, checked_by: str = "system") -> LogicCheckResult:
        """详细逻辑检查（新接口）"""
        return await self.logic_engine.check_logic(content, checked_by)
    
    async def generate_reflection_report(self, content: str) -> Dict[str, Any]:
        """生成反思报告"""
        try:
            prompt = f"""
请为以下内容生成详细的反思报告：

内容：{content}

请包含：
1. 逻辑问题分析
2. 角色一致性检查
3. 情节合理性评估
4. 改进建议
5. 风险提示

请以JSON格式返回报告。
"""
            
            response = await self.llm_client.generate_text(
                prompt=prompt,
                temperature=0.3,
                max_tokens=20000
            )
            
            return {"status": "success", "report": response}
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
