"""
章节大纲生成Prompt模板
"""

def get_chapter_outline_generation_prompt(plot_segment: dict, previous_chapters: str = "", 
                                        current_chapter_number: int = 1, world_view: dict = None,
                                        characters: str = "", locations: str = "", 
                                        organizations: str = "", foreshadowing_network: str = "",
                                        validation_warnings: str = "") -> str:
    """
    获取章节大纲生成prompt
    
    Args:
        plot_segment: 剧情段落信息
        previous_chapters: 前文章节
        current_chapter_number: 当前章节编号
        world_view: 世界观信息
        characters: 角色信息
        locations: 地点信息
        organizations: 组织信息
        foreshadowing_network: 伏笔网络
        validation_warnings: 验证警告
    
    Returns:
        格式化的prompt字符串
    """
    world_view = world_view or {}
    
    return f"""你是一个专业的章节规划师。请根据剧情弧线、角色设定和世界观，为每个章节制定详细的大纲。

## 当前剧情段落
- 标题: {plot_segment.get('title', '')}
- 描述: {plot_segment.get('description', '')}
- 段落类型: {plot_segment.get('segment_type', '')}
- 段落顺序: {plot_segment.get('order', '')}
- 涉及角色: {plot_segment.get('characters_involved', '')}
- 主要冲突: {plot_segment.get('main_conflict', '')}
- 情感基调: {plot_segment.get('emotional_tone', '')}
- 紧张程度: {plot_segment.get('tension_level', 5)}/10
- 目标字数: {plot_segment.get('target_word_count', 3000)}
- 预计章节数: {plot_segment.get('estimated_chapters', 1)}

## 前文章节
{previous_chapters}

## 当前章节信息
- 章节编号: {current_chapter_number}
- 前文发展: 基于前面的章节内容

## 世界观信息
- 世界观名称: {world_view.get('name', '')}
- 力量体系: {world_view.get('power_system', '')}
- 文化背景: {world_view.get('culture', '')}

## 主要角色
{characters}

## 相关地点
{locations}

## 相关组织
{organizations}

## 伏笔网络
{foreshadowing_network}

## 逻辑验证警告
{validation_warnings}

## 要求
1. 章节要有明确的目标和冲突
2. 包含丰富的细节和描述
3. 为角色提供发展机会
4. 推进整体剧情发展
5. 保持与前后章节的连贯性
6. 合理使用伏笔和悬念

## 输出格式
请以JSON格式返回章节大纲信息，包括：
- title: 章节标题
- type: 章节类型 (OPENING/DEVELOPMENT/CLIMAX/RESOLUTION/TRANSITION/FLASHBACK/SIDE_STORY)
- word_count_target: 目标字数
- key_events: 关键事件列表
- characters_present: 出现角色列表
- location: 主要地点
- time_period: 时间背景
- main_conflict: 主要冲突
- foreshadowing_setups: 埋设的伏笔列表
- foreshadowing_payoffs: 回收的伏笔列表
- emotional_tone: 情感基调
- tension_level: 紧张程度 (1-10)

## 示例
{{
  "title": "初入宗门",
  "type": "DEVELOPMENT",
  "word_count_target": 3000,
  "key_events": [
    "主角到达宗门山门",
    "通过入门测试",
    "遇到重要角色",
    "发现神秘线索"
  ],
  "characters_present": ["主角", "宗门长老", "师兄"],
  "location": "天玄宗山门",
  "time_period": "春季",
  "main_conflict": "主角需要证明自己的修炼天赋",
  "foreshadowing_setups": ["foreshadowing_001"],
  "foreshadowing_payoffs": [],
  "emotional_tone": "紧张兴奋",
  "tension_level": 7
}}"""
