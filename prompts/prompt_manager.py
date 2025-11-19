"""
统一提示词管理器
"""
from typing import Dict, List, Any, Optional


class PromptManager:
    """统一提示词管理器"""
    
    def __init__(self):
        self.prompt_cache = {}
    
    def get_world_generation_prompt(self, core_concept: str, description: str = None) -> str:
        """获取完整世界观生成提示词"""
        from .world_generation import get_world_generation_prompt
        return get_world_generation_prompt(core_concept, description)
    
    def get_partial_update_prompt(
        self,
        existing_worldview: Dict[str, Any],
        update_dimensions: List[str],
        update_description: str,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """获取部分更新提示词"""
        from .part_world_update import get_partial_update_prompt
        return get_partial_update_prompt(
            existing_worldview, update_dimensions, update_description, additional_context
        )
    
    def get_dimension_specific_prompt(
        self,
        dimension: str,
        existing_data: Dict[str, Any],
        update_description: str
    ) -> str:
        """获取特定维度的更新提示词"""
        
        # 直接在manager中定义各维度的提示词模板
        dimension_templates = {
            'power_system': self._get_power_system_template,
            'geography': self._get_geography_template,
            'culture': self._get_culture_template,
            'history': self._get_history_template
        }
        
        if dimension in dimension_templates:
            return dimension_templates[dimension](existing_data, update_description)
        else:
            raise ValueError(f"不支持的维度: {dimension}")
    
    def get_detailed_plot_prompt(
        self,
        chapter_outline: Any,
        plot_outline: Any,
        world_view: Dict[str, Any],
        characters: List[Dict[str, Any]],
        additional_requirements: Optional[str] = None
    ) -> str:
        """获取详细剧情生成提示词"""
        from .detailed_plot_generation import get_detailed_plot_prompt
        return get_detailed_plot_prompt(
            chapter_outline, plot_outline, world_view, characters, additional_requirements
        )
    
    def get_detailed_plot_analysis_prompt(self, content: str) -> str:
        """获取详细剧情分析提示词"""
        from .detailed_plot_generation import get_detailed_plot_analysis_prompt
        return get_detailed_plot_analysis_prompt(content)
    
    def get_detailed_plot_revision_prompt(
        self,
        original_content: str,
        revision_requirements: str,
        analysis_feedback: str = None
    ) -> str:
        """获取详细剧情修订提示词"""
        from .detailed_plot_generation import get_detailed_plot_revision_prompt
        return get_detailed_plot_revision_prompt(
            original_content, revision_requirements, analysis_feedback
        )
    
    def get_detailed_plot_summary_prompt(self, content: str) -> str:
        """获取详细剧情摘要提示词"""
        from .detailed_plot_generation import get_detailed_plot_summary_prompt
        return get_detailed_plot_summary_prompt(content)
    
    def get_character_generation_prompt(self, world_view: dict, character_requirements: str) -> str:
        """获取角色生成提示词"""
        from .character_generation import get_character_generation_prompt
        return get_character_generation_prompt(world_view, character_requirements)
    
    def get_batch_character_generation_prompt(self, world_view: dict, character_description: str, 
                                            character_count: int, role_types: list) -> str:
        """获取批量角色生成提示词"""
        from .character_generation import get_batch_character_generation_prompt
        return get_batch_character_generation_prompt(
            world_view, character_description, character_count, role_types
        )
    
    
    def _get_power_system_template(self, existing_data: Dict[str, Any], update_description: str) -> str:
        """力量体系提示词模板"""
        return f"""
# 力量体系更新任务

## 现有力量体系
- 修炼境界: {len(existing_data.get('cultivation_realms', []))} 个
- 能量类型: {len(existing_data.get('energy_types', []))} 个  
- 功法分类: {len(existing_data.get('technique_categories', []))} 个

## 更新要求
{update_description}

## 输出格式
请返回JSON格式的力量体系数据：
```json
{{
    "cultivation_realms": [
        {{
            "name": "境界名称",
            "level": 境界等级,
            "description": "境界描述",
            "requirements": "突破要求"
        }}
    ],
    "energy_types": [
        {{
            "name": "能量名称",
            "rarity": "稀有度",
            "description": "能量描述"
        }}
    ],
    "technique_categories": [
        {{
            "name": "功法名称",
            "description": "功法描述",
            "difficulty": "难度等级"
        }}
    ]
}}
```
"""
    
    def _get_geography_template(self, existing_data: Dict[str, Any], update_description: str) -> str:
        """地理设定提示词模板"""
        return f"""
# 地理设定更新任务

## 现有地理设定
- 主要区域: {len(existing_data.get('main_regions', []))} 个
- 特殊地点: {len(existing_data.get('special_locations', []))} 个

## 更新要求
{update_description}

## 输出格式
请返回JSON格式的地理设定数据：
```json
{{
    "main_regions": [
        {{
            "name": "区域名称",
            "type": "区域类型",
            "description": "区域描述",
            "resources": ["资源1", "资源2"],
            "special_features": "特殊特征"
        }}
    ],
    "special_locations": [
        {{
            "name": "地点名称",
            "type": "地点类型",
            "description": "地点描述",
            "significance": "重要性",
            "dangers": ["危险1", "危险2"]
        }}
    ]
}}
```
"""
    
    def _get_culture_template(self, existing_data: Dict[str, Any], update_description: str) -> str:
        """社会组织提示词模板"""
        return f"""
# 社会组织更新任务

## 现有社会组织
- 组织数量: {len(existing_data.get('organizations', []))} 个
- 社会制度: {'有' if existing_data.get('social_system') else '无'}

## 更新要求
{update_description}

## 输出格式
请返回JSON格式的社会组织数据：
```json
{{
    "organizations": [
        {{
            "name": "组织名称",
            "type": "组织类型",
            "description": "组织描述",
            "power_level": "实力等级",
            "ideology": "理念宗旨",
            "structure": "组织结构"
        }}
    ],
    "social_system": {{
        "hierarchy": "等级制度",
        "economy": "经济体系",
        "trading": "交易方式"
    }}
}}
```
"""
    
    def _get_history_template(self, existing_data: Dict[str, Any], update_description: str) -> str:
        """历史文化提示词模板"""
        return f"""
# 历史文化更新任务

## 现有历史文化
- 历史事件: {len(existing_data.get('historical_events', []))} 个
- 文化特色: {len(existing_data.get('cultural_features', []))} 个
- 当前冲突: {len(existing_data.get('current_conflicts', []))} 个

## 更新要求
{update_description}

## 输出格式
请返回JSON格式的历史文化数据：
```json
{{
    "historical_events": [
        {{
            "name": "事件名称",
            "time_period": "时间时期",
            "description": "事件描述",
            "impact": "影响"
        }}
    ],
    "cultural_features": [
        {{
            "region": "文化区域",
            "traditions": "传统习俗",
            "values": "价值观念",
            "lifestyle": "生活方式"
        }}
    ],
    "current_conflicts": [
        {{
            "name": "冲突名称",
            "description": "冲突描述",
            "parties": ["参与方1", "参与方2"],
            "stakes": "利害关系"
        }}
    ]
}}
```
"""
