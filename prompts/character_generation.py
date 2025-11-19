"""
角色生成Prompt模板
"""

def get_character_generation_prompt(world_view: dict, character_requirements: str) -> str:
    """
    获取角色生成prompt
    
    Args:
        world_view: 世界观数据字典，包含完整的世界观信息
        character_requirements: 角色要求
    
    Returns:
        格式化的prompt字符串
    """
    
    # 提取世界观信息
    world_name = world_view.get('name', '未知世界观')
    world_description = world_view.get('description', '无描述')
    core_concept = world_view.get('core_concept', '无核心概念')
    
    # 提取力量体系信息
    power_system_info = world_view.get('power_system', {})
    cultivation_realms = power_system_info.get('cultivation_realms', [])
    power_system_text = ""
    if cultivation_realms:
        power_system_text = "修炼境界体系：\n"
        for realm in cultivation_realms:
            power_system_text += f"- {realm.get('name', '未知境界')}：{realm.get('description', '无描述')}\n"
    
    # 提取地理势力信息
    geography_info = world_view.get('geography', {})
    main_regions = geography_info.get('main_regions', [])
    geography_text = ""
    if main_regions:
        geography_text = "地理势力分布：\n"
        for region in main_regions:
            geography_text += f"- {region.get('name', '未知区域')}：{region.get('description', '无描述')}\n"
            forces = region.get('forces', [])
            if forces:
                geography_text += "  主要势力：\n"
                for force in forces:
                    geography_text += f"    * {force.get('name', '未知势力')}（{force.get('type', '未知类型')}）：{force.get('description', '无描述')}\n"
    
    return f"""你是一个专业的修仙小说角色设计师。请根据给定的世界观和角色描述，生成一个完整的角色。

## 世界观信息
- **世界观名称**：{world_name}
- **世界观描述**：{world_description}
- **核心概念**：{core_concept}

{power_system_text}

{geography_text}

## 角色要求
{character_requirements}

## 生成要求

**核心原则：无论角色描述是否包含基本信息，都必须生成完整的角色数据！**

**重要说明：**
- 如果角色描述中没有明确指定姓名、年龄、性别等基本信息，请根据角色描述的内容、性格特点、能力特征等自行推断和生成
- 例如：描述"一个年轻的剑客" → 推断为男性，年龄18-25岁，生成符合剑客身份的名字
- 例如：描述"擅长快剑，性格孤傲" → 推断为男性，年龄20-30岁，生成体现孤傲特点的名字
- 例如：描述"一个神秘的女子" → 推断为女性，年龄25-35岁，生成神秘感的名字

**角色类型要求：**
- **必须严格按照用户指定的角色类型生成角色！**
- 如果用户指定了角色类型，必须使用该类型，不要自行更改！
- 如果用户未指定角色类型，才从以下类型中选择：主角、配角、正义伙伴、反派、情人、其他、特殊

**世界观适配要求：**
- 角色的修炼境界必须符合世界观中的修炼体系
- 角色的当前位置必须符合世界观中的地理分布
- 角色的所属组织必须符合世界观中的势力分布
- 角色的背景故事必须与世界观的核心概念相符

**个人关系视角要求：**
- 必须生成简短的关系描述，格式为："关系类型：角色姓名，关系描述"
- 包含3-5个重要关系，如家人、朋友、师父、敌人等
- 每个关系描述控制在8-15字以内，使用简洁准确的词汇
- 关系要符合角色的身份和背景设定
- 示例格式："女儿：柳青儿，疼爱有加；徒弟：林凡，悉心教导；师父：青云长老，敬重如父；仇敌：黑狼帮主，势不两立"
- 其他示例："师兄：张明，情同手足；师妹：小雅，暗生情愫；掌门：玄机真人，敬畏有加；宿敌：血魔，不死不休"

请按照以下字段生成完整的角色信息：

### 基础信息（必须完整）
- **name**：根据角色描述生成符合修仙小说风格的名字
- **age**：根据角色描述设定合适的年龄
- **gender**：根据角色描述确定性别
- **role_type**：必须使用用户指定的角色类型
- **cultivation_level**：根据世界观中的修炼体系设定合适的修炼等级
- **element_type**：根据角色特点设定灵根属性
- **background**：根据角色背景和世界观设定生成详细的背景故事
- **current_location**：根据世界观中的地理分布设定当前位置
- **organization_id**：根据世界观中的势力分布设定所属组织

### 性格和目标（必须完整）
- **personality_traits**：根据角色描述生成性格特质描述（文本格式）
- **main_goals**：根据角色背景和世界观设定生成主要目标描述
- **short_term_goals**：根据角色背景和世界观设定生成短期目标描述

### 能力和关系（必须完整）
- **techniques**：根据角色描述和世界观设定生成2-3个主要技能（对象数组格式）
- **weaknesses**：根据角色特点生成弱点和限制描述（文本格式）

### 外貌和经历（必须完整）
- **appearance**：根据角色身份、性格生成外貌描述
- **turning_point**：根据角色背景和世界观设定生成重要转折点
- **relationship_text**：生成个人关系视角描述，格式为简短的关系描述，如："女儿：柳青儿，疼爱有加；徒弟：林凡，悉心教导；师父：青云长老，敬重如父；仇敌：黑狼帮主，势不两立"

## 输出格式

**严格按照以下JSON格式输出，所有字段都必须有具体值：**

{{
  "name": "角色姓名",
  "age": 年龄,
  "gender": "性别",
  "role_type": "角色类型",
  "cultivation_level": "修炼境界（必须符合世界观中的修炼体系）",
  "element_type": "灵根属性",
  "background": "背景故事（必须与世界观设定相符）",
  "current_location": "当前位置（必须符合世界观中的地理分布）",
  "organization_id": "所属组织（必须符合世界观中的势力分布）",
  "personality_traits": "性格特质描述，如：勇敢无畏，正义感强，但有时过于冲动",
  "main_goals": "主要目标描述，如：成为绝世强者，保护重要的人",
  "short_term_goals": "短期目标描述，如：突破到金丹境，学会新的剑法",
  "techniques": [
    {{"name": "技能名称", "level": "技能等级", "description": "技能描述"}},
    {{"name": "技能名称", "level": "技能等级", "description": "技能描述"}}
  ],
  "weaknesses": "弱点和限制描述，如：缺乏实战经验，容易冲动",
  "appearance": "外貌描述",
  "turning_point": "重要转折点",
  "relationship_text": "个人关系视角，如：女儿：柳青儿，疼爱有加；徒弟：林凡，悉心教导；师父：青云长老，敬重如父；仇敌：黑狼帮主，势不两立",
  "values": "价值观和信念描述，如：坚持正义，保护弱小，追求武道极致"
}}

## 重要提醒

**必须生成完整的内容，所有字段都要有具体值！**

**关键要求：**
1. **角色类型严格匹配**：必须使用用户指定的角色类型，不能自行更改！
2. **基本信息推断**：即使角色描述中没有明确指定姓名、年龄、性别，也必须根据描述内容进行合理推断和生成
3. **世界观适配**：角色的所有设定都必须与提供的世界观信息完全相符
4. **数据完整性**：每个字段都必须有值，不能为空
5. **格式正确性**：确保JSON格式完全正确，所有字段都有具体值
6. **内容质量**：角色设定要具体详细，为后续创作提供丰富素材
7. **关系视角完整性**：必须生成具体的关系描述，不能为空或"暂无"

**禁止行为：**
- 不要出现空字段或"暂无"、"待定"、"待补充"等占位符
- 不要返回不完整的JSON结构
- 不要因为信息不足而省略任何字段
- 不要生成与世界观设定不符的角色信息
- 不要生成空的关系视角或"暂无关系"等占位符

**补充原则：**
- 如果角色描述信息不足，请根据修仙小说的常见设定和世界观信息进行合理补充
- 根据角色的身份、能力、性格特点等推断缺失的信息
- 确保生成的角色完全符合提供的世界观设定"""


