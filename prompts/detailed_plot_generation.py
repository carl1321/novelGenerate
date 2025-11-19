"""
详细剧情生成提示词管理 - 简化版（基于事件驱动）
"""
from typing import Dict, List, Any, Optional


def get_detailed_plot_generation_prompt(
    chapter_outline: Any,
    plot_outline: Any, 
    world_view: Dict[str, Any],
    characters: List[Dict[str, Any]],
    events: List[Dict[str, Any]] = None,
    additional_requirements: Optional[str] = None
) -> str:
    """获取详细剧情生成提示词 - 简化版（基于事件驱动）"""
    
    # 格式化角色信息
    characters_info = ""
    if characters:
        character_details = []
        for char in characters[:8]:  # 限制角色数量但提供更多信息
            name = char.get('name', '未知角色')
            age = char.get('age', '未知')
            gender = char.get('gender', '未知')
            role_type = char.get('role_type', '未知')
            cultivation_level = char.get('cultivation_level', '无境界')
            element_type = char.get('element_type', '无属性')
            background = char.get('background', '暂无背景故事')
            current_location = char.get('current_location', '未知位置')
            current_region = char.get('current_region', '')
            
            # 组合地理位置信息
            location_info = ""
            if current_region and current_location:
                location_info = f"{current_region} - {current_location}"
            elif current_region:
                location_info = current_region
            elif current_location:
                location_info = current_location
            else:
                location_info = "未知位置"
            
            # 获取性格特质
            personality_traits = char.get('personality_traits', [])
            personality_str = ""
            if isinstance(personality_traits, list):
                personality_texts = []
                for trait in personality_traits[:3]:  # 限制性格特质数量
                    if isinstance(trait, dict):
                        trait_desc = trait.get('description', f"{trait.get('name', '特质')}")
                        personality_texts.append(trait_desc)
                    else:
                        personality_texts.append(str(trait))
                personality_str = "、".join(personality_texts)
            
            # 获取目标
            goals = char.get('goals', [])
            goals_str = ""
            if isinstance(goals, list):
                goal_texts = []
                for goal in goals[:2]:  # 限制目标数量
                    if isinstance(goal, dict):
                        goal_desc = goal.get('description', f"{goal.get('name', '目标')}")
                        goal_texts.append(goal_desc)
                    else:
                        goal_texts.append(str(goal))
                goals_str = "、".join(goal_texts)
            
            # 获取关系信息
            relationships = char.get('relationships', {})
            relationships_str = ""
            if isinstance(relationships, dict) and relationships:
                # 取前3个关系
                rel_list = list(relationships.items())[:3]
                rel_texts = [f"{rel_char}: {rel_desc}" if isinstance(rel_desc, str) else f"{rel_char}: {str(rel_desc)}" 
                           for rel_char, rel_desc in rel_list]
                relationships_str = "、".join(rel_texts)
            
            # 构建角色详情
            char_detail = f"""【{name}】
基本信息: {age}岁{gender}, 角色类型: {role_type}
修炼境界: {cultivation_level}, 灵根属性: {element_type}
当前位置: {location_info}
背景故事: {background[:100]}{'...' if len(background) > 100 else ''}"""
            
            if personality_str:
                char_detail += f"\n性格特质: {personality_str}"
            if goals_str:
                char_detail += f"\n当前目标: {goals_str}"
            if relationships_str:
                char_detail += f"\n重要关系: {relationships_str}"
            
            character_details.append(char_detail)
        
        characters_info = "\n\n".join(character_details)
    
    # 格式化世界观信息
    world_info = f"""
世界观名称: {world_view.get('name', '未知世界观')}
世界观描述: {world_view.get('description', '暂无描述')}
核心概念: {world_view.get('core_concept', '无核心概念')}
力量体系: {world_view.get('power_system', {}).get('name', '未知力量体系') if isinstance(world_view.get('power_system'), dict) else str(world_view.get('power_system', '未知力量体系'))}
地理设定: {str(world_view.get('geography', {}))[:200]}...
"""
    
    # 格式化剧情大纲信息
    plot_info = f"""
剧情大纲: {getattr(plot_outline, 'title', '未知剧情')}
剧情描述: {getattr(plot_outline, 'description', '暂无描述')}
主题: {getattr(plot_outline, 'theme', '未知主题')}
基调: {getattr(plot_outline, 'story_tone', '未知基调')}
"""
    
    # 格式化章节大纲信息 - 简化版
    chapter_info = f"""
章节标题: {getattr(chapter_outline, 'title', '未知章节')}
章节概要: {getattr(chapter_outline, 'chapter_summary', '暂无概要')}
所属幕次: {getattr(chapter_outline, 'act_belonging', '未知')}
剧情功能: {getattr(chapter_outline, 'plot_function', '未知')}
预计字数: {getattr(chapter_outline, 'estimated_word_count', '未知')}
冲突发展: {getattr(chapter_outline, 'conflict_development', '暂无描述')}
写作指导: {getattr(chapter_outline, 'writing_notes', '暂无指导')}
"""
    
    # 格式化关键场景信息 - 简化版
    scenes_info = ""
    scenes = getattr(chapter_outline, 'key_scenes', [])
    if scenes:
        scenes_info = "关键场景设置：\n"
        for scene in scenes:
            scene_title = getattr(scene, 'title', '未知场景')
            scene_desc = getattr(scene, 'description', '暂无描述')
            scene_location = getattr(scene, 'location', '未知地点')
            scene_purpose = getattr(scene, 'purpose', '未知目的')
            characters_present = getattr(scene, 'characters_present', [])
            related_events = getattr(scene, 'related_events', [])
            
            scenes_info += f"""
- {scene_title}:
  地点: {scene_location}
  描述: {scene_desc}
  目的: {scene_purpose}
  在场角色: {', '.join(characters_present) if characters_present else '无'}
  关联事件: {', '.join(related_events) if related_events else '无'}
"""
    
    # 格式化事件信息 - 新增
    events_info = ""
    if events:
        events_info = "相关事件信息：\n"
        for i, event in enumerate(events[:10], 1):  # 限制事件数量
            event_title = event.get('title', '未知事件')
            event_desc = event.get('description', '暂无描述')
            event_type = event.get('event_type', '未知类型')
            event_outcome = event.get('outcome', '暂无结果')
            event_importance = event.get('importance', '普通')
            
            events_info += f"""
{i}. {event_title} ({event_type}, {event_importance}):
   描述: {event_desc[:150]}{'...' if len(event_desc) > 150 else ''}
   结果: {event_outcome[:150]}{'...' if len(event_outcome) > 150 else ''}
"""
    
    prompt = f"""你是一个专业的小说创作助手。请基于以下信息生成详细的章节剧情内容：

重要提醒：生成的剧情内容必须达到5000字以上，这是硬性要求！

{world_info}

{plot_info}

{chapter_info}

{scenes_info}

{events_info}

角色信息：
{characters_info}

额外要求：
{additional_requirements or "无特殊要求"}

请生成详细的章节剧情内容，要求：
1. 内容要生动具体，包含对话、动作和场景描述
2. 字数必须达到5000字以上，不得少于5000字
3. 严格按照关键场景设置来构建剧情结构
4. 要体现章节的剧情功能：{getattr(chapter_outline, 'plot_function', '未知')}
5. 要体现冲突发展：{getattr(chapter_outline, 'conflict_development', '暂无描述')}
6. 要遵循写作指导：{getattr(chapter_outline, 'writing_notes', '暂无指导')}
7. 语言要流畅自然，符合小说写作风格
8. 要符合世界观设定，保持逻辑一致性
9. 要推进剧情发展，但需要平缓，不能过快或偏离主线
10. **严格按照角色的基本信息、性格特质、当前目标和关系来塑造角色**
11. **角色的对话和行为必须与其性格特质完全匹配**
12. **角色的修炼境界和修炼属性要影响其战斗能力和表现**
13. **尊重角色的背景故事，角色行为要与其过往经历一致**
14. **重要：必须基于关键场景设置来构建剧情，每个场景都要得到充分展开**
15. **重要：场景中的关联事件要在合适的时机自然引入，不要强行拼凑**
16. **重要：场景的目的和在场角色要得到充分体现**
17. **重要：事件信息中提到的每个相关事件都要在剧情中得到合理体现**

请直接输出详细的剧情内容，不要添加任何解释或格式标记。

再次强调：字数必须达到5000字以上！"""

    return prompt


