"""
进化与重写引擎服务
"""
from typing import Dict, List, Any, Optional
import asyncio
from openai import AsyncAzureOpenAI

from app.core.config import settings
from app.utils import llm_client


class EvolutionService:
    """进化与重写引擎服务类"""
    
    def __init__(self):
        pass
    
    async def analyze_problems(self, content: Dict[str, Any], 
                             scores: Dict[str, Any]) -> Dict[str, Any]:
        """分析内容问题"""
        try:
            prompt = f"""
请分析以下内容的问题：

内容：{content}
评分：{scores}

请识别：
1. 主要问题类型
2. 问题严重程度
3. 问题位置
4. 问题原因
5. 影响范围

请以JSON格式返回分析结果。
"""
            
            response = await self.client.chat.completions.create(
                model=settings.AZURE_OPENAI_DEPLOYMENT_NAME,
                messages=[
                    {"role": "system", "content": "你是一个专业的内容分析师，擅长识别和分析内容问题。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=20000
            )
            
            result = response
            return {"status": "success", "analysis": result}
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def generate_rewrite_suggestions(self, content: Dict[str, Any], 
                                        problems: Dict[str, Any]) -> Dict[str, Any]:
        """生成重写建议"""
        try:
            prompt = f"""
请为以下内容生成重写建议：

内容：{content}
问题分析：{problems}

请提供：
1. 具体修改建议
2. 修改理由
3. 预期效果
4. 修改优先级
5. 替代方案

请以JSON格式返回建议。
"""
            
            response = await self.client.chat.completions.create(
                model=settings.AZURE_OPENAI_DEPLOYMENT_NAME,
                messages=[
                    {"role": "system", "content": "你是一个专业的编辑，擅长提供内容重写建议。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=20000
            )
            
            result = response
            return {"status": "success", "suggestions": result}
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def generate_ab_test_versions(self, content: Dict[str, Any], 
                                      suggestions: Dict[str, Any]) -> Dict[str, Any]:
        """生成A/B测试版本"""
        try:
            prompt = f"""
请为以下内容生成A/B测试版本：

原内容：{content}
重写建议：{suggestions}

请生成：
1. 版本A：保守修改
2. 版本B：激进修改
3. 版本C：创新修改

每个版本请包含：
- 修改说明
- 预期效果
- 风险评估

请以JSON格式返回版本。
"""
            
            response = await self.client.chat.completions.create(
                model=settings.AZURE_OPENAI_DEPLOYMENT_NAME,
                messages=[
                    {"role": "system", "content": "你是一个专业的A/B测试设计师，擅长创建不同版本的内容。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=20000
            )
            
            result = response
            return {"status": "success", "versions": result}
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def optimize_content(self, content: Dict[str, Any], 
                             target_scores: Dict[str, Any]) -> Dict[str, Any]:
        """优化内容"""
        try:
            prompt = f"""
请优化以下内容以达到目标评分：

内容：{content}
目标评分：{target_scores}

请进行：
1. 内容优化
2. 结构调整
3. 语言润色
4. 逻辑完善
5. 创新提升

请以JSON格式返回优化后的内容。
"""
            
            response = await self.client.chat.completions.create(
                model=settings.AZURE_OPENAI_DEPLOYMENT_NAME,
                messages=[
                    {"role": "system", "content": "你是一个专业的内容优化师，擅长提升内容质量。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=20000
            )
            
            result = response
            return {"status": "success", "optimized_content": result}
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
