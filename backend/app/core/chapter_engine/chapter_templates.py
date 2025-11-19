"""
章节模板系统
"""
from typing import Dict, List
from .chapter_models import ChapterTemplate, PlotFunction, SceneType, EmotionalTone


class ChapterTemplateManager:
    """章节模板管理器"""
    
    def __init__(self):
        self.templates = self._initialize_templates()
    
    def _initialize_templates(self) -> Dict[str, ChapterTemplate]:
        """初始化章节模板"""
        templates = {}
        
        # 背景介绍模板
        templates["exposition"] = ChapterTemplate(
            template_id="exposition",
            template_name="背景介绍章节",
            plot_function=PlotFunction.EXPOSITION,
            structure=[
                "介绍故事背景",
                "介绍主要角色",
                "建立世界观",
                "设置初始状态"
            ],
            scene_types=[SceneType.ATMOSPHERIC, SceneType.DIALOGUE],
            emotional_tone=EmotionalTone.RELAXED,
            writing_tips=[
                "避免信息过载",
                "通过角色视角展示世界",
                "保持读者兴趣",
                "设置悬念"
            ]
        )
        
        # 引发事件模板
        templates["inciting_incident"] = ChapterTemplate(
            template_id="inciting_incident",
            template_name="引发事件章节",
            plot_function=PlotFunction.INCITING_INCIDENT,
            structure=[
                "正常生活被打破",
                "主角面临选择",
                "冲突开始显现",
                "故事目标确立"
            ],
            scene_types=[SceneType.ACTION, SceneType.DIALOGUE],
            emotional_tone=EmotionalTone.TENSE,
            writing_tips=[
                "制造戏剧性转折",
                "让主角主动选择",
                "建立紧迫感",
                "为后续冲突埋下伏笔"
            ]
        )
        
        # 上升行动模板
        templates["rising_action"] = ChapterTemplate(
            template_id="rising_action",
            template_name="上升行动章节",
            plot_function=PlotFunction.RISING_ACTION,
            structure=[
                "主角开始行动",
                "遇到障碍和挑战",
                "角色关系发展",
                "冲突逐步升级"
            ],
            scene_types=[SceneType.ACTION, SceneType.DIALOGUE, SceneType.BATTLE],
            emotional_tone=EmotionalTone.DRAMATIC,
            writing_tips=[
                "逐步增加紧张感",
                "发展角色关系",
                "引入新角色或元素",
                "为高潮做准备"
            ]
        )
        
        # 高潮模板
        templates["climax"] = ChapterTemplate(
            template_id="climax",
            template_name="高潮章节",
            plot_function=PlotFunction.CLIMAX,
            structure=[
                "冲突达到顶点",
                "主角面临最大挑战",
                "关键决策时刻",
                "冲突解决或转变"
            ],
            scene_types=[SceneType.BATTLE, SceneType.ACTION, SceneType.DIALOGUE],
            emotional_tone=EmotionalTone.TENSE,
            writing_tips=[
                "制造最大紧张感",
                "让主角面临终极选择",
                "解决主要冲突",
                "为结局做准备"
            ]
        )
        
        # 回落行动模板
        templates["falling_action"] = ChapterTemplate(
            template_id="falling_action",
            template_name="回落行动章节",
            plot_function=PlotFunction.FALLING_ACTION,
            structure=[
                "冲突后果显现",
                "角色处理结果",
                "关系重新调整",
                "为结局做准备"
            ],
            scene_types=[SceneType.DIALOGUE, SceneType.ATMOSPHERIC],
            emotional_tone=EmotionalTone.RELAXED,
            writing_tips=[
                "处理高潮的后果",
                "发展角色关系",
                "为结局做铺垫",
                "保持读者兴趣"
            ]
        )
        
        # 结局模板
        templates["resolution"] = ChapterTemplate(
            template_id="resolution",
            template_name="结局章节",
            plot_function=PlotFunction.RESOLUTION,
            structure=[
                "解决剩余问题",
                "角色获得成长",
                "关系得到确认",
                "故事圆满结束"
            ],
            scene_types=[SceneType.DIALOGUE, SceneType.ATMOSPHERIC],
            emotional_tone=EmotionalTone.JOYFUL,
            writing_tips=[
                "给读者满足感",
                "展示角色成长",
                "解决所有悬念",
                "留下余韵"
            ]
        )
        
        # 角色发展模板
        templates["character_development"] = ChapterTemplate(
            template_id="character_development",
            template_name="角色发展章节",
            plot_function=PlotFunction.CHARACTER_DEVELOPMENT,
            structure=[
                "角色面临挑战",
                "内心冲突展现",
                "成长时刻",
                "新能力或认知"
            ],
            scene_types=[SceneType.INTERNAL_MONOLOGUE, SceneType.DIALOGUE],
            emotional_tone=EmotionalTone.DRAMATIC,
            writing_tips=[
                "深入角色内心",
                "展示成长过程",
                "通过行动体现变化",
                "为后续情节做准备"
            ]
        )
        
        # 世界观构建模板
        templates["world_building"] = ChapterTemplate(
            template_id="world_building",
            template_name="世界观构建章节",
            plot_function=PlotFunction.WORLD_BUILDING,
            structure=[
                "介绍新环境",
                "展示世界规则",
                "介绍新角色",
                "扩展世界观"
            ],
            scene_types=[SceneType.ATMOSPHERIC, SceneType.DIALOGUE],
            emotional_tone=EmotionalTone.MYSTERIOUS,
            writing_tips=[
                "通过角色视角展示",
                "避免信息过载",
                "保持神秘感",
                "与主线情节结合"
            ]
        )
        
        # 伏笔设置模板
        templates["foreshadowing"] = ChapterTemplate(
            template_id="foreshadowing",
            template_name="伏笔设置章节",
            plot_function=PlotFunction.FORESHADOWING,
            structure=[
                "暗示未来事件",
                "引入关键元素",
                "建立联系",
                "增加悬念"
            ],
            scene_types=[SceneType.ATMOSPHERIC, SceneType.DIALOGUE],
            emotional_tone=EmotionalTone.MYSTERIOUS,
            writing_tips=[
                "巧妙暗示，不要过于明显",
                "与后续情节呼应",
                "增加故事深度",
                "保持读者好奇心"
            ]
        )
        
        # 过渡模板
        templates["transition"] = ChapterTemplate(
            template_id="transition",
            template_name="过渡章节",
            plot_function=PlotFunction.TRANSITION,
            structure=[
                "连接前后情节",
                "时间或地点转换",
                "角色状态调整",
                "为下个阶段做准备"
            ],
            scene_types=[SceneType.ATMOSPHERIC, SceneType.DIALOGUE],
            emotional_tone=EmotionalTone.RELAXED,
            writing_tips=[
                "保持故事流畅性",
                "避免突兀转换",
                "利用过渡发展角色",
                "为后续情节做铺垫"
            ]
        )
        
        return templates
    
    def get_template(self, template_id: str) -> ChapterTemplate:
        """获取指定模板"""
        return self.templates.get(template_id)
    
    def get_templates_by_function(self, plot_function: PlotFunction) -> List[ChapterTemplate]:
        """根据剧情功能获取模板"""
        return [template for template in self.templates.values() 
                if template.plot_function == plot_function]
    
    def get_all_templates(self) -> List[ChapterTemplate]:
        """获取所有模板"""
        return list(self.templates.values())
    
    def suggest_template(self, story_position: float, plot_function: PlotFunction) -> ChapterTemplate:
        """根据故事位置和剧情功能建议模板"""
        # 根据故事位置调整模板
        if story_position < 0.1:
            # 故事开始，优先使用背景介绍
            if plot_function == PlotFunction.EXPOSITION:
                return self.templates["exposition"]
        elif story_position < 0.2:
            # 引发事件阶段
            if plot_function == PlotFunction.INCITING_INCIDENT:
                return self.templates["inciting_incident"]
        elif story_position < 0.8:
            # 上升行动阶段
            if plot_function == PlotFunction.RISING_ACTION:
                return self.templates["rising_action"]
        elif story_position < 0.9:
            # 高潮阶段
            if plot_function == PlotFunction.CLIMAX:
                return self.templates["climax"]
        elif story_position < 0.95:
            # 回落行动阶段
            if plot_function == PlotFunction.FALLING_ACTION:
                return self.templates["falling_action"]
        else:
            # 结局阶段
            if plot_function == PlotFunction.RESOLUTION:
                return self.templates["resolution"]
        
        # 默认返回对应功能的模板
        templates = self.get_templates_by_function(plot_function)
        return templates[0] if templates else self.templates["transition"]


# 全局模板管理器实例
template_manager = ChapterTemplateManager()