def get_batch_character_generation_prompt(world_view: dict, character_description: str, 
                                        character_count: int, role_types: list) -> str:
    """
    获取批量角色生成prompt
    
    Args:
        world_view: 世界观数据字典，包含完整的世界观信息
        character_description: 角色描述（一句话）
        character_count: 角色数量
        role_types: 角色类型列表
    
    Returns:
        格式化的prompt字符串
    """
    
    # 提取世界观信息
    world_name = world_view.get('name', '未知世界观')
    world_description = world_view.get('description', '无描述')
    core_concept = world_view.get('core_concept', '无核心概念')
    
    # 提取力量体系信息
    power_system_info = world_view.get('power_system', {})
    cultivation_realms = power_system_info.get('cultivation_realms', [])
    power_system_text = ""
    if cultivation_realms:
        power_system_text = "修炼境界体系：\n"
        for realm in cultivation_realms:
            power_system_text += f"- {realm.get('name', '未知境界')}：{realm.get('description', '无描述')}\n"
    
    # 提取地理势力信息
    geography_info = world_view.get('geography', {})
    main_regions = geography_info.get('main_regions', [])
    geography_text = ""
    if main_regions:
        geography_text = "地理势力分布：\n"
        for region in main_regions:
            geography_text += f"- {region.get('name', '未知区域')}：{region.get('description', '无描述')}\n"
            forces = region.get('forces', [])
            if forces:
                geography_text += "  主要势力：\n"
                for force in forces:
                    geography_text += f"    * {force.get('name', '未知势力')}（{force.get('type', '未知类型')}）：{force.get('description', '无描述')}\n"
    
    role_types_str = "、".join(role_types)
    
    return f"""你是一个专业的修仙小说角色设计师。请根据给定的世界观和角色描述，批量生成{character_count}个符合故事发展的角色。

## 世界观信息
- **世界观名称**：{world_name}
- **世界观描述**：{world_description}
- **核心概念**：{core_concept}

{power_system_text}

{geography_text}

## 角色要求
- **角色描述**：{character_description}
- **角色数量**：{character_count}个
- **角色类型**：{role_types_str}

## 生成要求

**核心原则：无论角色描述是否包含基本信息，都必须生成完整的角色数据！**

**重要说明：**
- 如果角色描述中没有明确指定姓名、年龄、性别等基本信息，请根据角色描述的内容、性格特点、能力特征等自行推断和生成
- 例如：描述"一个年轻的剑客" → 推断为男性，年龄18-25岁，生成符合剑客身份的名字
- 例如：描述"擅长快剑，性格孤傲" → 推断为男性，年龄20-30岁，生成体现孤傲特点的名字
- 例如：描述"一个神秘的女子" → 推断为女性，年龄25-35岁，生成神秘感的名字

**角色类型要求：**
- **必须严格按照用户指定的角色类型生成角色！**
- 如果用户指定了角色类型，必须使用该类型，不要自行更改！
- 如果用户未指定角色类型，才从以下类型中选择：主角、配角、正义伙伴、反派、情人、其他、特殊

**世界观适配要求：**
- 角色的修炼境界必须符合世界观中的修炼体系
- 角色的当前位置必须符合世界观中的地理分布
- 角色的所属组织必须符合世界观中的势力分布
- 角色的背景故事必须与世界观的核心概念相符

**个人关系视角要求：**
- 必须生成简短的关系描述，格式为："关系类型：角色姓名，关系描述"
- 包含3-5个重要关系，如家人、朋友、师父、敌人等
- 每个关系描述控制在8-15字以内，使用简洁准确的词汇
- 关系要符合角色的身份和背景设定
- 示例格式："女儿：柳青儿，疼爱有加；徒弟：林凡，悉心教导；仇敌：黑狼帮主，势不两立"
- 其他示例："师兄：张明，情同手足；师妹：小雅，暗生情愫；师傅：玄机真人，敬畏有加；宿敌：血魔，不死不休"

请按照以下字段生成完整的角色信息：

### 基础信息（必须完整）
- **name**：根据角色描述生成符合修仙小说风格的名字
- **age**：根据角色描述设定合适的年龄
- **gender**：根据角色描述确定性别
- **role_type**：必须使用用户指定的角色类型
- **cultivation_level**：根据世界观中的修炼体系设定合适的修炼等级
- **element_type**：根据角色特点设定灵根属性
- **background**：根据角色背景和世界观设定生成详细的背景故事
- **current_location**：根据世界观中的地理分布设定当前位置
- **organization_id**：根据世界观中的势力分布设定所属组织

### 性格和目标（必须完整）
- **personality_traits**：根据角色描述生成性格特质描述（文本格式）
- **main_goals**：根据角色背景和世界观设定生成主要目标描述
- **short_term_goals**：根据角色背景和世界观设定生成短期目标描述

### 能力和关系（必须完整）
- **techniques**：根据角色描述和世界观设定生成2-3个主要技能（对象数组格式）
- **weaknesses**：根据角色特点生成弱点和限制描述（文本格式）

### 外貌和经历（必须完整）
- **appearance**：根据角色身份、性格生成外貌描述
- **turning_point**：根据角色背景和世界观设定生成重要转折点
- **relationship_text**：生成个人关系视角描述，格式为简短的关系描述，如："女儿：柳青儿，疼爱有加；徒弟：林凡，悉心教导；师父：青云长老，敬重如父；仇敌：黑狼帮主，势不两立"

## 输出格式

**严格按照以下JSON格式输出：**
{{
  "characters": [
    {{
      "name": "角色姓名",
      "age": 年龄,
      "gender": "性别",
      "role_type": "角色类型",
      "cultivation_level": "修炼境界（必须符合世界观中的修炼体系）",
      "element_type": "灵根属性",
      "background": "背景故事（必须与世界观设定相符）",
      "current_location": "当前位置（必须符合世界观中的地理分布）",
      "organization_id": "所属组织（必须符合世界观中的势力分布）",
      "personality_traits": "性格特质描述",
      "main_goals": "主要目标描述",
      "short_term_goals": "短期目标描述",
      "techniques": [
        {{"name": "技能名称", "level": "技能等级", "description": "技能描述"}},
        {{"name": "技能名称", "level": "技能等级", "description": "技能描述"}}
      ],
      "weaknesses": "弱点和限制描述",
      "appearance": "外貌描述",
      "turning_point": "重要转折点",
      "relationship_text": "个人关系视角，如：女儿：柳青儿，疼爱有加；徒弟：林凡，悉心教导；师父：青云长老，敬重如父；仇敌：黑狼帮主，势不两立",
      "values": "价值观和信念描述"
    }}
  ]
}}

## 注意事项

1. 必须生成{character_count}个角色，不能多也不能少
2. 每个角色都要符合世界观设定
3. 角色类型要合理分配，不能全部都是同一种类型
4. 角色之间要有差异化，避免重复
5. 为每个角色设计合理的关系网络
6. 确保JSON格式完全正确
7. 角色的所有设定都必须与提供的世界观信息完全相符

## 重要提醒

**必须生成完整的内容，所有字段都要有具体值！**
- 确保JSON格式正确
- 不要出现空字段或"暂无"等占位符
- 角色设定要具体详细，为后续创作提供丰富素材
- 严格按照要求的数量生成角色
- 确保生成的角色完全符合提供的世界观设定"""
