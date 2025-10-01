"""
修仙世界观生成提示词（简洁版）
"""

def get_world_generation_prompt(core_concept: str, additional_requirements: str = "无特殊要求") -> str:
    """
    获取世界观生成prompt
    
    Args:
        core_concept: 核心概念
        additional_requirements: 额外要求
    
    Returns:
        格式化的prompt字符串
    """
    return f"""# 修仙世界观生成提示词（简洁版）

## 核心功能
基于用户提供的核心概念，快速生成完整自洽的修仙世界观。

## 输入参数
- **核心概念**：{core_concept}
- **创新程度**：中（默认）
- **复杂度**：标准（默认）
- **额外要求**：{additional_requirements}

## 生成维度

### 1. 基础框架
- 世界名称与核心概念
- 基本法则与运行规律
- 位面结构与空间特性

### 2. 力量体系
- 修炼境界（6-8个主要境界）
- 能量属性与功法类型
- 修炼限制与代价

### 3. 世界环境
- 主要地理区域（3-4个）
- 重要地点与特殊秘境
- 资源分布与灵气特性

### 4. 社会组织
- 主要势力（3-4个组织）
- 社会结构与等级制度
- 经济体系与交易方式

### 5. 历史文化
- 关键历史事件（2-3个）
- 文化特色与生活方式
- 当前冲突与发展趋势

## 输出要求
- 完整的JSON格式
- 每个维度至少3个具体条目
- 确保逻辑自洽
- 避免传统俗套设定
- 类型不能为空或未知

## 输出格式

请严格按照以下JSON结构输出，注意每个数组元素都必须是完整的对象，不能是简单字符串：

{{
  "name": "世界观名称",
  "description": "世界观详细描述",
  "core_concept": "核心概念描述",
  "power_system": {{
    "cultivation_realms": [
      {{
        "name": "境界名称",
        "level": "境界等级",
        "description": "境界描述",
        "requirements": "突破要求"
      }}
    ],
    "energy_types": [
      {{
        "name": "能量类型",
        "rarity": "稀有度",
        "description": "特性描述"
      }}
    ],
    "technique_categories": [
      {{
        "name": "功法类别",
        "description": "类别描述",
        "difficulty": "修炼难度"
      }}
    ]
  }},
  "geography": {{
    "main_regions": [
      {{
        "name": "区域名称",
        "type": "区域类型",
        "description": "区域描述",
        "resources": ["资源1", "资源2"],
        "special_features": "特色描述"
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
  }},
  "society": {{
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
  }},
  "history_culture": {{
    "historical_events": [
      {{
        "name": "事件名称",
        "time_period": "时间范围",
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
}}

## 重要提醒

1. **确保逻辑自洽**：所有设定必须相互兼容，无矛盾
2. **避免传统俗套**：在传统基础上加入独特创意
3. **内容丰富完整**：每个数组字段至少包含3-5个元素
4. **描述具体详细**：所有描述字段都要有具体内容，不能为空
5. **JSON格式正确**：确保所有字段都有值且不能为暂无设定，类型不能为空或未知
6. **创新平衡**：既有传统修仙元素，又有独特创新点
7. **对象数组格式**：每个数组元素必须是完整的对象，包含所有指定字段，不要返回简单的字符串数组

请充分发挥创意，生成一个独特而丰富的修仙世界观！
"""