"""
事件评分prompt模板
用于对生成的事件进行多维度评分
"""

def get_event_scoring_prompt(event, characters, world_info, plot_info):
    """
    生成事件评分prompt
    
    Args:
        event: 事件对象
        characters: 角色列表
        world_info: 世界观信息
        plot_info: 剧情大纲信息
    
    Returns:
        str: 评分prompt
    """
    
    # 格式化世界观信息
    world_text = ""
    try:
        if isinstance(world_info, dict):
            world_text = f"""
核心概念: {world_info.get('core_concept', '未知')}
世界观描述: {world_info.get('world_description', '未知')}
"""
        else:
            world_text = str(world_info) if world_info else "暂无世界观信息"
    except Exception as e:
        print(f"处理世界观信息失败: {e}")
        world_text = "世界观信息处理失败"
    
    # 格式化剧情大纲信息
    plot_text = ""
    try:
        if isinstance(plot_info, dict):
            plot_text = f"""
剧情标题: {plot_info.get('title', '未知')}
故事背景: {plot_info.get('background', '未知')}
主要冲突: {plot_info.get('main_conflict', '未知')}
故事主题: {plot_info.get('theme', '未知')}
"""
        elif hasattr(plot_info, 'title'):
            # 处理PlotOutline对象
            plot_text = f"""
剧情标题: {getattr(plot_info, 'title', '未知')}
故事背景: {getattr(plot_info, 'story_summary', '未知')}
主要冲突: {getattr(plot_info, 'core_conflict', '未知')}
故事主题: {getattr(plot_info, 'theme', '未知')}
"""
        else:
            plot_text = str(plot_info) if plot_info else "暂无剧情信息"
    except Exception as e:
        print(f"处理剧情信息失败: {e}")
        plot_text = "剧情信息处理失败"
    
    prompt = f"""你是一位极其严格的小说事件评分师，请对以下事件进行多维度评分。特别注意剧情逻辑性与合理性的严格审查：

## 事件内容
**标题**: {event.title if hasattr(event, 'title') else '未知'}
**事件类型**: {event.event_type if hasattr(event, 'event_type') else '未知'}
**描述**: {event.description if hasattr(event, 'description') else '未知'}
**事件结果**: {event.outcome if hasattr(event, 'outcome') else '未知'}


## 世界观设定
{world_text}

## 剧情大纲
{plot_text}

## 评分要求
请从以下5个维度对事件进行严格评分（0-10分，10分为满分）：

1. **主角参与度** (protagonist_involvement): 事件是否以主角为核心？主角在事件中的作用是否突出？

2. **剧情逻辑性** (plot_coherence): 【重点审查维度】
   - 事件发展是否符合逻辑？因果关系是否清晰？
   - 角色行为是否符合其性格、能力、动机？
   - 事件是否与世界观设定一致？
   - 事件结果是否自然合理？

3. **文笔质量** (writing_quality): 语言表达是否简洁有力？描述是否清晰明了？

4. **戏剧张力** (dramatic_tension): 冲突是否激烈？紧张感是否足够？

5. **综合质量** (overall_quality): 整体评价，综合考虑所有维度

## 严格评分标准
**剧情逻辑性评分特别严格**：
- **9-10分**: 逻辑完美，无任何漏洞，因果关系清晰，角色行为完全合理
- **7-8分**: 逻辑基本合理，但存在轻微不合理之处
- **5-6分**: 逻辑有明显问题，存在不合理的情节或角色行为
- **3-4分**: 逻辑严重不合理，多处情节牵强或角色行为不符合设定
- **0-2分**: 逻辑完全不合理，存在重大漏洞或矛盾

**其他维度评分标准**：
- **9-10分**: 优秀，该维度表现突出
- **7-8分**: 良好，该维度表现较好
- **5-6分**: 一般，该维度表现中等
- **3-4分**: 较差，该维度存在明显问题
- **0-2分**: 很差，该维度严重不足

## 输出格式
请严格按照以下JSON格式输出评分结果：

```json
{{
    "protagonist_involvement": 8.5,
    "plot_coherence": 6.0,
    "writing_quality": 8.0,
    "dramatic_tension": 7.5,
    "overall_quality": 7.0,
    "feedback": "事件整体质量中等，主角参与度突出，文笔表达生动。但剧情逻辑性存在明显问题：1）角色行为不符合其设定；2）事件发展过于巧合；3）因果关系不够清晰。建议重新梳理情节逻辑，确保每个转折都有充分理由。",
    "strengths": [
        "主角在事件中发挥核心作用",
        "文笔表达生动细腻",
        "戏剧张力营造到位"
    ],
    "weaknesses": [
        "剧情逻辑存在明显漏洞",
        "角色行为不符合其性格设定",
        "事件发展过于巧合，缺乏充分理由",
        "因果关系不够清晰"
    ]
}}
```

## 特别注意事项
1. **严格审查逻辑性**：对任何不合理的情节、角色行为、因果关系都要严格扣分
2. **细节推敲**：仔细检查每个细节是否经得起推敲
3. **设定一致性**：确保事件与世界观、角色设定完全一致
4. **合理性判断**：对过于巧合或牵强的情节要严厉扣分
5. **客观评分**：不要因为其他维度表现好而放松对逻辑性的要求

请仔细分析事件内容，给出客观、严格、专业的评分。"""
    
    return prompt
