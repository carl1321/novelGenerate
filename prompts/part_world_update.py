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
    preserve_dimensions = [dim for dim in ['power_system', 'geography', 'history'] 
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

## 地理布局要求
- **宏观版块划分**：将整个世界划分为4-6个大地图版块（如中洲、东陵、西烬、北荒、南瘴等）
- **版块面积宏大**：每个版块都要有宏大的面积范围，如方圆千里、横跨三州等
- **版块边界清晰**：版块间有明确的地理边界（山脉、河流、海洋、沙漠等自然分界线）
- **版块特色鲜明**：每个版块都要有独特的地理特征、气候环境和资源分布
- **版块内势力分布**：每个版块内必须包含3-4个主要势力，势力要符合版块特色

#### 典型版块分布示例
- **中洲版块**：中央皇畿，四面临山，易守难攻，朝廷势力核心，方圆千里
- **东陵版块**：修仙山脉，连绵不绝，灵气浓郁，修仙门派聚集，横跨三州
- **北荒版块**：荒原草原，雪山阻隔，气候严寒，武者组织聚集，广袤无垠
- **西烬版块**：沙漠戈壁，移动沙丘，遗迹众多，寻宝者聚集，黄沙万里
- **南瘴版块**：瘴气森林，毒虫横行，神秘莫测，巫教组织聚集，瘴气弥漫
- **东海版块**：群岛星罗，海风湿润，贸易繁荣，散修聚集，岛屿众多

## 地理设定符合性要求
- **朝廷势力版块**：必须有皇城、城镇、乡村等核心区域，通常位于中央版块
- **商业组织版块**：必须有商会总部、分店、仓库等设施，通常位于交通枢纽版块
- **诸侯势力版块**：必须有各方势力分布地区，围绕中央版块周边分布，且距离较远
- **土匪势力版块**：所在的版块必须有山寨、土匪窝、山洞等设施，依山而建，通常是小山头
- **神秘组织版块**：必须有隐秘据点、仪式场所、秘密通道等
- **修仙门派版块**：必须有山门、修炼洞府、灵田、藏经阁等设施，通常位于山脉、海岛版块

## 输出要求
1. 只返回需要更新的维度JSON数据
2. 保持与现有世界观的一致性
3. 确保更新内容符合更新描述
4. 不要包含保留维度的数据
5. **重要：每个数组元素必须是完整的对象，不能是简单字符串**
6. **重要：确保所有字段都有具体内容，不能为空或"暂无设定"**
7. **地理建筑匹配性：每个势力的地理建筑必须与其类型和功能完全匹配**
8. **地理逻辑自洽：朝廷区域必须有皇城，修仙区域必须有山门，商业区域必须有市场**
9. **核心区域优先：特殊地点只包含核心区域（皇城、主山门、核心要塞等），不包含小村庄、小据点等次要地点**

## 输出格式
请严格按照以下JSON结构输出，注意每个数组元素都必须是完整的对象：

{{
    "update_mode": "merge",  // 或 "replace"，根据更新描述自动判断
    "power_system": {{
        "cultivation_realms": [
            {{"name": "境界名称", "level": 1, "description": "详细描述", "energy_type": "能量类型一句话描述，如：气血之力，凡人与武者共有的基础能量，源于饮食、锻炼与意志，是武道根基"}}
        ]
    }},
    "geography": {{
        "main_regions": [
            {{
                "name": "大地图版块名称（如：中洲、东陵、西烬、北荒、南瘴等）",
                "type": "版块类型（如：中央皇畿、修仙山脉、沙漠戈壁、荒原草原、瘴气森林等）", 
                "description": "版块整体描述，包括地理特征、气候环境、主要地形",
                "area_scope": "版块面积范围（如：方圆千里、横跨三州等）",
                "boundaries": "版块边界描述（如：东至东海，西接西烬沙海等）",
                "resources": ["版块内主要资源"],
                "special_features": "版块特色（如：终年雷暴、瘴气弥漫、灵气浓郁等）",
                "forces": [  // 每个区域必须包含3-4个主要势力
                    {{
                        "name": "版块内主要势力名称1",
                        "type": "势力类型1",
                        "description": "势力在版块中的地位和作用",
                        "power_level": "实力等级",
                        "influence": "在版块内的影响力范围",
                        "territory_control": "控制的版块区域（如：版块东部、版块核心等）",
                        "resources_controlled": ["控制的版块资源"],
                        "relationships": {{
                            "allies": ["版块内盟友势力"],
                            "enemies": ["版块内敌对势力"],
                            "neutral": ["版块内中立势力"]
                        }}
                    }}
                ]
            }}
        ]
    }}
}}

## 注意事项
- 保持世界观的整体风格和设定
- 确保更新内容与现有内容逻辑一致
- 如果某个维度不需要更新，请不要在输出中包含该维度
- **每个数组元素必须是完整的对象，包含所有指定字段**
- **所有描述字段都要有具体内容，不能为空或"暂无设定"**
- **宏观地理分布：将整个世界划分为4-6个大型区域，每个区域占据地图的15-25%面积**
- **地理势力一体化：每个地理区域都要有完整的势力分布，每个区域必须包含3-4个主要势力**
- **势力关系网络化：明确各势力间的复杂关系，如动乱的朝廷，那么必然有起义军和地方割据势力**
- **资源控制具体化：每个势力都要控制具体的资源**
- **区域边界明确：区域间有明确的地理边界（山脉、河流、海洋、沙漠等）**
- **空间关系合理：区域间距离适中，便于势力互动和贸易往来**
- **地理建筑匹配性：每个势力的地理建筑必须与其类型和功能完全匹配**
- **地理逻辑自洽：朝廷区域必须有皇城，修仙区域必须有山门，商业区域必须有市场**
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
**地理设定**: {len(worldview.get('geography', {}).get('regions', worldview.get('geography', {}).get('main_regions', [])))} 个区域
**历史文化**: {len(worldview.get('history', {}).get('historical_events', []))} 个历史事件
"""


def _get_dimension_descriptions(update_dimensions: List[str]) -> str:
    """获取维度说明"""
    descriptions = {
        'power_system': """
**力量体系** (power_system):
- cultivation_realms: 修炼境界对象数组，每个对象包含 {name, level, description, energy_type}
- energy_type: 能量类型一句话描述，如：气血之力，凡人与武者共有的基础能量，源于饮食、锻炼与意志，是武道根基
""",
        'geography': """
**地理设定** (geography):
- regions: 大地图版块对象数组，每个版块包含 {name, type, description, area_scope, boundaries, resources, special_features, forces}
- forces: 版块内势力分布数组，每个势力包含 {name, type, description, power_level, influence, territory_control, resources_controlled, relationships}
- relationships: 势力关系对象，包含 {allies, enemies, neutral}
"""
    }
    
    return '\n'.join([descriptions.get(dim, '') for dim in update_dimensions])
