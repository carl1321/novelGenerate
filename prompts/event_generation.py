"""
事件生成Prompt模板
"""

def get_event_generation_prompt(event_type: str, world_name: str = "", world_description: str = "",
                              power_system: str = "", characters_info: str = "",
                              event_requirements: str = "") -> str:
    """
    获取事件生成prompt
    
    Args:
        event_type: 事件类型
        world_name: 世界观名称
        world_description: 世界观描述
        power_system: 力量体系
        characters_info: 角色信息
        event_requirements: 事件要求
    
    Returns:
        格式化的prompt字符串
    """
    return f"""你是一个专业的事件设计师。请基于以下信息生成一个{event_type}：

世界观信息：
- 名称：{world_name}
- 描述：{world_description}
- 力量体系：{power_system}

角色信息：
{characters_info}

事件要求：
{event_requirements}

请严格按照以下JSON格式输出，不要添加任何其他文字或解释：

{{
  "title": "事件标题",
  "description": "事件描述（200字以内）",
  "event_type": "{event_type}",
  "importance": "中",
  "category": "剧情推动",
  "setting": "事件发生地点",
  "participants": ["角色1", "角色2"],
  "duration": "持续时间",
  "outcome": "事件结果",
  "plot_impact": "对剧情的影响",
  "character_impact": {{
    "角色1": "影响描述",
    "角色2": "影响描述"
  }},
  "foreshadowing_elements": ["伏笔1", "伏笔2"],
  "prerequisites": ["条件1", "条件2"],
  "consequences": ["影响1", "影响2"],
  "tags": ["标签1", "标签2"],
  "sequence_order": 1
}}"""
