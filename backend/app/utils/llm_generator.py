"""
通用LLM生成器
所有模块共用的LLM生成功能
"""
import json
import asyncio
from typing import Dict, List, Any, Optional, Union
from app.utils import llm_client, dynamic_parser
from app.utils.prompt_manager import PromptManager


class UniversalLLMGenerator:
    """通用LLM生成器"""
    
    def __init__(self):
        self.prompt_manager = PromptManager()
    
    async def generate_content(self, 
                             prompt_type: str,
                             **kwargs) -> Dict[str, Any]:
        """
        通用内容生成方法
        
        Args:
            prompt_type: prompt类型，对应prompts目录中的文件名
            **kwargs: 传递给prompt的参数
            
        Returns:
            解析后的JSON数据
        """
        try:
            # 获取prompt
            prompt = self._get_prompt(prompt_type, **kwargs)
            
            # 调用LLM
            response = await llm_client.generate_text(prompt)
            
            # 解析响应
            result = dynamic_parser.parse_json(response)
            if not result:
                raise Exception("LLM返回格式错误或无法解析")
            
            return result
            
        except Exception as e:
            print(f"LLM生成失败: {e}")
            raise
    
    async def generate_chat_content(self,
                                  prompt_type: str,
                                  system_message: str = None,
                                  **kwargs) -> Dict[str, Any]:
        """
        使用对话模式生成内容
        
        Args:
            prompt_type: prompt类型
            system_message: 系统消息，如果为None则使用默认
            **kwargs: 传递给prompt的参数
            
        Returns:
            解析后的JSON数据
        """
        try:
            # 获取prompt
            prompt = self._get_prompt(prompt_type, **kwargs)
            
            # 构建消息
            messages = []
            if system_message:
                messages.append({"role": "system", "content": system_message})
            else:
                # 使用默认系统消息
                messages.append({"role": "system", "content": "你是一个专业的AI助手，请根据用户要求生成高质量的内容。"})
            
            messages.append({"role": "user", "content": prompt})
            
            # 调用LLM
            response = await llm_client.generate_chat(messages)
            
            # 解析响应
            result = dynamic_parser.parse_json(response)
            if not result:
                raise Exception("LLM返回格式错误或无法解析")
            
            return result
            
        except Exception as e:
            print(f"LLM对话生成失败: {e}")
            raise
    
    def _get_prompt(self, prompt_type: str, **kwargs) -> str:
        """获取prompt"""
        try:
            # 根据prompt类型调用对应的方法
            if prompt_type == "world_generation":
                return self.prompt_manager.get_world_generation_prompt(**kwargs)
            elif prompt_type == "character_generation":
                return self.prompt_manager.get_character_generation_prompt(**kwargs)
            elif prompt_type == "batch_character_generation":
                return self.prompt_manager.get_batch_character_generation_prompt(**kwargs)
            elif prompt_type == "plot_generation":
                return self.prompt_manager.get_plot_generation_prompt(**kwargs)
            elif prompt_type == "event_generation":
                return self.prompt_manager.get_event_generation_prompt(**kwargs)
            elif prompt_type == "chapter_outline_generation":
                return self.prompt_manager.get_chapter_outline_generation_prompt(**kwargs)
            elif prompt_type == "foreshadowing_network_creation":
                return self.prompt_manager.get_foreshadowing_network_creation_prompt(**kwargs)
            elif prompt_type == "logic_check":
                return self.prompt_manager.get_logic_check_prompt(**kwargs)
            elif prompt_type == "part_world_update":
                return self.prompt_manager.get_part_world_update_prompt(**kwargs)
            elif prompt_type == "plot_engine":
                return self.prompt_manager.get_plot_engine_prompt(**kwargs)
            elif prompt_type == "scoring_criteria":
                return self.prompt_manager.get_scoring_criteria_prompt(**kwargs)
            else:
                # 通用方法，直接加载prompt文件
                prompt_func = self.prompt_manager.load_prompt(prompt_type)
                if callable(prompt_func):
                    return prompt_func(**kwargs)
                else:
                    return prompt_func.format(**kwargs)
                    
        except Exception as e:
            print(f"获取prompt失败: {e}")
            raise
    
    # 便捷方法，对应各个模块的生成需求
    
    async def generate_world_view(self, core_concept: str, 
                                description: str = None,
                                additional_requirements: str = None) -> Dict[str, Any]:
        """生成世界观"""
        # 整合核心概念和描述
        full_concept = core_concept
        if description:
            full_concept = f"{core_concept}\n\n详细描述：{description}"
        
        return await self.generate_content(
            "world_generation",
            core_concept=full_concept,
            additional_requirements=additional_requirements or "无特殊要求"
        )
    
    async def generate_character(self, world_name: str, world_description: str,
                               power_system: str, culture: str,
                               character_requirements: str) -> Dict[str, Any]:
        """生成单个角色"""
        return await self.generate_content(
            "character_generation",
            world_name=world_name,
            world_description=world_description,
            power_system=power_system,
            culture=culture,
            character_requirements=character_requirements
        )
    
    async def generate_characters_batch(self, world_name: str, world_description: str,
                                      power_system: str, culture: str,
                                      character_description: str, character_count: int,
                                      role_types: List[str]) -> Dict[str, Any]:
        """批量生成角色"""
        return await self.generate_content(
            "batch_character_generation",
            world_name=world_name,
            world_description=world_description,
            power_system=power_system,
            culture=culture,
            character_description=character_description,
            character_count=character_count,
            role_types=role_types
        )
    
    async def generate_plot(self, world_name: str, world_description: str,
                          power_system: str, culture: str, core_concept: str,
                          characters_info: str, plot_requirements: str) -> Dict[str, Any]:
        """生成剧情"""
        return await self.generate_content(
            "plot_generation",
            world_name=world_name,
            world_description=world_description,
            power_system=power_system,
            culture=culture,
            core_concept=core_concept,
            characters_info=characters_info,
            plot_requirements=plot_requirements
        )
    
    async def generate_event(self, world_view: Dict[str, Any],
                           characters: List[Dict[str, Any]],
                           event_requirements: List[str],
                           event_type: str = "daily") -> Dict[str, Any]:
        """生成事件"""
        return await self.generate_content(
            "event_generation",
            world_view=world_view,
            characters=characters,
            event_requirements=event_requirements,
            event_type=event_type
        )
    
    async def generate_chapter_outline(self, world_view: Dict[str, Any],
                                     characters: List[Dict[str, Any]],
                                     plot_points: List[Dict[str, Any]],
                                     chapter_count: int) -> Dict[str, Any]:
        """生成章节大纲"""
        return await self.generate_content(
            "chapter_outline_generation",
            world_view=world_view,
            characters=characters,
            plot_points=plot_points,
            chapter_count=chapter_count
        )
    
    async def generate_foreshadowing_network(self, world_view: Dict[str, Any],
                                           characters: List[Dict[str, Any]],
                                           plot_points: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成伏笔网络"""
        return await self.generate_content(
            "foreshadowing_network_creation",
            world_view=world_view,
            characters=characters,
            plot_points=plot_points
        )
    
    async def check_logic(self, content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """逻辑检查"""
        return await self.generate_content(
            "logic_check",
            content=content,
            context=context
        )
    
    async def update_world_part(self, world_view: Dict[str, Any],
                              update_type: str, update_content: str) -> Dict[str, Any]:
        """部分更新世界观"""
        return await self.generate_content(
            "part_world_update",
            world_view=world_view,
            update_type=update_type,
            update_content=update_content
        )
    
    async def generate_plot_engine(self, world_view: Dict[str, Any],
                                 characters: List[Dict[str, Any]],
                                 current_plot: Dict[str, Any]) -> Dict[str, Any]:
        """剧情引擎生成"""
        return await self.generate_content(
            "plot_engine",
            world_view=world_view,
            characters=characters,
            current_plot=current_plot
        )
    
    async def generate_scoring_criteria(self, content_type: str,
                                      content: str) -> Dict[str, Any]:
        """生成评分标准"""
        return await self.generate_content(
            "scoring_criteria",
            content_type=content_type,
            content=content
        )


# 创建全局实例
universal_llm_generator = UniversalLLMGenerator()
