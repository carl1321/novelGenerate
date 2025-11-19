"""
进化智能体Prompt模板
用于对详细剧情进行智能进化和优化
"""

def get_evolution_agent_prompt(content: str, evolution_type: str = "general") -> str:
    """
    获取进化智能体的prompt
    
    Args:
        content: 原始详细剧情内容
        evolution_type: 进化类型 (general, dialogue, action, description, conflict, character)
    
    Returns:
        格式化的prompt字符串
    """
    
    base_prompt = f"""
你是一位专业的网络小说编辑和剧情优化专家。请对以下详细剧情进行智能进化，提升其质量、可读性和吸引力。

原始剧情内容：
{content}

请从以下维度对剧情进行进化优化：

## 1. 戏剧张力强化 (Dramatic Tension)
- 增强事件的紧张刺激感，让读者无法放下
- 巧妙设置悬念，保持读者的期待感
- 优化冲突升级，让情节更加引人入胜
- 控制节奏，在紧张和舒缓之间找到平衡
- 增加"接下来会怎样"的期待感

## 2. 情感冲击增强 (Emotional Impact)
- 强化情感表达，引起读者强烈的情感波动
- 增加悲伤、喜悦、愤怒、恐惧等情感元素
- 让情感表达更加真实可信，增强读者共鸣
- 优化情感转折，让情感变化更加自然合理
- 控制情感强度，避免过度或不足

## 3. 角色塑造深化 (Character Development)
- 丰富角色内心活动和情感表达
- 增强角色对话的个性化特征
- 深化角色动机和性格层次
- 提升角色间的互动张力
- 让角色成长更加明显和合理

## 4. 主题深度提升 (Thematic Depth)
- 深化故事的核心主题，增加内涵
- 让主题表达更加自然，不刻意
- 增加能引发读者深度思考的内容
- 强化主题与情节的紧密结合
- 提升主题的现实意义和价值

## 5. 节奏与流畅度优化 (Pacing & Fluency)
- 优化事件节奏，让快慢更加适中
- 提升叙述的流畅度和自然度
- 优化段落转换，让过渡更加自然
- 增强语言表达的清晰度
- 提升整体阅读体验的舒适度

## 6. 新颖性与创意提升 (Originality & Creativity)
- 避免常见的套路和桥段
- 增加令人耳目一新的创意点
- 让情节设置更加独特
- 提升角色设定的新意
- 增强整体构思的创新性

请按照以下JSON格式返回进化结果：

```json
{{
    "evolution_type": "general",
    "original_content": "原始内容",
    "evolved_content": "进化后的内容",
    "improvements": {{
        "dramatic_tension": "戏剧张力方面的改进说明",
        "emotional_impact": "情感冲击方面的改进说明",
        "character_development": "角色塑造方面的改进说明",
        "thematic_depth": "主题深度方面的改进说明",
        "pacing_fluency": "节奏与流畅度方面的改进说明",
        "originality_creativity": "新颖性与创意方面的改进说明"
    }},
    "evolution_summary": "整体进化总结",
    "word_count_change": 0,
    "quality_score": 85.5,
    "evolution_notes": "进化过程中的重要说明和建议"
}}
```

请确保：
1. 保持原有情节的核心框架和主要事件
2. 进化后的内容更加生动、有趣、有吸引力
3. **字数要求：保持原文字数或适度增加（最多增加30%），不得大幅删减内容**
4. 保持与原文风格的一致性
5. 提供具体的改进说明，便于理解优化思路
6. **重要：进化是优化和增强，不是删减和压缩**
"""

    # 根据进化类型调整prompt
    if evolution_type == "dialogue":
        base_prompt += """

## 特别关注：对话优化
- 增强对话的戏剧张力和情感冲击
- 提升对话的个性化和差异化
- 优化对话的节奏和流畅度
- 增强对话对角色塑造和主题深化的作用
- 增加对话的新颖性和创意
"""
    elif evolution_type == "action":
        base_prompt += """

## 特别关注：动作描写优化
- 增强动作描写的戏剧张力和紧张感
- 提升动作描写的动态感和画面感
- 优化动作序列的流畅性和节奏感
- 增强动作与情感冲击的结合
- 增加动作描写的新颖性和创意
"""
    elif evolution_type == "description":
        base_prompt += """

## 特别关注：环境描写优化
- 增强环境描写的沉浸感和情感冲击
- 提升描写的文学性和美感
- 优化环境与情节和主题的结合
- 增强环境对氛围和戏剧张力的营造作用
- 增加环境描写的新颖性和创意
"""
    elif evolution_type == "conflict":
        base_prompt += """

## 特别关注：冲突强化
- 增强冲突的戏剧张力和紧迫感
- 优化冲突的层次和递进
- 提升冲突解决的情感和主题深度
- 增强冲突对角色发展的推动作用
- 增加冲突设置的新颖性和创意
"""
    elif evolution_type == "character":
        base_prompt += """

## 特别关注：角色深化
- 增强角色的内心世界描写和情感冲击
- 提升角色情感表达的细腻度和真实感
- 优化角色关系的复杂性和戏剧张力
- 增强角色成长的主题深度和合理性
- 增加角色塑造的新颖性和创意
"""

    return base_prompt.strip()


def get_evolution_types() -> list:
    """获取可用的进化类型"""
    return [
        {"value": "general", "label": "综合进化", "description": "全面提升剧情质量，优化所有维度"},
        {"value": "dialogue", "label": "对话优化", "description": "重点优化对话的戏剧张力和情感冲击"},
        {"value": "action", "label": "动作强化", "description": "重点强化动作描写的紧张感和流畅度"},
        {"value": "description", "label": "描写美化", "description": "重点美化环境描写的沉浸感和创意"},
        {"value": "conflict", "label": "冲突强化", "description": "重点强化戏剧冲突的张力和主题深度"},
        {"value": "character", "label": "角色深化", "description": "重点深化角色塑造的层次和情感冲击"}
    ]
