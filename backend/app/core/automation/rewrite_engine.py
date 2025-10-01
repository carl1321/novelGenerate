"""
自动重写引擎
"""
from typing import Dict, Any, List, Optional
import asyncio
from openai import AsyncAzureOpenAI

from app.core.config import settings
from app.utils import llm_client
from app.core.world.service import WorldService
from app.core.character.service import CharacterService
from app.core.plot.llm_generator import PlotLLMGenerator
from app.core.automation.decision_engine import RewriteStrategy, DecisionResult
from app.utils.prompt_manager import prompt_manager


class AutoRewriteEngine:
    """自动重写引擎"""
    
    def __init__(self):
        pass
        
        self.world_service = WorldService()
        self.character_service = CharacterService()
        self.plot_generator = PlotLLMGenerator()
    
    async def rewrite_content(self, content: Dict[str, Any], 
                            decision: DecisionResult) -> Dict[str, Any]:
        """根据决策结果重写内容"""
        rewritten_content = content.copy()
        
        try:
            if decision.strategy == RewriteStrategy.LOGIC_FIX:
                rewritten_content = await self._rewrite_logic_fix(rewritten_content, decision)
            elif decision.strategy == RewriteStrategy.CONFLICT_ENHANCEMENT:
                rewritten_content = await self._rewrite_conflict_enhancement(rewritten_content, decision)
            elif decision.strategy == RewriteStrategy.CHARACTER_DEVELOPMENT:
                rewritten_content = await self._rewrite_character_development(rewritten_content, decision)
            elif decision.strategy == RewriteStrategy.PLOT_REFINEMENT:
                rewritten_content = await self._rewrite_plot_refinement(rewritten_content, decision)
            elif decision.strategy == RewriteStrategy.MINOR_ADJUSTMENT:
                rewritten_content = await self._rewrite_minor_adjustment(rewritten_content, decision)
            elif decision.strategy == RewriteStrategy.MAJOR_REWRITE:
                rewritten_content = await self._rewrite_major_rewrite(rewritten_content, decision)
            
            return rewritten_content
            
        except Exception as e:
            print(f"重写过程中出现错误: {e}")
            return content
    
    async def _rewrite_logic_fix(self, content: Dict[str, Any], 
                                decision: DecisionResult) -> Dict[str, Any]:
        """逻辑修复重写"""
        print("🔧 执行逻辑修复重写...")
        
        # 重写世界观
        if 'world' in decision.target_modules and 'world_view' in content:
            world_view = content['world_view']
            logic_prompt = prompt_manager.build_prompt(
                "logic_check",
                content=world_view
            )
            
            # 生成逻辑修复建议
            fix_suggestions = await self._get_rewrite_suggestions(
                "logic_fix", world_view, logic_prompt
            )
            
            # 应用修复建议
            if fix_suggestions:
                world_view = await self._apply_fixes(world_view, fix_suggestions)
                content['world_view'] = world_view
        
        # 重写角色
        if 'character' in decision.target_modules and 'characters' in content:
            characters = content['characters']
            for i, character in enumerate(characters):
                char_prompt = prompt_manager.build_prompt(
                    "character_generation",
                    world_view=content.get('world_view', {}),
                    core_concept="逻辑修复",
                    character_type="现有角色",
                    requirements="请修复角色设定中的逻辑问题，确保角色行为符合世界观设定"
                )
                
                fix_suggestions = await self._get_rewrite_suggestions(
                    "character_logic_fix", character, char_prompt
                )
                
                if fix_suggestions:
                    characters[i] = await self._apply_fixes(character, fix_suggestions)
        
        # 重写剧情
        if 'plot' in decision.target_modules and 'plot' in content:
            plot = content['plot']
            plot_prompt = prompt_manager.build_prompt(
                "plot_generation",
                world_view=content.get('world_view', {}),
                characters=content.get('characters', []),
                core_concept="逻辑修复",
                requirements="请修复剧情中的逻辑问题，确保剧情发展符合世界观和角色设定"
            )
            
            fix_suggestions = await self._get_rewrite_suggestions(
                "plot_logic_fix", plot, plot_prompt
            )
            
            if fix_suggestions:
                content['plot'] = await self._apply_fixes(plot, fix_suggestions)
        
        return content
    
    async def _rewrite_conflict_enhancement(self, content: Dict[str, Any], 
                                          decision: DecisionResult) -> Dict[str, Any]:
        """冲突增强重写"""
        print("⚔️ 执行冲突增强重写...")
        
        if 'plot' in content:
            plot = content['plot']
            
            # 生成冲突增强建议
            conflict_prompt = f"""
请分析以下剧情并增强戏剧冲突：

剧情内容：{plot}

请提供以下改进建议：
1. 增加主要冲突的激烈程度
2. 添加次要冲突和矛盾
3. 增强角色间的对立关系
4. 提高情节的紧张感
5. 确保冲突符合角色性格和世界观设定

请以JSON格式返回增强后的剧情内容。
"""
            
            response = await self.client.chat.completions.create(
                model=settings.AZURE_OPENAI_DEPLOYMENT_NAME,
                messages=[
                    {"role": "system", "content": "你是一个专业的剧情冲突设计师。"},
                    {"role": "user", "content": conflict_prompt}
                ],
                temperature=0.7,
                max_tokens=20000
            )
            
            try:
                enhanced_plot = response
                # 这里可以解析JSON并更新剧情
                content['plot'] = enhanced_plot
            except Exception as e:
                print(f"冲突增强重写失败: {e}")
        
        return content
    
    async def _rewrite_character_development(self, content: Dict[str, Any], 
                                           decision: DecisionResult) -> Dict[str, Any]:
        """角色发展重写"""
        print("👥 执行角色发展重写...")
        
        if 'characters' in content:
            characters = content['characters']
            
            for i, character in enumerate(characters):
                # 生成角色发展建议
                development_prompt = f"""
请分析以下角色并增强其发展：

角色信息：{character}

请提供以下改进建议：
1. 增强角色的性格特点
2. 丰富角色的背景故事
3. 明确角色的目标和动机
4. 改善角色的一致性
5. 增加角色的成长潜力

请以JSON格式返回增强后的角色信息。
"""
                
                response = await self.client.chat.completions.create(
                    model=settings.AZURE_OPENAI_DEPLOYMENT_NAME,
                    messages=[
                        {"role": "system", "content": "你是一个专业的角色发展设计师。"},
                        {"role": "user", "content": development_prompt}
                    ],
                    temperature=0.7,
                    max_tokens=20000
                )
                
                try:
                    enhanced_character = response
                    characters[i] = enhanced_character
                except Exception as e:
                    print(f"角色发展重写失败: {e}")
        
        return content
    
    async def _rewrite_plot_refinement(self, content: Dict[str, Any], 
                                     decision: DecisionResult) -> Dict[str, Any]:
        """剧情精炼重写"""
        print("📚 执行剧情精炼重写...")
        
        if 'plot' in content:
            plot = content['plot']
            
            # 生成剧情精炼建议
            refinement_prompt = f"""
请分析以下剧情并进行精炼：

剧情内容：{plot}

请提供以下改进建议：
1. 优化剧情结构
2. 增强创新元素
3. 改善情节发展
4. 增加伏笔设计
5. 提高整体质量

请以JSON格式返回精炼后的剧情内容。
"""
            
            response = await self.client.chat.completions.create(
                model=settings.AZURE_OPENAI_DEPLOYMENT_NAME,
                messages=[
                    {"role": "system", "content": "你是一个专业的剧情精炼师。"},
                    {"role": "user", "content": refinement_prompt}
                ],
                temperature=0.7,
                max_tokens=20000
            )
            
            try:
                refined_plot = response
                content['plot'] = refined_plot
            except Exception as e:
                print(f"剧情精炼重写失败: {e}")
        
        return content
    
    async def _rewrite_minor_adjustment(self, content: Dict[str, Any], 
                                      decision: DecisionResult) -> Dict[str, Any]:
        """小幅调整重写"""
        print("🔧 执行小幅调整重写...")
        
        # 对所有模块进行小幅调整
        for module in decision.target_modules:
            if module == 'world' and 'world_view' in content:
                content['world_view'] = await self._minor_adjust_world(content['world_view'])
            elif module == 'character' and 'characters' in content:
                content['characters'] = await self._minor_adjust_characters(content['characters'])
            elif module == 'plot' and 'plot' in content:
                content['plot'] = await self._minor_adjust_plot(content['plot'])
        
        return content
    
    async def _rewrite_major_rewrite(self, content: Dict[str, Any], 
                                   decision: DecisionResult) -> Dict[str, Any]:
        """大幅重写"""
        print("🔄 执行大幅重写...")
        
        # 重新生成所有内容
        if 'world_view' in content:
            world_view = content['world_view']
            core_concept = world_view.get('core_concept', '重新生成')
            
            # 重新生成世界观
            new_world_view = await self.world_service.create_world_view(
                core_concept=core_concept,
                description=None,
                additional_requirements={
                    "请重新生成世界观，修复所有逻辑问题",
                    "确保世界观逻辑自洽且富有想象力",
                    "这是大幅重写，请提供全新的优质内容"
                }
            )
            content['world_view'] = new_world_view.dict()
        
        if 'characters' in content:
            characters = content['characters']
            new_characters = []
            
            for character in characters:
                # 重新生成角色
                new_character = await self.character_service.create_character(
                    world_view_id=content['world_view']['id'],
                    character_requirements=[
                        "请重新生成角色，修复所有逻辑问题",
                        "确保角色符合世界观设定",
                        "这是大幅重写，请提供全新的优质角色"
                    ]
                )
                new_characters.append(new_character.dict())
            
            content['characters'] = new_characters
        
        if 'plot' in content:
            # 重新生成剧情
            new_plot = await self.plot_generator.generate_plot_outline(
                world_view=content['world_view'],
                characters=content['characters'],
                requirements={
                    "请重新生成剧情，修复所有逻辑问题",
                    "确保剧情符合世界观和角色设定",
                    "这是大幅重写，请提供全新的优质剧情"
                }
            )
            content['plot'] = new_plot.dict()
        
        return content
    
    async def _get_rewrite_suggestions(self, strategy: str, content: Dict[str, Any], 
                                     prompt: str) -> Optional[Dict[str, Any]]:
        """获取重写建议"""
        try:
            response = await self.client.chat.completions.create(
                model=settings.AZURE_OPENAI_DEPLOYMENT_NAME,
                messages=[
                    {"role": "system", "content": f"你是一个专业的{strategy}专家。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=20000
            )
            
            suggestions = response
            # 这里可以解析JSON格式的建议
            return {"suggestions": suggestions}
            
        except Exception as e:
            print(f"获取重写建议失败: {e}")
            return None
    
    async def _apply_fixes(self, content: Dict[str, Any], 
                          suggestions: Dict[str, Any]) -> Dict[str, Any]:
        """应用修复建议"""
        # 这里可以实现具体的修复逻辑
        # 目前返回原内容，实际应用中需要根据建议进行修改
        return content
    
    async def _minor_adjust_world(self, world_view: Dict[str, Any]) -> Dict[str, Any]:
        """小幅调整世界观"""
        # 实现世界观的小幅调整逻辑
        return world_view
    
    async def _minor_adjust_characters(self, characters: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """小幅调整角色"""
        # 实现角色的小幅调整逻辑
        return characters
    
    async def _minor_adjust_plot(self, plot: Dict[str, Any]) -> Dict[str, Any]:
        """小幅调整剧情"""
        # 实现剧情的小幅调整逻辑
        return plot
