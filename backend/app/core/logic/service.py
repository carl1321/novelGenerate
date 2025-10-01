"""
叙事逻辑与反思引擎服务
"""
from typing import Dict, List, Any, Optional
import asyncio
from openai import AsyncAzureOpenAI

from app.core.config import settings
from app.utils import llm_client
from app.utils.prompt_manager import prompt_manager


class LogicReflectionService:
    """叙事逻辑与反思引擎服务类"""
    
    def __init__(self):
        pass
    
    async def check_logic_consistency(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """检查逻辑一致性"""
        try:
            prompt = prompt_manager.build_prompt(
                "logic_check",
                content=content
            )
            
            response = await self.client.chat.completions.create(
                model=settings.AZURE_OPENAI_DEPLOYMENT_NAME,
                messages=[
                    {"role": "system", "content": prompt_manager.get_logic_check_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=20000
            )
            
            result = response
            return {"status": "success", "analysis": result}
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def generate_reflection_report(self, content: Dict[str, Any]) -> Dict[str, Any]:
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
            
            response = await self.client.chat.completions.create(
                model=settings.AZURE_OPENAI_DEPLOYMENT_NAME,
                messages=[
                    {"role": "system", "content": "你是一个专业的编辑，擅长分析小说内容并提供改进建议。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=20000
            )
            
            result = response
            return {"status": "success", "report": result}
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
