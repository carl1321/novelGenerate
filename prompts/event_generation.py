"""
统一的事件生成Prompt模板 - 融合普通模式和增强模式
"""
from typing import Dict, List, Any, Optional

def get_event_generation_prompt(
    # 世界观信息
    core_concept: str,
    world_description: str,
    geography_setting: str,
    
    # 角色清单
    characters: List[Dict[str, Any]],
    
    # 故事信息
    story_tone: str,
    narrative_structure: str,
    title: str,
    
    # 生成参数
    importance_distribution: Dict[str, int],
    event_requirements: str = "",
    
    # 幕次选择
    selected_act: Optional[Dict[str, Any]] = None
) -> str:
    """获取事件生成prompt（优化版本）"""
    return get_enhanced_event_generation_prompt(
        core_concept, world_description, geography_setting,
        characters, story_tone, narrative_structure, title,
        importance_distribution, event_requirements, selected_act
    )

def get_enhanced_event_generation_prompt(
    # 世界观信息（优化版）
    core_concept: str,
    world_description: str,
    geography_setting: str,
    
    # 角色清单（优化版）
    characters: List[Dict[str, Any]],
    
    # 故事信息
    story_tone: str,
    narrative_structure: str,
    title: str,
    
    # 生成参数
    importance_distribution: Dict[str, int],
    event_requirements: str = "",
    
    # 幕次选择（新增）
    selected_act: Optional[Dict[str, Any]] = None
) -> str:
    """
    获取增强的事件生成prompt
    
    Args:
        core_concept: 世界观核心概念
        world_description: 世界观描述
        characters: 角色列表
        selected_act: 选中的幕次信息
        importance_distribution: 重要性分布 {"重大事件": 3, "重要事件": 5, "普通事件": 10, "特殊事件": 2}
        event_requirements: 事件要求
        
    Returns:
        格式化的prompt字符串
    """
    if selected_act:
        if isinstance(selected_act, dict):
            act_name = selected_act.get('act_name', '未知幕次')
            core_mission = selected_act.get('core_mission', '无任务')
            daily_events = selected_act.get('daily_events', '无日常事件')
            conflict_events = selected_act.get('conflict_events', '无冲突事件')
            special_events = selected_act.get('special_events', '无特殊事件')
            major_events = selected_act.get('major_events', '无重大事件')
    
    # 背景信息
    world_info = f"""
**核心概念**: {core_concept}
**世界观描述**: {world_description}
**幕次名称**: {act_name}
**核心任务**: {core_mission}

## 幕次事件类型描述（需要细化和扩充）
**重大事件**: {major_events}
**冲突事件**: {conflict_events}
**特殊事件**: {special_events}
**日常事件**: {daily_events}

**重要说明**: 请根据上述幕次中的各种事件类型描述，生成具体的事件来细化和扩充这些事件类型。每个生成的事件都应该是对幕次事件类型的具体化和详细化。
"""

    # 构建角色信息
    characters_info = ""
    if characters:
        character_details = []
        
        for i, char in enumerate(characters[:12]):  # 最多12个角色
            try:
                if isinstance(char, dict):
                    name = char.get('name', '未知角色')
                    role_type_raw = char.get('role_type', '未知')
                    personality = char.get('personality_traits', '未知')
                    background = char.get('background', '暂无背景故事')
                else:
                    # 处理对象类型
                    name = getattr(char, 'name', '未知角色')
                    role_type_raw = getattr(char, 'role_type', '未知')
                    personality = getattr(char, 'personality_traits', '未知')
                    background = getattr(char, 'background', '暂无背景故事')

                # 统一处理role_type
                if hasattr(role_type_raw, 'value'):
                    role_type = role_type_raw.value
                elif hasattr(role_type_raw, '__str__'):
                    role_type = str(role_type_raw)
                else:
                    role_type = role_type_raw
                
                char_detail = f"""{name}
角色类型: {role_type} 
性格特征: {personality[:200]}{'...' if len(personality) > 200 else ''}
背景信息: {background[:200]}{'...' if len(background) > 200 else ''}
"""
                
                character_details.append(char_detail)
                
            except Exception as e:
                print(f"❌ 处理角色失败: {e}")
                continue
        
        characters_info = "\n\n".join(character_details)
    
    # 构建重要性分布说明
    distribution_text = ""
    for importance, count in importance_distribution.items():
        distribution_text += f"- {importance}: {count}个\n"
    
    prompt = f"""你是一位资深的小说事件设计师，专门负责根据剧情大纲幕次中的事件类型描述来细化和扩充事件。

## 背景设定
{world_info}

## 关键角色
{characters_info}

## 事件说明
{event_requirements}

## 生成任务
**重要性分布**: {distribution_text}
**重要提醒**: 请根据幕次中的各种事件类型描述，生成具体的事件来细化和扩充这些事件类型。

## 生成要求

1. **事件细化和扩充原则**：
   - 根据幕次中的事件类型描述，生成具体的事件来细化和扩充
   - 每个事件都应该是对幕次事件类型的具体化和详细化
   - 每个生成的事件都应该是对幕次事件类型的具体化和详细化

2. **严格按照重要性分布生成事件数量，严格按照幕次信息的设定和事件说明生成事件内容**

3. **主角参与度要求**：
   - **重大、冲突、特殊事件**：主角必须作为主人翁，是事件的核心推动者和主要参与者
   - **日常事件**：主角可以参与，但不强制要求主导地位
   - **主角视角**：从主角的视角描述事件，体现主角的感受和反应

4. **事件描述必须简洁明了且符合逻辑**：
   - 事件标题要简洁有力，体现事件核心
   - 事件描述要简洁明了，不超过200字
   - 要包含事件的起因、经过、结果，逻辑链条要清晰
   - **重大事件**：推动主线剧情，影响整个故事走向
   - **冲突事件**：发展角色关系，展现人物性格
   - **特殊事件**：构建奇遇、外挂等，推动主角成长
   - **日常事件**：展现日常生活

## 输出格式
请严格按照以下JSON格式输出，不要添加任何其他文字或解释：

{{
  "events": [
    {{
      "title": "事件标题（简洁有力，体现事件核心）",
      "event_type": "事件类型（重大事件、冲突事件、特殊事件、日常事件）",
      "description": "主角在特定情境下遇到挑战，通过自己的努力和智慧解决问题，获得成长或重要资源。事件过程简洁明了，重点突出主角的作用和成长。",
      "outcome": "事件结果（简洁描述：1）对主角的具体影响；2）对剧情发展的作用；3）为后续埋下的伏笔）"
    }}
  ]
}}

"""
    return prompt


