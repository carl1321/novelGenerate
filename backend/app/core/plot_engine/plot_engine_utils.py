"""
剧情引擎工具方法
"""
from typing import List, Dict, Any
from app.core.plot_engine.plot_models import PlotOutline, PlotStructure


class PlotEngineUtils:
    """剧情引擎工具类"""
    
    @staticmethod
    def build_plot_structure_prompt(request, world_view: Dict[str, Any], characters: List[Dict[str, Any]]) -> str:
        """构建剧情结构生成提示词"""
        characters_info = "\n".join([
            f"- {char['name']}: {char.get('role_type', '未知')} - {char.get('background', '未知背景')}"
            for char in characters
        ])
        
        return f"""
        请根据以下信息设计一个完整的剧情大纲：
        
        ## 基本信息
        - 标题：{request.title}
        - 描述：{request.description}
        - 结构类型：{request.structure_type.value}
        - 总章节数：{request.total_chapters}
        - 目标字数：{request.target_word_count}
        
        ## 世界观信息
        - 世界观：{world_view.get('name', '未知')}
        - 描述：{world_view.get('description', '未知')}
        - 力量体系：{world_view.get('power_system', '未知')}
        - 文化背景：{world_view.get('culture', '未知')}
        
        ## 角色信息
        {characters_info}
        
        ## 剧情要求
        - 主要冲突：{request.main_conflict}
        - 主题思想：{request.theme}
        - 故事基调：{request.tone}
        - 额外要求：{request.additional_requirements or '无'}
        
        请设计一个完整的剧情大纲，包括：
        1. 整体剧情走向
        2. 关键转折点
        3. 角色发展轨迹
        4. 伏笔设置
        5. 冲突升级过程
        
        请以结构化的方式组织内容。
        """
    
    @staticmethod
    def build_chapter_prompt(plot_outline: PlotOutline, template: Dict[str, Any], 
                           chapter_number: int, world_view: Dict[str, Any], 
                           characters: List[Dict[str, Any]]) -> str:
        """构建章节生成提示词"""
        characters_info = "\n".join([
            f"- {char['name']}: {char.get('role_type', '未知')} - {char.get('background', '未知背景')}"
            for char in characters
        ])
        
        return f"""
        请为剧情大纲《{plot_outline.title}》设计第{chapter_number}章的详细大纲。
        
        ## 章节模板信息
        - 章节类型：{template.get('type', '普通章节')}
        - 主要功能：{template.get('function', '推进剧情')}
        - 重点内容：{template.get('focus', '角色发展')}
        
        ## 剧情背景
        - 主题：{plot_outline.theme}
        - 主要冲突：{plot_outline.main_conflict}
        - 故事基调：{plot_outline.tone}
        
        ## 角色信息
        {characters_info}
        
        请设计该章节的详细内容，包括：
        1. 章节标题
        2. 章节概要
        3. 主要事件
        4. 关键场景
        5. 参与角色
        6. 角色发展
        7. 冲突升级
        8. 剧情推进
        9. 伏笔设置
        10. 预计字数
        
        请确保内容与整体剧情保持一致。
        """
    
    @staticmethod
    def get_three_act_structure(total_chapters: int) -> List[Dict[str, Any]]:
        """获取三幕式结构模板"""
        act1_chapters = max(1, total_chapters // 4)
        act2_chapters = total_chapters // 2
        act3_chapters = total_chapters - act1_chapters - act2_chapters
        
        templates = []
        
        # 第一幕：开端
        for i in range(act1_chapters):
            templates.append({
                "type": "开端",
                "function": "建立世界观和角色",
                "focus": "角色介绍和背景设定"
            })
        
        # 第二幕：发展
        for i in range(act2_chapters):
            templates.append({
                "type": "发展",
                "function": "冲突升级和角色成长",
                "focus": "剧情推进和角色发展"
            })
        
        # 第三幕：结局
        for i in range(act3_chapters):
            templates.append({
                "type": "结局",
                "function": "冲突解决和主题升华",
                "focus": "高潮和结局"
            })
        
        return templates
    
    @staticmethod
    def get_five_act_structure(total_chapters: int) -> List[Dict[str, Any]]:
        """获取五幕式结构模板"""
        chapters_per_act = total_chapters // 5
        remaining_chapters = total_chapters % 5
        
        templates = []
        act_types = ["开端", "上升", "高潮", "下降", "结局"]
        
        for act_idx, act_type in enumerate(act_types):
            chapters_count = chapters_per_act + (1 if act_idx < remaining_chapters else 0)
            for i in range(chapters_count):
                templates.append({
                    "type": act_type,
                    "function": f"{act_type}阶段",
                    "focus": "剧情推进"
                })
        
        return templates
    
    @staticmethod
    def get_freeform_structure(total_chapters: int) -> List[Dict[str, Any]]:
        """获取自由形式结构模板"""
        templates = []
        for i in range(total_chapters):
            templates.append({
                "type": "自由章节",
                "function": "推进剧情",
                "focus": "角色发展和剧情推进"
            })
        return templates
    
    @staticmethod
    def parse_plot_response(response: str) -> Dict[str, Any]:
        """解析剧情生成响应"""
        # 简单的文本解析，实际项目中可以使用更复杂的解析逻辑
        return {
            "title": "解析的标题",
            "description": "解析的描述",
            "structure": "解析的结构"
        }
    
    @staticmethod
    def parse_chapter_response(response: str) -> Dict[str, Any]:
        """解析章节生成响应"""
        # 简单的文本解析，实际项目中可以使用更复杂的解析逻辑
        return {
            "title": "解析的章节标题",
            "summary": "解析的章节概要",
            "main_events": ["事件1", "事件2"],
            "key_scenes": ["场景1", "场景2"],
            "participating_characters": ["角色1", "角色2"],
            "character_development": {"角色1": "发展描述"},
            "conflict_escalation": "冲突升级描述",
            "plot_advancement": "剧情推进描述",
            "foreshadowing": ["伏笔1", "伏笔2"],
            "estimated_word_count": 5000
        }
