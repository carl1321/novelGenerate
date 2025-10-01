"""
动态解析器 - 使用LLM解析大模型生成的内容
"""
import json
import asyncio
from typing import Any, Dict, List, Optional, Type, Union
from enum import Enum

from app.utils import llm_client
from app.core.character.models import CultivationLevel, ElementType, Gender, GoalType, CharacterRoleType
from app.core.world.models import CultivationLevel as WorldCultivationLevel, ElementType as WorldElementType


class DynamicParser:
    """动态解析器，使用LLM解析各种类型的内容"""
    
    def __init__(self):
        self.cultivation_levels = {
            "凡人": CultivationLevel.MORTAL,
            "练气": CultivationLevel.QI_REFINING,
            "炼体": CultivationLevel.QI_REFINING,
            "筑基": CultivationLevel.FOUNDATION,
            "金丹": CultivationLevel.GOLDEN_CORE,
            "元婴": CultivationLevel.NASCENT_SOUL,
            "化神": CultivationLevel.SPIRIT_TRANSFORMATION,
            "合体": CultivationLevel.SPIRIT_FUSION,
            "大乘": CultivationLevel.GREAT_ACCOMPLISHMENT,
            "渡劫": CultivationLevel.GREAT_ACCOMPLISHMENT,
            "仙人": CultivationLevel.IMMORTAL,
            "真仙": CultivationLevel.IMMORTAL,
            "天仙": CultivationLevel.IMMORTAL,
        }
        
        self.element_types = {
            "金": ElementType.GOLD,
            "木": ElementType.WOOD,
            "水": ElementType.WATER,
            "火": ElementType.FIRE,
            "土": ElementType.EARTH,
            "风": ElementType.WIND,
            "雷": ElementType.THUNDER,
            "冰": ElementType.ICE,
            "光": ElementType.LIGHT,
            "暗": ElementType.DARK,
        }
        
        self.genders = {
            "男": Gender.MALE,
            "女": Gender.FEMALE,
            "男性": Gender.MALE,
            "女性": Gender.FEMALE,
            "非二元": Gender.NON_BINARY,
            "无相": Gender.NON_BINARY,
            "其他": Gender.OTHER,
            "未知": Gender.UNKNOWN,
        }
        
        self.goal_types = {
            "复仇": GoalType.REVENGE,
            "变强": GoalType.POWER,
            "权力": GoalType.POWER,
            "长生": GoalType.CULTIVATION,
            "修炼": GoalType.CULTIVATION,
            "保护": GoalType.PROTECTION,
            "探索": GoalType.EXPLORATION,
            "爱情": GoalType.LOVE,
            "求知": GoalType.KNOWLEDGE,
            "创造": GoalType.CREATION,
            "毁灭": GoalType.DESTRUCTION,
        }
        
        self.role_types = {
            "主角": CharacterRoleType.PROTAGONIST,
            "配角": CharacterRoleType.SUPPORTING,
            "反派": CharacterRoleType.ANTAGONIST,
            "导师": CharacterRoleType.MENTOR,
            "盟友": CharacterRoleType.ALLY,
            "路人": CharacterRoleType.EXTRA,
            "忠诚伙伴": CharacterRoleType.LOYAL_COMPANION,
            "叛逆盟友": CharacterRoleType.REBEL_ALLY,
            "技术支援": CharacterRoleType.TECH_SUPPORT,
            "神秘向导": CharacterRoleType.MYSTERIOUS_GUIDE,
            "亦敌亦友": CharacterRoleType.FRIEND_FOE,
            "治愈辅助": CharacterRoleType.HEALING_SUPPORT,
            "热血斗士": CharacterRoleType.HOT_BLOODED_WARRIOR,
            "智囊谋士": CharacterRoleType.STRATEGIC_ADVISOR,
            "情报联络": CharacterRoleType.INTELLIGENCE_CONTACT,
            "悲情守护者": CharacterRoleType.TRAGIC_GUARDIAN,
            "正义伙伴": CharacterRoleType.JUSTICE_COMPANION,
            "叛逆伙伴": CharacterRoleType.REBELLIOUS_COMPANION,
            "神秘导师型伙伴": CharacterRoleType.MYSTERIOUS_MENTOR,
            "技术型伙伴": CharacterRoleType.TECH_COMPANION,
            "忠诚护卫型伙伴": CharacterRoleType.LOYAL_GUARDIAN,
            "治愈型伙伴": CharacterRoleType.HEALING_COMPANION,
            "自由奔放型伙伴": CharacterRoleType.FREE_SPIRIT,
            "赎罪型伙伴": CharacterRoleType.REDEMPTION_COMPANION,
            "自然亲和型伙伴": CharacterRoleType.NATURE_AFFINITY,
            "智囊型伙伴": CharacterRoleType.WISDOM_COMPANION,
        }
    
    async def parse_cultivation_level(self, level_str: str) -> CultivationLevel:
        """动态解析修炼境界"""
        if not level_str or level_str.strip() == "":
            return CultivationLevel.QI_REFINING
        
        # 首先尝试直接匹配
        level_str = level_str.strip()
        for key, value in self.cultivation_levels.items():
            if key in level_str:
                return value
        
        # 如果直接匹配失败，使用LLM解析
        try:
            return await self._llm_parse_enum(level_str, self.cultivation_levels, CultivationLevel.QI_REFINING)
        except:
            return CultivationLevel.QI_REFINING
    
    async def parse_element_type(self, element_str: str) -> ElementType:
        """动态解析元素类型"""
        if not element_str or element_str.strip() == "":
            return ElementType.GOLD
        
        element_str = element_str.strip()
        for key, value in self.element_types.items():
            if key in element_str:
                return value
        
        try:
            return await self._llm_parse_enum(element_str, self.element_types, ElementType.GOLD)
        except:
            return ElementType.GOLD
    
    async def parse_gender(self, gender_str: str) -> Gender:
        """动态解析性别"""
        if not gender_str or gender_str.strip() == "":
            return Gender.MALE
        
        gender_str = gender_str.strip()
        for key, value in self.genders.items():
            if key in gender_str:
                return value
        
        try:
            return await self._llm_parse_enum(gender_str, self.genders, Gender.MALE)
        except:
            return Gender.MALE
    
    async def parse_goal_type(self, goal_str: str) -> GoalType:
        """动态解析目标类型"""
        if not goal_str or goal_str.strip() == "":
            return GoalType.POWER
        
        goal_str = goal_str.strip()
        for key, value in self.goal_types.items():
            if key in goal_str:
                return value
        
        try:
            return await self._llm_parse_enum(goal_str, self.goal_types, GoalType.POWER)
        except:
            return GoalType.POWER
    
    async def parse_role_type(self, role_str: str) -> CharacterRoleType:
        """动态解析角色类型"""
        if not role_str or role_str.strip() == "":
            return CharacterRoleType.JUSTICE_COMPANION
        
        role_str = role_str.strip()
        for key, value in self.role_types.items():
            if key in role_str:
                return value
        
        try:
            return await self._llm_parse_enum(role_str, self.role_types, CharacterRoleType.JUSTICE_COMPANION)
        except:
            return CharacterRoleType.JUSTICE_COMPANION
    
    async def parse_power_level(self, power_str: str) -> int:
        """动态解析力量等级（1-10）"""
        if not power_str or power_str.strip() == "":
            return 5
        
        power_str = power_str.strip().lower()
        
        # 直接数字匹配
        try:
            if power_str.isdigit():
                level = int(power_str)
                return max(1, min(10, level))
        except:
            pass
        
        # 关键词匹配
        power_keywords = {
            "极弱": 1, "很弱": 2, "弱": 3, "较弱": 4,
            "中等": 5, "一般": 5, "普通": 5,
            "较强": 6, "强": 7, "很强": 8, "极强": 9, "最强": 10,
            "入门": 3, "初级": 4, "中级": 6, "高级": 8, "顶级": 10,
            "练气": 3, "筑基": 4, "金丹": 5, "元婴": 6, "化神": 7, "合体": 8, "大乘": 9, "仙人": 10
        }
        
        for keyword, level in power_keywords.items():
            if keyword in power_str:
                return level
        
        # 使用LLM解析
        try:
            return await self._llm_parse_power_level(power_str)
        except:
            return 5
    
    async def _llm_parse_enum(self, input_str: str, enum_mapping: Dict[str, Any], default_value: Any) -> Any:
        """使用LLM解析枚举值"""
        prompt = f"""
请根据以下输入字符串，从给定的选项中选择最匹配的枚举值。

输入字符串: "{input_str}"

可选选项:
{json.dumps(enum_mapping, ensure_ascii=False, indent=2)}

请只返回最匹配的键名，不要返回其他内容。
"""
        
        try:
            response = await llm_client.generate_text(prompt, max_tokens=100)
            response = response.strip().strip('"').strip("'")
            
            if response in enum_mapping:
                return enum_mapping[response]
            else:
                return default_value
        except:
            return default_value
    
    async def _llm_parse_power_level(self, power_str: str) -> int:
        """使用LLM解析力量等级"""
        prompt = f"""
请根据以下描述，评估力量等级（1-10分）。

描述: "{power_str}"

评分标准:
1-2分: 极弱/很弱
3-4分: 弱/较弱/入门/初级
5分: 中等/一般/普通
6-7分: 较强/强/中级
8-9分: 很强/极强/高级
10分: 最强/顶级

请只返回一个数字（1-10），不要返回其他内容。
"""
        
        try:
            response = await llm_client.generate_text(prompt, max_tokens=50)
            level = int(response.strip())
            return max(1, min(10, level))
        except:
            return 5
    
    def add_cultivation_level(self, key: str, value: CultivationLevel):
        """动态添加修炼境界"""
        self.cultivation_levels[key] = value
    
    def add_element_type(self, key: str, value: ElementType):
        """动态添加元素类型"""
        self.element_types[key] = value
    
    def add_gender(self, key: str, value: Gender):
        """动态添加性别"""
        self.genders[key] = value
    
    def add_goal_type(self, key: str, value: GoalType):
        """动态添加目标类型"""
        self.goal_types[key] = value
    
    def parse_json(self, text: str) -> Optional[Dict[str, Any]]:
        """解析JSON文本"""
        try:
            # 尝试直接解析JSON
            return json.loads(text)
        except json.JSONDecodeError:
            # 如果直接解析失败，尝试提取JSON部分
            import re
            # 查找JSON对象
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except json.JSONDecodeError:
                    pass
            
            # 查找JSON数组
            array_match = re.search(r'\[.*\]', text, re.DOTALL)
            if array_match:
                try:
                    return json.loads(array_match.group())
                except json.JSONDecodeError:
                    pass
            
            return None


# 全局解析器实例
dynamic_parser = DynamicParser()
