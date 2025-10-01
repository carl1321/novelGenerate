"""
伏笔网络创建Prompt模板
"""

def get_foreshadowing_network_creation_prompt(plot_outline: dict, characters: str = "",
                                            world_view: dict = None, templates: str = "") -> str:
    """
    获取伏笔网络创建prompt
    
    Args:
        plot_outline: 剧情大纲
        characters: 角色信息
        world_view: 世界观信息
        templates: 伏笔模板
    
    Returns:
        格式化的prompt字符串
    """
    world_view = world_view or {}
    
    return f"""你是一个专业的伏笔设计师。请根据剧情大纲、角色设定和世界观，设计巧妙的伏笔网络。

## 剧情大纲
- 标题: {plot_outline.get('title', '')}
- 描述: {plot_outline.get('description', '')}
- 主要冲突: {plot_outline.get('main_conflicts', '')}
- 主题: {plot_outline.get('themes', '')}

## 主要角色
{characters}

## 世界观信息
- 世界观名称: {world_view.get('name', '')}
- 力量体系: {world_view.get('power_system', '')}
- 文化背景: {world_view.get('culture', '')}

## 伏笔模板
{templates}

## 要求
1. 伏笔要自然，不显突兀
2. 与后续剧情呼应
3. 增加故事的深度和层次
4. 为读者提供重读的乐趣
5. 符合角色的行为逻辑
6. 考虑伏笔的隐蔽程度和重要性

## 输出格式
请以JSON格式返回伏笔网络信息，包括：
- story_id: 故事ID
- setups: 伏笔设置列表，每个伏笔包含：
  - id: 伏笔ID
  - title: 伏笔标题
  - description: 伏笔描述
  - type: 伏笔类型 (DIALOGUE/ACTION/OBJECT/ENVIRONMENT/CHARACTER/EVENT/SYMBOL)
  - level: 隐蔽程度 (OBVIOUS/SUBTLE/HIDDEN/CRYPTIC)
  - setup_chapter: 埋设章节
  - payoff_chapter: 回收章节
  - content: 具体内容
  - characters_involved: 涉及角色列表
  - importance: 重要性 (1-10)
  - subtlety: 隐蔽程度 (1-10)
- connections: 伏笔之间的连接关系
- themes: 主题伏笔列表

## 示例
{{
  "story_id": "story_001",
  "setups": [
    {{
      "id": "foreshadowing_001",
      "title": "神秘古玉",
      "description": "主角在古墓中发现的神秘古玉，看似普通但蕴含强大力量",
      "type": "OBJECT",
      "level": "SUBTLE",
      "setup_chapter": 3,
      "payoff_chapter": 15,
      "content": "主角在古墓中发现一块温润的古玉，上面刻着奇异的符文，虽然不知道用途，但总感觉不简单",
      "characters_involved": ["主角"],
      "importance": 9,
      "subtlety": 7
    }}
  ],
  "connections": [
    ["foreshadowing_001", "foreshadowing_002"]
  ],
  "themes": ["命运", "力量", "传承"]
}}"""
