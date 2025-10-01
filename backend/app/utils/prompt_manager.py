"""
Prompt管理器
"""
import os
from pathlib import Path
from typing import Dict, Optional, Any, List


class PromptManager:
    """Prompt管理器类"""
    
    def __init__(self, prompts_dir: str = None):
        if prompts_dir is None:
            # 从backend目录向上两级到项目根目录，然后进入prompts目录
            current_dir = Path(__file__).parent
            project_root = current_dir.parent.parent.parent
            prompts_dir = project_root / "prompts"
        self.prompts_dir = Path(prompts_dir)
        self._prompts_cache = {}
    
    def load_prompt(self, prompt_name: str) -> str:
        """加载prompt文件"""
        if prompt_name in self._prompts_cache:
            return self._prompts_cache[prompt_name]
        
        # 优先尝试加载Python文件
        prompt_file = self.prompts_dir / f"{prompt_name}.py"
        
        if prompt_file.exists():
            try:
                # 动态导入Python模块
                import importlib.util
                spec = importlib.util.spec_from_file_location(prompt_name, prompt_file)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # 获取对应的函数
                function_name = f"get_{prompt_name}_prompt"
                if hasattr(module, function_name):
                    prompt_func = getattr(module, function_name)
                    # 缓存函数而不是结果，因为函数可能需要参数
                    self._prompts_cache[prompt_name] = prompt_func
                    return prompt_func
                else:
                    raise Exception(f"Python文件中没有找到函数: {function_name}")
                    
            except Exception as e:
                raise Exception(f"加载Python prompt文件失败: {e}")
        
        # 如果Python文件不存在，尝试加载txt文件
        prompt_file = self.prompts_dir / f"{prompt_name}.txt"
        
        if not prompt_file.exists():
            raise FileNotFoundError(f"Prompt文件不存在: {prompt_file}")
        
        try:
            with open(prompt_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self._prompts_cache[prompt_name] = content
            return content
            
        except Exception as e:
            raise Exception(f"加载prompt文件失败: {e}")
    
    def get_world_generation_prompt(self, core_concept: str = "", additional_requirements: str = "无特殊要求") -> str:
        """获取世界观生成prompt"""
        prompt_func = self.load_prompt("world_generation")
        if callable(prompt_func):
            return prompt_func(core_concept, additional_requirements)
        else:
            # 如果是字符串模板，使用format方法
            return prompt_func.format(
                core_concept=core_concept,
                additional_requirements=additional_requirements
            )
    
    def get_character_generation_prompt(self, world_name: str = "", world_description: str = "", 
                                       power_system: str = "", culture: str = "", 
                                       character_requirements: str = "") -> str:
        """获取角色生成prompt"""
        prompt_func = self.load_prompt("character_generation")
        if callable(prompt_func):
            return prompt_func(world_name, world_description, power_system, culture, character_requirements)
        else:
            return prompt_func.format(
                world_name=world_name,
                world_description=world_description,
                power_system=power_system,
                culture=culture,
                character_requirements=character_requirements
            )
    
    def get_batch_character_generation_prompt(self, world_name: str = "", world_description: str = "", 
                                            power_system: str = "", culture: str = "", 
                                            character_description: str = "", character_count: int = 1, 
                                            role_types: list = None) -> str:
        """获取批量角色生成prompt"""
        prompt_func = self.load_prompt("character_generation")
        if callable(prompt_func):
            # 检查是否有批量生成函数
            try:
                import sys
                import os
                # 添加prompts目录到Python路径
                prompts_dir = self.prompts_dir
                if str(prompts_dir) not in sys.path:
                    sys.path.insert(0, str(prompts_dir))
                
                import character_generation
                if hasattr(character_generation, 'get_batch_character_generation_prompt'):
                    batch_func = getattr(character_generation, 'get_batch_character_generation_prompt')
                    return batch_func(world_name, world_description, power_system, culture, 
                                    character_description, character_count, role_types or [])
            except Exception as e:
                print(f"加载批量角色生成函数失败: {e}")
            # 如果没有批量函数，使用普通函数
            return prompt_func(world_name, world_description, power_system, culture, character_description)
        else:
            return prompt_func.format(
                world_name=world_name,
                world_description=world_description,
                power_system=power_system,
                culture=culture,
                character_requirements=character_description
            )
    
    def get_plot_generation_prompt(self, world_name: str = "", world_description: str = "", 
                                 power_system: str = "", culture: str = "", 
                                 core_concept: str = "", characters_info: str = "", 
                                 plot_requirements: str = "") -> str:
        """获取剧情生成prompt"""
        prompt_func = self.load_prompt("plot_generation")
        if callable(prompt_func):
            return prompt_func(world_name, world_description, power_system, culture, 
                             core_concept, characters_info, plot_requirements)
        else:
            return prompt_func.format(
                world_name=world_name,
                world_description=world_description,
                power_system=power_system,
                culture=culture,
                core_concept=core_concept,
                characters_info=characters_info,
                plot_requirements=plot_requirements
            )
    
    def get_scoring_criteria_prompt(self, content: str = "", dimension: str = "all") -> str:
        """获取评分标准prompt"""
        prompt_func = self.load_prompt("scoring_criteria")
        if callable(prompt_func):
            return prompt_func(content, dimension)
        else:
            return prompt_func.format(content=content, dimension=dimension)
    
    def get_logic_check_prompt(self, content: str = "") -> str:
        """获取逻辑检查prompt"""
        prompt_func = self.load_prompt("logic_check")
        if callable(prompt_func):
            return prompt_func(content)
        else:
            return prompt_func.format(content=content)
    
    def get_character_growth_planning_prompt(self) -> str:
        """获取角色成长规划prompt"""
        return self.load_prompt("character_growth_planning")
    
    def get_foreshadowing_network_creation_prompt(self, plot_outline: dict = None, characters: str = "",
                                                world_view: dict = None, templates: str = "") -> str:
        """获取伏笔网络创建prompt"""
        prompt_func = self.load_prompt("foreshadowing_network_creation")
        if callable(prompt_func):
            return prompt_func(plot_outline or {}, characters, world_view or {}, templates)
        else:
            return prompt_func
    
    def get_chapter_outline_generation_prompt(self, plot_segment: dict = None, previous_chapters: str = "",
                                           current_chapter_number: int = 1, world_view: dict = None,
                                           characters: str = "", locations: str = "", 
                                           organizations: str = "", foreshadowing_network: str = "",
                                           validation_warnings: str = "") -> str:
        """获取章节大纲生成prompt"""
        prompt_func = self.load_prompt("chapter_outline_generation")
        if callable(prompt_func):
            return prompt_func(plot_segment or {}, previous_chapters, current_chapter_number,
                             world_view or {}, characters, locations, organizations,
                             foreshadowing_network, validation_warnings)
        else:
            return prompt_func
    
    def get_event_generation_prompt(self, event_type: str = "", world_name: str = "", 
                                  world_description: str = "", power_system: str = "",
                                  characters_info: str = "", event_requirements: str = "") -> str:
        """获取事件生成prompt"""
        prompt_func = self.load_prompt("event_generation")
        if callable(prompt_func):
            return prompt_func(event_type, world_name, world_description, power_system,
                             characters_info, event_requirements)
        else:
            return prompt_func
    
    def get_plot_engine_prompt(self, world_name: str = "", world_description: str = "",
                             power_system: str = "", characters_info: str = "",
                             events_info: str = "", plot_title: str = "",
                             plot_description: str = "", core_concept: str = "",
                             target_length: int = 10) -> str:
        """获取剧情引擎prompt"""
        prompt_func = self.load_prompt("plot_engine")
        if callable(prompt_func):
            return prompt_func(world_name, world_description, power_system, characters_info,
                             events_info, plot_title, plot_description, core_concept, target_length)
        else:
            return prompt_func
    
    def get_event_generation_prompt(self, world_view: Dict[str, Any] = None,
                                  characters: List[Dict[str, Any]] = None,
                                  event_requirements: List[str] = None,
                                  event_type: str = "daily") -> str:
        """获取事件生成prompt"""
        prompt_func = self.load_prompt("event_generation")
        if callable(prompt_func):
            return prompt_func(world_view or {}, characters or [], event_requirements or [], event_type)
        else:
            return prompt_func
    
    def get_chapter_outline_generation_prompt(self, world_view: Dict[str, Any] = None,
                                            characters: List[Dict[str, Any]] = None,
                                            plot_points: List[Dict[str, Any]] = None,
                                            chapter_count: int = 10) -> str:
        """获取章节大纲生成prompt"""
        prompt_func = self.load_prompt("chapter_outline_generation")
        if callable(prompt_func):
            return prompt_func(world_view or {}, characters or [], plot_points or [], chapter_count)
        else:
            return prompt_func
    
    def get_foreshadowing_network_creation_prompt(self, world_view: Dict[str, Any] = None,
                                                characters: List[Dict[str, Any]] = None,
                                                plot_points: List[Dict[str, Any]] = None) -> str:
        """获取伏笔网络创建prompt"""
        prompt_func = self.load_prompt("foreshadowing_network_creation")
        if callable(prompt_func):
            return prompt_func(world_view or {}, characters or [], plot_points or [])
        else:
            return prompt_func
    
    def get_logic_check_prompt(self, content: str = "", context: Dict[str, Any] = None) -> str:
        """获取逻辑检查prompt"""
        prompt_func = self.load_prompt("logic_check")
        if callable(prompt_func):
            return prompt_func(content, context or {})
        else:
            return prompt_func
    
    def get_part_world_update_prompt(self, world_view: Dict[str, Any] = None,
                                   update_type: str = "", update_content: str = "") -> str:
        """获取部分世界观更新prompt"""
        prompt_func = self.load_prompt("part_world_update")
        if callable(prompt_func):
            return prompt_func(world_view or {}, update_type, update_content)
        else:
            return prompt_func
    
    def get_scoring_criteria_prompt(self, content_type: str = "", content: str = "") -> str:
        """获取评分标准prompt"""
        prompt_func = self.load_prompt("scoring_criteria")
        if callable(prompt_func):
            return prompt_func(content_type, content)
        else:
            return prompt_func
    
    def build_prompt(self, prompt_name: str, **kwargs) -> str:
        """构建带参数的prompt"""
        base_prompt = self.load_prompt(prompt_name)
        
        # 替换参数
        for key, value in kwargs.items():
            placeholder = f"{{{key}}}"
            base_prompt = base_prompt.replace(placeholder, str(value))
        
        return base_prompt
    
    def get_available_prompts(self) -> list:
        """获取可用的prompt列表"""
        if not self.prompts_dir.exists():
            return []
        
        # 优先查找Python文件
        prompt_files = list(self.prompts_dir.glob("*.py"))
        if not prompt_files:
            # 如果没有Python文件，查找txt文件
            prompt_files = list(self.prompts_dir.glob("*.txt"))
        
        return [f.stem for f in prompt_files]
    
    def clear_cache(self):
        """清空prompt缓存"""
        self._prompts_cache.clear()


# 创建全局prompt管理器实例
prompt_manager = PromptManager()
