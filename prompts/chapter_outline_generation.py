"""
章节大纲生成Prompt模板 - 事件驱动版
"""

def get_chapter_outline_prompt(
    plot_outline: dict, 
    events: list,
    chapter_count: int,
    start_chapter: int,
    act_belonging: str = None,
    additional_requirements: str = ""
) -> str:
    """
    生成事件驱动的章节大纲prompt
    """
    
    # 构建事件信息（简化版，只包含名称和描述）
    events_info = ""
    if events:
        events_info = "### 可用事件列表（作为参考材料）\n"
        for i, event in enumerate(events, 1):
            description = event.get('description', '无描述')
            if description and description != '无描述':
                # 如果描述存在且不为空，截断到200字符
                if len(description) > 200:
                    description = description[:200] + "..."
            else:
                description = "暂无详细描述"
            
            events_info += f"""
**事件{i}**: {event.get('title', '无标题')}
- 描述: {description}
"""
    else:
        events_info = "### 可用事件列表\n暂无可用事件，请根据剧情需要自行编造事件。"

    prompt = f"""
你是一位专业的小说章节大纲生成师，擅长基于事件驱动生成连贯的章节大纲。

## 任务要求
基于提供的事件生成 {chapter_count} 个章节大纲（第 {start_chapter} 到第 {start_chapter + chapter_count - 1} 章）。
{f"**重要：当前生成的是 {act_belonging} 的章节，请围绕该幕次的事件推动剧情发展。**" if act_belonging else ""}

**核心事件选择**：多个章节可以围绕同一个事件展开，将一个事件分解为多个片段和场景。每个章节可以选择下面提供的事件列表中的事件作为核心事件，也可以根据章节剧情需要自己编造新的事件标题。

**事件展开示例**：
- 事件"黑狼帮逼婚"可以分解为：第1章"危机降临"（介绍威胁）、第2章"暗中布局"（林凡准备）、第3章"智斗流寇"（实施计划）
- 事件"流民潮涌"可以分解为：第1章"难民涌入"（危机开始）、第2章"组织救援"（林凡行动）、第3章"建立秩序"（管理流民）

## 核心原则
**事件是剧情驱动的核心要素，章节要围绕事件去推动剧情，场景要围绕事件去细化。**

## 输入信息

### 剧情大纲
标题: {plot_outline.get('title', '未知标题')}
描述: {plot_outline.get('description', '无描述')}
故事基调: {plot_outline.get('story_tone', '未知')}
叙事结构: {plot_outline.get('narrative_structure', '未知')}
故事结构: {plot_outline.get('story_structure', '未知')}

### 额外要求
{additional_requirements if additional_requirements else "无特殊要求"}

## 生成要求

### 1. 事件驱动原则
- **事件是剧情驱动的核心要素**，多个章节可以围绕同一个事件展开
- **事件分解**：将一个复杂事件分解为多个章节片段，每个章节展现事件的不同阶段
- **章节要围绕事件推动剧情发展**，确保事件在章节中起到核心作用
- **场景要围绕事件细化表达**，用场景展现事件的发生过程

### 2. 章节结构
- 每个章节包含 3-5 个关键场景，围绕核心事件展开
- 场景要有明确的事件关联性，服务于事件的发展
- 场景之间要有事件驱动的逻辑连接
- 核心事件字段使用提供事件列表中的事件标题或自己编造的标题
- **事件展开**：同一个事件可以在多个章节中逐步展开，每个章节展现事件的不同侧面

### 3. 剧情功能
- 每个章节要有明确的剧情功能，推进主线剧情发展
- 保持适当的冲突和张力
- 确保事件与当前幕次的剧情发展相符


## 输出格式
请严格按照以下JSON格式输出，确保所有字段都有具体内容，特别注意：
1. 所有字符串内容不要包含换行符，使用句号结尾
2. 描述内容控制在指定字数内，避免过长
3. 确保JSON格式正确，所有引号和括号匹配
4. **core_event字段**：可以使用提供事件列表中的事件标题，也可以根据章节需要编造新的事件标题
5. **title字段**：章节标题应该是概括性的标题，不要直接使用事件名称作为章节标题

{{
    "chapters": [
        {{
            "chapter_number": 1,
            "title": "章节标题",
            "act_belonging": "第一幕",
            "chapter_summary": "章节概要，100-200字，详细描述章节的主要情节和事件发展。",
            "core_event": "从提供事件列表选择或自编的事件标题",
            "key_scenes": [
                {{
                    "scene_title": "场景标题",
                    "scene_description": "场景描述，100-150字，详细描述场景环境、人物行动和情节发展。",
                }}
            ]
        }}
    ]
}}

## 注意事项
1. 确保章节编号连续，从 {start_chapter} 开始
2. **事件驱动**：多个章节可以围绕同一个事件展开，事件是剧情驱动的核心要素
3. **事件分解**：将一个复杂事件分解为多个章节片段，每个章节展现事件的不同阶段
4. **场景细化**：场景要围绕事件细化表达，展现事件的发生过程
5. **剧情推动**：章节要推动剧情发展，确保事件在章节中起到核心作用
6. 关键场景不能为空，每个场景都要与核心事件有关联
7. 剧情发展要符合剧情大纲设定
8. **章节标题**：章节标题应该是概括性的标题，体现章节的主要情节或主题，不要直接使用事件名称
9. **核心事件**：core_event字段使用事件名称，title字段使用章节标题
10. **事件展开**：同一个事件可以在多个章节中逐步展开，每个章节展现事件的不同侧面
{f"11. **幕次一致性**：当前生成的是 {act_belonging} 的章节，必须围绕该幕次的事件推动剧情发展" if act_belonging else ""}

请开始生成章节大纲：

{events_info}
"""

    return prompt
           