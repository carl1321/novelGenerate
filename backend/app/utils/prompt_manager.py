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
    
    def get_character_generation_prompt(self, world_view: dict = None, character_requirements: str = "") -> str:
        """获取角色生成prompt"""
        prompt_func = self.load_prompt("character_generation")
        if callable(prompt_func):
            return prompt_func(world_view or {}, character_requirements)
        else:
            # 如果world_view为空，提供默认值
            if not world_view:
                world_view = {
                    'name': '未知世界观',
                    'description': '无描述',
                    'core_concept': '无核心概念',
                    'power_system': {'cultivation_realms': []},
                    'geography': {'main_regions': []}
                }
            return prompt_func.format(
                world_view=world_view,
                character_requirements=character_requirements
            )
    
    def get_batch_character_generation_prompt(self, world_view: dict = None, character_description: str = "", 
                                            character_count: int = 1, role_types: list = None) -> str:
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
                    return batch_func(world_view or {}, character_description, character_count, role_types or [])
            except Exception as e:
                print(f"加载批量角色生成函数失败: {e}")
            # 如果没有批量函数，使用普通函数
            return prompt_func(world_view or {}, character_description)
        else:
            # 如果world_view为空，提供默认值
            if not world_view:
                world_view = {
                    'name': '未知世界观',
                    'description': '无描述',
                    'core_concept': '无核心概念',
                    'power_system': {'cultivation_realms': []},
                    'geography': {'main_regions': []}
                }
            return prompt_func.format(
                world_view=world_view,
                character_description=character_description,
                character_count=character_count,
                role_types=role_types or []
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
    
    def get_plot_structure_prompt(self, request_data: dict, world_view: dict, characters: list) -> str:
        """获取剧情结构生成prompt"""
        prompt_func = self.load_prompt("plot_generation")
        if callable(prompt_func):
            # 尝试调用get_plot_structure_prompt方法
            if hasattr(prompt_func, 'get_plot_structure_prompt'):
                return prompt_func.get_plot_structure_prompt(request_data, world_view, characters)
            else:
                # 回退到基本方法
                return prompt_func(request_data.get('title', ''), 
                                 request_data.get('description', ''),
                                 request_data.get('power_system', ''),
                                 request_data.get('culture', ''),
                                 request_data.get('core_concept', ''),
                                 str(characters),
                                 request_data.get('plot_requirements', ''))
        else:
            return prompt_func.format(
                world_name=world_view.get('name', ''),
                world_description=world_view.get('description', ''),
                power_system=world_view.get('power_system', ''),
                culture=world_view.get('culture', ''),
                core_concept=request_data.get('core_concept', ''),
                characters_info=str(characters),
                plot_requirements=request_data.get('plot_requirements', '')
            )
    
    def get_chapter_generation_prompt(self, plot_outline: dict, chapter_template: dict, 
                                    chapter_number: int, world_view: dict, characters: list) -> str:
        """获取章节生成prompt"""
        prompt_func = self.load_prompt("plot_generation")
        if callable(prompt_func):
            # 尝试调用get_chapter_generation_prompt方法
            if hasattr(prompt_func, 'get_chapter_generation_prompt'):
                return prompt_func.get_chapter_generation_prompt(plot_outline, chapter_template, 
                                                               chapter_number, world_view, characters)
            else:
                # 回退到基本方法
                return prompt_func(plot_outline.get('title', ''),
                                 plot_outline.get('description', ''),
                                 world_view.get('power_system', ''),
                                 world_view.get('culture', ''),
                                 plot_outline.get('theme', ''),
                                 str(characters),
                                 plot_outline.get('main_conflict', ''))
        else:
            return prompt_func.format(
                world_name=world_view.get('name', ''),
                world_description=world_view.get('description', ''),
                power_system=world_view.get('power_system', ''),
                culture=world_view.get('culture', ''),
                core_concept=plot_outline.get('theme', ''),
                characters_info=str(characters),
                plot_requirements=plot_outline.get('main_conflict', '')
            )
    
    def get_character_arc_prompt(self, character: dict, plot_outline: dict) -> str:
        """获取角色发展弧线prompt"""
        prompt_func = self.load_prompt("plot_generation")
        if callable(prompt_func):
            # 尝试调用get_character_arc_prompt方法
            if hasattr(prompt_func, 'get_character_arc_prompt'):
                return prompt_func.get_character_arc_prompt(character, plot_outline)
            else:
                # 回退到基本方法
                return prompt_func(character.get('name', ''),
                                 character.get('background', ''),
                                 character.get('personality', ''),
                                 plot_outline.get('theme', ''),
                                 plot_outline.get('main_conflict', ''),
                                 str(character),
                                 plot_outline.get('description', ''))
        else:
            return prompt_func.format(
                world_name=character.get('name', ''),
                world_description=character.get('background', ''),
                power_system=character.get('abilities', ''),
                culture=character.get('personality', ''),
                core_concept=plot_outline.get('theme', ''),
                characters_info=str(character),
                plot_requirements=plot_outline.get('main_conflict', '')
            )
    
    def get_plot_validation_prompt(self, plot_outline: dict, validation_type: str = "logic") -> str:
        """获取剧情验证prompt"""
        prompt_func = self.load_prompt("plot_generation")
        if callable(prompt_func):
            # 尝试调用get_plot_validation_prompt方法
            if hasattr(prompt_func, 'get_plot_validation_prompt'):
                return prompt_func.get_plot_validation_prompt(plot_outline, validation_type)
            else:
                # 回退到基本方法
                return prompt_func(plot_outline.get('title', ''),
                                 plot_outline.get('description', ''),
                                 plot_outline.get('power_system', ''),
                                 plot_outline.get('culture', ''),
                                 plot_outline.get('theme', ''),
                                 str(plot_outline),
                                 f"验证类型: {validation_type}")
        else:
            return prompt_func.format(
                world_name=plot_outline.get('title', ''),
                world_description=plot_outline.get('description', ''),
                power_system=plot_outline.get('power_system', ''),
                culture=plot_outline.get('culture', ''),
                core_concept=plot_outline.get('theme', ''),
                characters_info=str(plot_outline),
                plot_requirements=f"验证类型: {validation_type}"
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
    
    def get_enhanced_event_generation_prompt(self, core_concept: str, world_description: str, 
                                           geography_setting: str, characters: List[Dict[str, Any]], 
                                           story_tone: str, narrative_structure: str, title: str,
                                           importance_distribution: Dict[str, int], event_requirements: str = "",
                                           selected_act: Optional[Dict[str, Any]] = None) -> str:
        """获取增强事件生成prompt（优化版本）"""
        prompt_func = self.load_prompt("event_generation")
        
        if callable(prompt_func):
            try:
                result = prompt_func(core_concept, world_description, geography_setting, characters,
                                   story_tone, narrative_structure, title, importance_distribution, 
                                   event_requirements, selected_act)
                return result
            except Exception as e:
                import traceback
                traceback.print_exc()
                raise
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
    
    def get_event_scoring_prompt(self, event, characters: List[Dict[str, Any]], 
                                world_info: Dict[str, Any], plot_info: Dict[str, Any]) -> str:
        """获取事件评分prompt"""
        prompt_func = self.load_prompt("event_scoring")
        if callable(prompt_func):
            return prompt_func(event, characters, world_info, plot_info)
        else:
            return prompt_func
    
    def get_event_evolution_prompt(self, event, score, characters: List[Dict[str, Any]], 
                                   world_info: Dict[str, Any], custom_description: str = "") -> str:
        """获取事件进化prompt"""
        prompt_func = self.load_prompt("event_evolution")
        if callable(prompt_func):
            return prompt_func(event, score, characters, world_info, custom_description)
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
    
    
    def get_part_world_update_prompt(self, world_view: Dict[str, Any] = None,
                                   update_type: str = "", update_content: str = "") -> str:
        """获取部分世界观更新prompt"""
        prompt_func = self.load_prompt("part_world_update")
        if callable(prompt_func):
            return prompt_func(world_view or {}, update_type, update_content)
        else:
            return prompt_func
    
    
    def get_detailed_plot_prompt(self, chapter_outline: Any, plot_outline: Any, 
                                world_view: Dict[str, Any], characters: List[Dict[str, Any]], 
                                events: List[Dict[str, Any]] = None, additional_requirements: str = None) -> str:
        """获取详细剧情生成prompt - 简化版（基于事件驱动）"""
        prompt_func = self.load_prompt("detailed_plot_generation")
        if callable(prompt_func):
            return prompt_func(chapter_outline, plot_outline, world_view, characters, events, additional_requirements)
        else:
            return prompt_func
    
    def get_detailed_plot_analysis_prompt(self, content: str) -> str:
        """获取详细剧情分析prompt"""
        prompt_func = self.load_prompt("detailed_plot_generation")
        if callable(prompt_func):
            # 尝试调用分析函数
            try:
                import sys
                import os
                prompts_dir = self.prompts_dir
                if str(prompts_dir) not in sys.path:
                    sys.path.insert(0, str(prompts_dir))
                
                import detailed_plot_generation
                if hasattr(detailed_plot_generation, 'get_detailed_plot_analysis_prompt'):
                    analysis_func = getattr(detailed_plot_generation, 'get_detailed_plot_analysis_prompt')
                    return analysis_func(content)
            except Exception as e:
                print(f"加载详细剧情分析函数失败: {e}")
            return prompt_func
        else:
            return prompt_func
    
    def get_detailed_plot_revision_prompt(self, original_content: str, revision_requirements: str, 
                                         analysis_feedback: str = None) -> str:
        """获取详细剧情修订prompt"""
        prompt_func = self.load_prompt("detailed_plot_generation")
        if callable(prompt_func):
            # 尝试调用修订函数
            try:
                import sys
                import os
                prompts_dir = self.prompts_dir
                if str(prompts_dir) not in sys.path:
                    sys.path.insert(0, str(prompts_dir))
                
                import detailed_plot_generation
                if hasattr(detailed_plot_generation, 'get_detailed_plot_revision_prompt'):
                    revision_func = getattr(detailed_plot_generation, 'get_detailed_plot_revision_prompt')
                    return revision_func(original_content, revision_requirements, analysis_feedback)
            except Exception as e:
                print(f"加载详细剧情修订函数失败: {e}")
            return prompt_func
        else:
            return prompt_func
    
    def get_detailed_plot_summary_prompt(self, content: str) -> str:
        """获取详细剧情摘要prompt"""
        prompt_func = self.load_prompt("detailed_plot_generation")
        if callable(prompt_func):
            # 尝试调用摘要函数
            try:
                import sys
                import os
                prompts_dir = self.prompts_dir
                if str(prompts_dir) not in sys.path:
                    sys.path.insert(0, str(prompts_dir))
                
                import detailed_plot_generation
                if hasattr(detailed_plot_generation, 'get_detailed_plot_summary_prompt'):
                    summary_func = getattr(detailed_plot_generation, 'get_detailed_plot_summary_prompt')
                    return summary_func(content)
            except Exception as e:
                print(f"加载详细剧情摘要函数失败: {e}")
            return prompt_func
        else:
            return prompt_func
    
    def get_evolution_prompt(self, content: str = "", evolution_type: str = "general") -> str:
        """获取进化智能体prompt"""
        prompt_func = self.load_prompt("evolution_agent")
        if callable(prompt_func):
            return prompt_func(content, evolution_type)
        else:
            return prompt_func.format(content=content, evolution_type=evolution_type)
    
    def get_correction_prompt(self, content: str = "", issues: list = None, user_prompt: str = "") -> str:
        """获取修正智能体prompt"""
        prompt_func = self.load_prompt("correction_agent")
        if callable(prompt_func):
            return prompt_func(content, issues or [], user_prompt)
        else:
            return prompt_func.format(content=content, issues=issues or [], user_prompt=user_prompt)
    
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
    
    def get_partial_update_prompt(
        self, 
        existing_worldview: Dict[str, Any],
        update_dimensions: List[str],
        update_description: str,
        additional_context: Optional[Dict[str, Any]] = None,
        merge_mode: str = "merge"
    ) -> str:
        """获取部分更新prompt"""
        # 动态加载part_world_update模块
        try:
            import importlib.util
            part_world_file = self.prompts_dir / "part_world_update.py"
            
            if part_world_file.exists():
                spec = importlib.util.spec_from_file_location("part_world_update", part_world_file)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                return module.get_partial_update_prompt(
                    existing_worldview=existing_worldview,
                    update_dimensions=update_dimensions,
                    update_description=update_description,
                    additional_context=additional_context,
                    merge_mode=merge_mode
                )
            else:
                raise Exception(f"部分更新prompt文件不存在: {part_world_file}")
                
        except Exception as e:
            raise Exception(f"获取部分更新prompt失败: {e}")
    
    def get_plot_outline_prompt(self, core_concept: str, world_description: str, 
                               geography_setting: str, protagonist_name: str,
                               protagonist_background: str, protagonist_personality: str,
                               protagonist_goals: str, core_conflict: str, story_tone: str,
                               narrative_structure: str, story_structure: str, theme: str, 
                               target_word_count: int, estimated_chapters: int) -> str:
        """获取剧情大纲生成prompt"""
        try:
            prompt_func = self.load_prompt("plot_outline_generation")
            if callable(prompt_func):
                return prompt_func(
                    core_concept, world_description, geography_setting, protagonist_name,
                    protagonist_background, protagonist_personality, protagonist_goals,
                    core_conflict, story_tone, narrative_structure, story_structure, theme, 
                    target_word_count, estimated_chapters
                )
            else:
                raise Exception("prompt函数不可调用")
        except Exception as e:
            raise Exception(f"获取剧情大纲prompt失败: {e}")


# 创建全局prompt管理器实例
prompt_manager = PromptManager()
