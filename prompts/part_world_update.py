"""
部分世界观更新提示词
"""
from typing import Dict, List, Any, Optional


def get_partial_update_prompt(
    existing_worldview: Dict[str, Any],
    update_dimensions: List[str],
    update_description: str,
    additional_context: Optional[Dict[str, Any]] = None,
    merge_mode: str = "merge"  # "merge" 或 "replace"
) -> str:
    """
    获取部分更新提示词
    
    Args:
        existing_worldview: 现有世界观数据
        update_dimensions: 要更新的维度列表
        update_description: 更新描述
        additional_context: 额外上下文
        
    Returns:
        格式化的提示词
    """
    
    # 构建现有世界观摘要
    existing_summary = _build_worldview_summary(existing_worldview)
    
    # 构建更新维度说明
    dimension_descriptions = _get_dimension_descriptions(update_dimensions)
    
    # 构建保留维度说明
    preserve_dimensions = [dim for dim in ['power_system', 'geography', 'culture', 'history'] 
                          if dim not in update_dimensions]
    
    update_instruction = f"""
## 更新模式判断
请根据更新描述自动判断处理方式：
- 如果描述包含"增加"、"添加"、"新增"、"补充"等词汇，使用"merge"模式
- 如果描述包含"修改"、"更新"、"重新设计"、"替换"等词汇，使用"replace"模式
- 如果描述不明确，默认使用"merge"模式

在输出的JSON中添加"update_mode"字段来指示处理方式。
"""

    prompt = f"""
# 世界观部分更新任务

## 现有世界观信息
{existing_summary}

## 更新要求
- **更新维度**: {', '.join(update_dimensions)}
- **更新描述**: {update_description}
- **保留维度**: {', '.join(preserve_dimensions) if preserve_dimensions else '无'}

{update_instruction}

## 维度说明
{dimension_descriptions}

## 输出要求
1. 只返回需要更新的维度JSON数据
2. 保持与现有世界观的一致性
3. 确保更新内容符合更新描述
4. 不要包含保留维度的数据
5. **重要：每个数组元素必须是完整的对象，不能是简单字符串**
6. **重要：确保所有字段都有具体内容，不能为空或"暂无设定"**

## 输出格式
请严格按照以下JSON结构输出，注意每个数组元素都必须是完整的对象：

{{
    "update_mode": "merge",  // 或 "replace"，根据更新描述自动判断
    "power_system": {{
        "cultivation_realms": [
            {{"name": "境界名称", "level": 1, "description": "详细描述", "requirements": "突破要求"}}
        ],
        "energy_types": [
            {{"name": "能量名称", "rarity": "稀有度", "description": "详细描述"}}
        ],
        "technique_categories": [
            {{"name": "功法名称", "description": "详细描述", "difficulty": "难度等级"}}
        ]
    }},
    "geography": {{
        "main_regions": [
            {{"name": "区域名称", "type": "区域类型", "description": "详细描述", "resources": ["资源1", "资源2"], "special_features": "特色描述"}}
        ],
        "special_locations": [
            {{"name": "地点名称", "type": "地点类型", "description": "详细描述", "significance": "重要性", "dangers": ["危险1", "危险2"]}}
        ]
    }},
    "culture": {{
        "organizations": [
            {{"name": "组织名称", "type": "组织类型", "description": "详细描述", "power_level": "实力等级", "ideology": "理念宗旨", "structure": "组织结构"}}
        ],
        "social_system": {{
            "hierarchy": "等级制度详细描述",
            "economy": "经济体系详细描述", 
            "trading": "交易方式详细描述"
        }}
    }},
    "history": {{
        "historical_events": [
            {{"name": "事件名称", "time_period": "时间时期", "description": "详细描述", "impact": "影响描述"}}
        ],
        "cultural_features": [
            {{"region": "文化区域", "traditions": "传统习俗", "values": "价值观念", "lifestyle": "生活方式"}}
        ],
        "current_conflicts": [
            {{"name": "冲突名称", "description": "详细描述", "parties": ["参与方1", "参与方2"], "stakes": "利害关系"}}
        ]
    }}
}}

## 注意事项
- 保持世界观的整体风格和设定
- 确保更新内容与现有内容逻辑一致
- 如果某个维度不需要更新，请不要在输出中包含该维度
- **每个数组元素必须是完整的对象，包含所有指定字段**
- **所有描述字段都要有具体内容，不能为空或"暂无设定"**
"""
    
    return prompt


def _build_worldview_summary(worldview: Dict[str, Any]) -> str:
    """构建世界观摘要"""
    return f"""
**基本信息**:
- 名称: {worldview.get('name', '未命名')}
- 核心概念: {worldview.get('core_concept', '未定义')}
- 描述: {worldview.get('description', '无描述')}

**力量体系**: {len(worldview.get('power_system', {}).get('cultivation_realms', []))} 个境界
**地理设定**: {len(worldview.get('geography', {}).get('main_regions', []))} 个区域
**社会组织**: {len(worldview.get('culture', {}).get('organizations', []))} 个组织
**历史文化**: {len(worldview.get('history', {}).get('historical_events', []))} 个历史事件
"""


def _get_dimension_descriptions(update_dimensions: List[str]) -> str:
    """获取维度说明"""
    descriptions = {
        'power_system': """
**力量体系** (power_system):
- cultivation_realms: 修炼境界对象数组，每个对象包含 {name, level, description, requirements}
- energy_types: 能量类型对象数组，每个对象包含 {name, rarity, description}
- technique_categories: 功法分类对象数组，每个对象包含 {name, description, difficulty}
""",
        'geography': """
**地理设定** (geography):
- main_regions: 主要区域对象数组，每个对象包含 {name, type, description, resources, special_features}
- special_locations: 特殊地点对象数组，每个对象包含 {name, type, description, significance, dangers}
""",
        'culture': """
**社会组织** (culture):
- organizations: 组织对象数组，每个对象包含 {name, type, description, power_level, ideology, structure}
- social_system: 社会制度对象，包含 {hierarchy, economy, trading}
""",
        'history': """
**历史文化** (history):
- historical_events: 历史事件对象数组，每个对象包含 {name, time_period, description, impact}
- cultural_features: 文化特色对象数组，每个对象包含 {region, traditions, values, lifestyle}
- current_conflicts: 当前冲突对象数组，每个对象包含 {name, description, parties, stakes}
"""
    }
    
    return '\n'.join([descriptions.get(dim, '') for dim in update_dimensions])