def get_detailed_plot_analysis_prompt(content: str) -> str:
    """获取详细剧情分析提示词"""
    return f"""请分析以下详细剧情内容的质量：

{content}

请从以下维度进行分析：
1. 情节逻辑性 - 剧情发展是否合理
2. 角色一致性 - 角色行为是否符合设定
3. 世界观一致性 - 是否符合世界观设定
4. 文笔质量 - 语言表达是否流畅
5. 情感渲染 - 是否能有效传达情感
6. 伏笔运用 - 是否合理运用了伏笔
7. 冲突设置 - 是否有足够的戏剧冲突
8. 节奏控制 - 情节节奏是否合适

请给出1-10分的评分，并提供具体的改进建议。"""


def get_detailed_plot_revision_prompt(
    original_content: str,
    revision_requirements: str,
    analysis_feedback: str = None
) -> str:
    """获取详细剧情修订提示词"""
    feedback_section = f"\n\n分析反馈：\n{analysis_feedback}" if analysis_feedback else ""
    
    return f"""请根据以下要求修订详细剧情内容：

原始内容：
{original_content}

修订要求：
{revision_requirements}
{feedback_section}

请保持原有内容的核心情节和角色设定，只对需要修订的部分进行调整。修订后的内容应该：
1. 保持原有的故事逻辑
2. 符合修订要求
3. 保持文笔质量
4. 保持字数基本不变

请直接输出修订后的剧情内容："""


def get_detailed_plot_summary_prompt(content: str) -> str:
    """获取详细剧情摘要提示词"""
    return f"""请为以下详细剧情内容生成简洁的摘要：

{content}

摘要要求：
1. 控制在200字以内
2. 突出主要情节和关键转折
3. 包含主要角色和重要事件
4. 保持客观描述，不添加主观评价

请直接输出摘要内容："""
