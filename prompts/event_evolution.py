"""
事件进化prompt模板
用于根据评分结果优化事件，修复识别出的问题
"""

def get_event_evolution_prompt(event, score, characters, world_info, custom_description=""):
    """
    生成事件进化prompt
    
    Args:
        event: 原始事件对象
        score: 事件评分结果
        characters: 角色列表
        world_info: 世界观信息
        custom_description: 用户自定义的进化描述
    
    Returns:
        str: 进化prompt
    """
  
    
    # 格式化世界观信息
    world_text = ""
    if isinstance(world_info, dict):
        world_text = f"""
核心概念: {world_info.get('core_concept', '未知')}
世界观描述: {world_info.get('world_description', '未知')}
"""
    else:
        world_text = str(world_info)
    
    # 生成改进建议
    improvement_suggestions = []
    
    # 根据评分等级生成不同的优化建议
    if score.protagonist_involvement < 6:
        improvement_suggestions.append("大幅增强主角在事件中的作用，让主角成为事件的推动者或核心参与者")
    elif score.protagonist_involvement < 8:
        improvement_suggestions.append("进一步增强主角在事件中的作用，让主角的决策和行动更加突出")
    else:
        improvement_suggestions.append("保持主角的核心地位，同时丰富主角的内心活动和成长细节")
    
    if score.plot_coherence < 6:
        improvement_suggestions.append("大幅优化事件逻辑，确保因果关系清晰，情节发展合理")
    elif score.plot_coherence < 8:
        improvement_suggestions.append("进一步优化事件逻辑，增强情节的连贯性和合理性")
    else:
        improvement_suggestions.append("保持逻辑严密的同时，增加更多细节和伏笔")
    
    if score.writing_quality < 6:
        improvement_suggestions.append("大幅提升文笔质量，增强语言表达的生动性，丰富描写细节，让对话更自然流畅")
    elif score.writing_quality < 8:
        improvement_suggestions.append("进一步提升文笔质量，增强描写的细腻度和语言的感染力")
    else:
        improvement_suggestions.append("保持文笔质量的同时，增加更多文学技巧和修辞手法")
    
    if score.dramatic_tension < 6:
        improvement_suggestions.append("大幅提升戏剧张力，增加冲突和紧张感，让事件更有冲击力")
    elif score.dramatic_tension < 8:
        improvement_suggestions.append("进一步提升戏剧张力，增加悬念和转折")
    else:
        improvement_suggestions.append("保持戏剧张力的同时，增加更多情感层次和心理描写")
    
    if score.overall_quality < 6:
        improvement_suggestions.append("全面提升事件质量，综合考虑所有维度进行优化")
    elif score.overall_quality < 8:
        improvement_suggestions.append("进一步提升整体质量，让事件更加精彩")
    else:
        improvement_suggestions.append("在保持高质量的基础上，增加更多创新元素和独特亮点")
    
    improvement_text = "\n".join([f"- {suggestion}" for suggestion in improvement_suggestions])
    
    # 处理用户自定义描述
    custom_requirements = ""
    if custom_description and custom_description.strip():
        custom_requirements = f"""
**用户特别要求**：
{custom_description.strip()}

请特别注意用户的上述要求，在优化过程中优先考虑这些需求。
"""
    else:
        custom_requirements = "无特殊要求，请按照评分结果进行标准优化。"
    
    prompt = f"""你是一位专业的小说事件重写师，请根据评分结果对以下事件进行重写优化：

## 原始事件
**标题**: {event.title if hasattr(event, 'title') else '未知'}
**事件类型**: {event.event_type if hasattr(event, 'event_type') else '未知'}
**描述**: {event.description if hasattr(event, 'description') else '未知'}
**事件结果**: {event.outcome if hasattr(event, 'outcome') else '未知'}

## 评分结果
**主角参与度**: {score.protagonist_involvement}/10
**剧情逻辑性**: {score.plot_coherence}/10
**文笔质量**: {score.writing_quality}/10
**戏剧张力**: {score.dramatic_tension}/10
**综合质量**: {score.overall_quality}/10

## 评分反馈
{score.feedback}

## 优点
{chr(10).join([f"- {strength}" for strength in score.strengths])}

## 缺点
{chr(10).join([f"- {weakness}" for weakness in score.weaknesses])}

## 世界观设定
{world_text}

## 重写要求
请根据评分结果和反馈，对事件进行以下重写优化：

{improvement_text}

## 用户自定义进化要求
{custom_requirements}

## 重写原则
1. **保持核心情节**: 保留事件的基本框架和核心情节，但可以优化表达方式
2. **增强主角作用**: 让主角在事件中发挥更核心的作用，增加主角的决策和行动
3. **提升逻辑性**: 确保事件发展更加合理，因果关系更加清晰
4. **提升文笔质量**: 增强语言表达的生动性，让描述更简洁有力
5. **确保世界观一致**: 严格遵循世界观设定，不出现设定冲突
6. **提升戏剧张力**: 增加冲突和紧张感，让事件更有冲击力
7. **控制字数**: 事件描述不超过300字，简洁描述过程即可


## 重写方式
- **重写而非批评**: 直接提供优化后的版本，不要批评原版的问题
- **保持原有风格**: 维持事件的原有风格和基调
- **自然优化**: 让优化显得自然，不生硬
- **世界观一致**: 确保完全符合世界观设定

## 输出格式
请严格按照以下JSON格式输出重写后的事件：
{{
    "title": "重写后的事件标题",
    "event_type": "事件类型",
    "description": "重写后的事件描述（不超过300字），保持原有核心情节，但增强主角作用、提升逻辑性、提升文笔质量、确保世界观一致、提升戏剧张力",
    "outcome": "重写后的事件结果（简洁描述：1）对主角的具体影响；2）对剧情发展的作用；3）为后续埋下的伏笔）"
}}
"""
    
    return prompt
