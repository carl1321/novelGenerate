"""
世界观规则引擎
"""
import json
from typing import Dict, List, Any, Optional
from pathlib import Path
import yaml

from app.core.world.models import WorldRule, CultivationLevel, ElementType, OrganizationType, LocationType


class RuleEngine:
    """规则引擎类"""
    
    def __init__(self):
        self.rules: Dict[str, WorldRule] = {}
        self.rule_categories = {
            "cultivation": "修炼体系",
            "geography": "地理规则",
            "organization": "组织规则",
            "artifact": "法宝规则",
            "pill": "丹药规则",
            "combat": "战斗规则",
            "economy": "经济规则",
            "social": "社会规则"
        }
        self._load_default_rules()
    
    def _load_default_rules(self):
        """加载默认规则库"""
        # 修炼体系规则
        cultivation_rules = [
            {
                "id": "cultivation_level_progression",
                "name": "境界提升规则",
                "category": "cultivation",
                "content": "修炼境界必须按顺序提升：凡人→练气→筑基→金丹→元婴→化神→合体→大乘→仙人",
                "priority": 10
            },
            {
                "id": "cultivation_time_requirement",
                "name": "修炼时间要求",
                "category": "cultivation",
                "content": "每个境界的修炼时间随境界提升呈指数增长，练气期1-10年，筑基期10-100年，金丹期100-1000年",
                "priority": 9
            },
            {
                "id": "element_compatibility",
                "name": "灵根属性相性",
                "category": "cultivation",
                "content": "金克木，木克土，土克水，水克火，火克金。相克属性修炼困难，相生属性修炼容易",
                "priority": 8
            }
        ]
        
        # 地理规则
        geography_rules = [
            {
                "id": "spiritual_energy_distribution",
                "name": "灵气分布规则",
                "category": "geography",
                "content": "灵气浓度与地理位置相关，山脉、湖泊、森林等自然景观灵气较浓，城市、平原灵气较稀",
                "priority": 7
            },
            {
                "id": "secret_realm_access",
                "name": "秘境进入规则",
                "category": "geography",
                "content": "秘境通常有境界限制，高级秘境需要特定境界或特殊条件才能进入",
                "priority": 8
            }
        ]
        
        # 组织规则
        organization_rules = [
            {
                "id": "sect_hierarchy",
                "name": "宗门等级制度",
                "category": "organization",
                "content": "宗门内部等级：外门弟子→内门弟子→核心弟子→长老→掌门。等级越高，资源越多，责任越大",
                "priority": 9
            },
            {
                "id": "resource_allocation",
                "name": "资源分配规则",
                "category": "organization",
                "content": "宗门资源按弟子等级和贡献分配，高级弟子享有更多修炼资源",
                "priority": 7
            }
        ]
        
        # 法宝规则
        artifact_rules = [
            {
                "id": "artifact_grade_power",
                "name": "法宝品级威力",
                "category": "artifact",
                "content": "法宝品级越高威力越大，但使用条件也越严格，需要更高境界或特殊灵根",
                "priority": 8
            },
            {
                "id": "artifact_binding",
                "name": "法宝认主规则",
                "category": "artifact",
                "content": "高级法宝需要认主才能发挥全部威力，认主后与主人心神相连",
                "priority": 7
            }
        ]
        
        # 战斗规则
        combat_rules = [
            {
                "id": "level_difference_power",
                "name": "境界差距影响",
                "category": "combat",
                "content": "境界差距越大，低境界者越难对高境界者造成伤害，但可以通过法宝、功法等弥补",
                "priority": 9
            },
            {
                "id": "element_advantage",
                "name": "属性相克优势",
                "category": "combat",
                "content": "相克属性在战斗中具有优势，但境界差距过大时相克效果减弱",
                "priority": 6
            }
        ]
        
        # 加载所有规则
        all_rules = (cultivation_rules + geography_rules + 
                    organization_rules + artifact_rules + combat_rules)
        
        for rule_data in all_rules:
            rule = WorldRule(**rule_data)
            self.rules[rule.id] = rule
    
    def add_rule(self, rule: WorldRule) -> bool:
        """添加新规则"""
        try:
            self.rules[rule.id] = rule
            return True
        except Exception as e:
            print(f"添加规则失败: {e}")
            return False
    
    def remove_rule(self, rule_id: str) -> bool:
        """删除规则"""
        if rule_id in self.rules:
            del self.rules[rule_id]
            return True
        return False
    
    def get_rules_by_category(self, category: str) -> List[WorldRule]:
        """根据分类获取规则"""
        return [rule for rule in self.rules.values() 
                if rule.category == category and rule.is_active]
    
    def get_rule(self, rule_id: str) -> Optional[WorldRule]:
        """获取指定规则"""
        return self.rules.get(rule_id)
    
    def validate_cultivation_progression(self, current_level: CultivationLevel, 
                                       target_level: CultivationLevel) -> bool:
        """验证修炼境界提升是否合理"""
        level_order = [
            CultivationLevel.MORTAL,
            CultivationLevel.QI_REFINING,
            CultivationLevel.FOUNDATION,
            CultivationLevel.GOLDEN_CORE,
            CultivationLevel.NASCENT_SOUL,
            CultivationLevel.SPIRIT_TRANSFORMATION,
            CultivationLevel.SPIRIT_FUSION,
            CultivationLevel.GREAT_ACCOMPLISHMENT,
            CultivationLevel.IMMORTAL
        ]
        
        current_index = level_order.index(current_level)
        target_index = level_order.index(target_level)
        
        # 只能提升到下一个境界
        return target_index == current_index + 1
    
    def validate_element_compatibility(self, element1: ElementType, 
                                     element2: ElementType) -> str:
        """验证灵根属性相性"""
        # 相克关系
        conflicts = {
            ElementType.GOLD: ElementType.WOOD,
            ElementType.WOOD: ElementType.EARTH,
            ElementType.EARTH: ElementType.WATER,
            ElementType.WATER: ElementType.FIRE,
            ElementType.FIRE: ElementType.GOLD
        }
        
        # 相生关系
        harmony = {
            ElementType.GOLD: ElementType.WATER,
            ElementType.WATER: ElementType.WOOD,
            ElementType.WOOD: ElementType.FIRE,
            ElementType.FIRE: ElementType.EARTH,
            ElementType.EARTH: ElementType.GOLD
        }
        
        if conflicts.get(element1) == element2:
            return "相克"
        elif harmony.get(element1) == element2:
            return "相生"
        else:
            return "中性"
    
    def validate_artifact_usage(self, artifact_grade: int, 
                              user_level: CultivationLevel) -> bool:
        """验证法宝使用条件"""
        level_requirements = {
            CultivationLevel.MORTAL: 1,
            CultivationLevel.QI_REFINING: 2,
            CultivationLevel.FOUNDATION: 3,
            CultivationLevel.GOLDEN_CORE: 4,
            CultivationLevel.NASCENT_SOUL: 5,
            CultivationLevel.SPIRIT_TRANSFORMATION: 6,
            CultivationLevel.SPIRIT_FUSION: 7,
            CultivationLevel.GREAT_ACCOMPLISHMENT: 8,
            CultivationLevel.IMMORTAL: 9
        }
        
        required_level = level_requirements.get(user_level, 1)
        return artifact_grade <= required_level
    
    def check_rule_violation(self, context: Dict[str, Any]) -> List[str]:
        """检查规则违反情况"""
        violations = []
        
        # 检查修炼境界提升
        if "cultivation_progression" in context:
            current = context["cultivation_progression"].get("current_level")
            target = context["cultivation_progression"].get("target_level")
            if current and target:
                if not self.validate_cultivation_progression(current, target):
                    violations.append(f"修炼境界提升不合理：从{current}直接跳到{target}")
        
        # 检查法宝使用
        if "artifact_usage" in context:
            grade = context["artifact_usage"].get("grade")
            user_level = context["artifact_usage"].get("user_level")
            if grade and user_level:
                if not self.validate_artifact_usage(grade, user_level):
                    violations.append(f"境界{user_level}无法使用{grade}品法宝")
        
        # 检查属性相性
        if "element_interaction" in context:
            element1 = context["element_interaction"].get("element1")
            element2 = context["element_interaction"].get("element2")
            if element1 and element2:
                compatibility = self.validate_element_compatibility(element1, element2)
                if compatibility == "相克":
                    violations.append(f"属性{element1}与{element2}相克，修炼困难")
        
        return violations
    
    def export_rules(self, file_path: str) -> bool:
        """导出规则到文件"""
        try:
            rules_data = {
                "rules": [rule.dict() for rule in self.rules.values()],
                "categories": self.rule_categories
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(rules_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"导出规则失败: {e}")
            return False
    
    def import_rules(self, file_path: str) -> bool:
        """从文件导入规则"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                rules_data = json.load(f)
            
            for rule_data in rules_data.get("rules", []):
                rule = WorldRule(**rule_data)
                self.rules[rule.id] = rule
            
            return True
        except Exception as e:
            print(f"导入规则失败: {e}")
            return False
