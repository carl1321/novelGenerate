"""
剧情大纲生成prompt - 简化版故事驱动模式
"""

def get_plot_outline_generation_prompt(
    # 世界观核心信息
    core_concept: str,           # 世界观核心概念
    world_description: str,      # 世界观描述
    geography_setting: str,      # 地理设定
    
    # 主角核心信息
    protagonist_name: str,       # 主角姓名
    protagonist_background: str, # 主角背景
    protagonist_personality: str, # 主角性格特质
    protagonist_goals: str,      # 主角目标
    
    # 人工输入的故事要素
    core_conflict: str,          # 核心冲突
    story_tone: str,            # 故事基调
    narrative_structure: str,    # 叙事结构
    story_structure: str,       # 故事结构
    theme: str,                  # 主题思想
    
    # 技术参数
    target_word_count: int,      # 目标字数
    estimated_chapters: int      # 预计章节数
) -> str:
    """基于简化的输入信息生成故事驱动的剧情大纲"""
    
    return f"""你是一个专业的剧情大纲设计师。请基于以下信息生成简洁实用的剧情大纲：

## 世界观信息
- **核心概念**: {core_concept}
- **世界观描述**: {world_description}
- **地理设定**: 
{geography_setting}

**地理设定说明**: 上述地理设定包含了完整的世界地图信息，包括各个区域的势力分布、资源状况、特殊地点等。请充分利用这些信息来设计剧情，确保故事中的事件和冲突与地理环境相符。

## 主角信息
- **姓名**: {protagonist_name}
- **背景**: {protagonist_background}
- **性格特质**: {protagonist_personality}
- **目标**: {protagonist_goals}

## 故事要素
- **核心冲突**: {core_conflict}
- **故事基调**: {story_tone}
- **叙事结构**: {narrative_structure}
- **故事结构**: {story_structure}
- **主题思想**: {theme}

## 技术要求
- **目标字数**: {target_word_count}字
- **预计章节数**: {estimated_chapters}章

## 任务要求
请生成一个以主角成长为核心的故事大纲，要求：

1. **故事简介**: 200-300字的故事概述
2. **幕次结构**: 根据{story_structure}结构设计幕次
3. **地理环境利用**: 充分利用地理设定中的区域、势力、资源等信息，确保剧情发展与地理环境紧密相关
4. **每个幕次包含**:
   - 核心任务: 主角在这一幕的主要目标和动机
   - 日常事件: 主角的日常修炼、生活、社交等活动，描述具体的行为和收获
   - 冲突事件: 主角面临的主要挑战和阻碍
   - 特殊事件: 主角的转折点、奇遇或重要发现
   - 重大事件: 非主角发起的环境变化事件（如宗门被灭、天灾降临等）
   - 阶段结果: 主角获得的成果、能力提升、资源积累和新目标设定

## 事件描述要求
- 每个事件主要描述核心内容，不要添加过多细节
- 每个事件描述控制在200字以内

## 输出格式
严格按照以下JSON格式输出：
{{
  "story_summary": "故事简介",
  "acts": [
    {{
      "act_number": 1,
      "act_name": "幕次名称",
      "core_mission": "核心任务描述",
      "daily_events": "日常事件描述",
      "conflict_events": "冲突事件描述",
      "special_events": "特殊事件描述",
      "major_events": "重大事件描述",
      "stage_result": "阶段结果描述"
    }}
  ]
}}

**重要提醒**：
- 确保故事逻辑连贯，主角成长轨迹清晰
- 重大事件要与世界观设定相符
- 充分利用地理设定中的势力分布、资源状况等信息
- 确保剧情发展与地理环境紧密相关
- 每个幕次都要有明确的推进作用

**输出要求**：
- 只输出JSON格式的内容，不要包含任何其他文字
- JSON必须是有效的格式，可以直接被解析
- 不要添加任何解释或说明文字"""