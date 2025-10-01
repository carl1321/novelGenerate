"""
角色关系管理器
"""
from typing import List, Dict, Any, Optional, Tuple
import random
from datetime import datetime

from app.core.character.models import (
    Character, Relationship, RelationshipType, PersonalityTrait
)


class RelationshipManager:
    """关系管理器"""
    
    def __init__(self):
        # 性格相性表
        self.personality_compatibility = {
            PersonalityTrait.BRAVE: [PersonalityTrait.BRAVE, PersonalityTrait.LOYAL, PersonalityTrait.AMBITIOUS],
            PersonalityTrait.CAUTIOUS: [PersonalityTrait.CAUTIOUS, PersonalityTrait.WISE, PersonalityTrait.PATIENT],
            PersonalityTrait.ARROGANT: [PersonalityTrait.ARROGANT, PersonalityTrait.AMBITIOUS, PersonalityTrait.VENGEFUL],
            PersonalityTrait.HUMBLE: [PersonalityTrait.HUMBLE, PersonalityTrait.GENEROUS, PersonalityTrait.FORGIVING],
            PersonalityTrait.LOYAL: [PersonalityTrait.LOYAL, PersonalityTrait.BRAVE, PersonalityTrait.GENEROUS],
            PersonalityTrait.TREACHEROUS: [PersonalityTrait.TREACHEROUS, PersonalityTrait.GREEDY, PersonalityTrait.VENGEFUL],
            PersonalityTrait.WISE: [PersonalityTrait.WISE, PersonalityTrait.CAUTIOUS, PersonalityTrait.PATIENT],
            PersonalityTrait.NAIVE: [PersonalityTrait.NAIVE, PersonalityTrait.OPEN, PersonalityTrait.GENEROUS],
            PersonalityTrait.AMBITIOUS: [PersonalityTrait.AMBITIOUS, PersonalityTrait.BRAVE, PersonalityTrait.ARROGANT],
            PersonalityTrait.CONTENT: [PersonalityTrait.CONTENT, PersonalityTrait.HUMBLE, PersonalityTrait.FORGIVING],
            PersonalityTrait.VENGEFUL: [PersonalityTrait.VENGEFUL, PersonalityTrait.ARROGANT, PersonalityTrait.TREACHEROUS],
            PersonalityTrait.FORGIVING: [PersonalityTrait.FORGIVING, PersonalityTrait.HUMBLE, PersonalityTrait.GENEROUS],
            PersonalityTrait.MYSTERIOUS: [PersonalityTrait.MYSTERIOUS, PersonalityTrait.WISE, PersonalityTrait.CAUTIOUS],
            PersonalityTrait.OPEN: [PersonalityTrait.OPEN, PersonalityTrait.NAIVE, PersonalityTrait.GENEROUS]
        }
        
        # 关系类型权重
        self.relationship_weights = {
            RelationshipType.FRIEND: 0.3,
            RelationshipType.ENEMY: 0.2,
            RelationshipType.MENTOR: 0.1,
            RelationshipType.DISCIPLE: 0.1,
            RelationshipType.FAMILY: 0.1,
            RelationshipType.LOVER: 0.05,
            RelationshipType.RIVAL: 0.1,
            RelationshipType.ALLY: 0.05
        }
    
    def create_relationship(self, character1: Character, character2: Character, 
                          relationship_type: RelationshipType, 
                          intimacy_level: int = 5, trust_level: int = 5) -> Relationship:
        """创建角色关系"""
        relationship_id = f"rel_{character1.id}_{character2.id}_{int(datetime.now().timestamp())}"
        
        # 根据性格计算关系强度
        intimacy_modifier = self._calculate_intimacy_modifier(character1, character2)
        trust_modifier = self._calculate_trust_modifier(character1, character2)
        
        final_intimacy = max(1, min(10, intimacy_level + intimacy_modifier))
        final_trust = max(1, min(10, trust_level + trust_modifier))
        
        # 生成关系描述
        description = self._generate_relationship_description(
            character1, character2, relationship_type, final_intimacy, final_trust
        )
        
        # 生成关系历史
        history = self._generate_relationship_history(
            character1, character2, relationship_type
        )
        
        return Relationship(
            id=relationship_id,
            character1_id=character1.id,
            character2_id=character2.id,
            relationship_type=relationship_type,
            intimacy_level=final_intimacy,
            trust_level=final_trust,
            description=description,
            history=history
        )
    
    def _calculate_intimacy_modifier(self, character1: Character, character2: Character) -> int:
        """计算亲密度修正值"""
        modifier = 0
        
        # 检查性格相性
        for trait1 in character1.personality:
            for trait2 in character2.personality:
                if trait2 in self.personality_compatibility.get(trait1, []):
                    modifier += 1
                elif trait1 in self.personality_compatibility.get(trait2, []):
                    modifier += 1
        
        # 检查共同目标
        common_goals = set()
        for goal1 in character1.goals:
            for goal2 in character2.goals:
                if goal1.get("type") == goal2.get("type"):
                    common_goals.add(goal1.get("type"))
        
        modifier += len(common_goals)
        
        # 检查组织关系
        if (character1.organization_id and character2.organization_id and 
            character1.organization_id == character2.organization_id):
            modifier += 2
        
        return modifier
    
    def _calculate_trust_modifier(self, character1: Character, character2: Character) -> int:
        """计算信任度修正值"""
        modifier = 0
        
        # 检查性格对信任的影响
        if PersonalityTrait.LOYAL in character1.personality:
            modifier += 1
        if PersonalityTrait.TREACHEROUS in character1.personality:
            modifier -= 2
        if PersonalityTrait.HONEST in character1.personality:
            modifier += 1
        if PersonalityTrait.DECEPTIVE in character1.personality:
            modifier -= 2
        
        # 检查背景相似性
        if character1.background and character2.background:
            # 简单的背景相似性检查
            if "宗门" in character1.background and "宗门" in character2.background:
                modifier += 1
            if "家族" in character1.background and "家族" in character2.background:
                modifier += 1
        
        return modifier
    
    def _generate_relationship_description(self, character1: Character, character2: Character,
                                        relationship_type: RelationshipType, 
                                        intimacy: int, trust: int) -> str:
        """生成关系描述"""
        descriptions = {
            RelationshipType.FRIEND: [
                f"{character1.name}和{character2.name}是好朋友，经常一起修炼和交流心得。",
                f"{character1.name}和{character2.name}关系密切，彼此信任，互相帮助。",
                f"{character1.name}和{character2.name}是生死之交，经历过许多危险。"
            ],
            RelationshipType.ENEMY: [
                f"{character1.name}和{character2.name}是死敌，彼此仇恨，势不两立。",
                f"{character1.name}和{character2.name}因为某些原因结下深仇大恨。",
                f"{character1.name}和{character2.name}是宿敌，多次交手，互有胜负。"
            ],
            RelationshipType.MENTOR: [
                f"{character1.name}是{character2.name}的师父，传授修炼心得和功法。",
                f"{character1.name}指导{character2.name}修炼，关系如师如父。",
                f"{character1.name}是{character2.name}的引路人，帮助其踏上修炼之路。"
            ],
            RelationshipType.DISCIPLE: [
                f"{character1.name}是{character2.name}的徒弟，尊敬师父，努力学习。",
                f"{character1.name}拜{character2.name}为师，跟随修炼。",
                f"{character1.name}是{character2.name}的弟子，传承其衣钵。"
            ],
            RelationshipType.FAMILY: [
                f"{character1.name}和{character2.name}是家人，血脉相连。",
                f"{character1.name}和{character2.name}是兄弟姐妹，从小一起长大。",
                f"{character1.name}和{character2.name}是父子/母女关系，亲情深厚。"
            ],
            RelationshipType.LOVER: [
                f"{character1.name}和{character2.name}是恋人，彼此深爱。",
                f"{character1.name}和{character2.name}是道侣，共同修炼，相伴一生。",
                f"{character1.name}和{character2.name}是夫妻，恩爱有加。"
            ],
            RelationshipType.RIVAL: [
                f"{character1.name}和{character2.name}是竞争对手，互相较劲。",
                f"{character1.name}和{character2.name}是劲敌，在修炼上互相超越。",
                f"{character1.name}和{character2.name}是宿敌，多次比试，难分高下。"
            ],
            RelationshipType.ALLY: [
                f"{character1.name}和{character2.name}是盟友，共同面对敌人。",
                f"{character1.name}和{character2.name}是合作伙伴，利益一致。",
                f"{character1.name}和{character2.name}是战友，并肩作战。"
            ]
        }
        
        base_descriptions = descriptions.get(relationship_type, ["关系复杂"])
        
        # 根据亲密度和信任度选择描述
        if intimacy >= 8 and trust >= 8:
            return base_descriptions[0] if len(base_descriptions) > 0 else "关系非常密切"
        elif intimacy >= 6 and trust >= 6:
            return base_descriptions[1] if len(base_descriptions) > 1 else "关系较好"
        else:
            return base_descriptions[2] if len(base_descriptions) > 2 else "关系一般"
    
    def _generate_relationship_history(self, character1: Character, character2: Character,
                                    relationship_type: RelationshipType) -> List[str]:
        """生成关系历史"""
        history = []
        
        if relationship_type == RelationshipType.FRIEND:
            history.extend([
                f"{character1.name}和{character2.name}在一次修炼中相遇",
                "两人发现彼此志趣相投，开始交往",
                "在一次危险中，{character1.name}救了{character2.name}",
                "两人结为好友，经常一起修炼"
            ])
        elif relationship_type == RelationshipType.ENEMY:
            history.extend([
                f"{character1.name}和{character2.name}因为利益冲突产生矛盾",
                "在一次比试中，{character1.name}击败了{character2.name}",
                "{character2.name}怀恨在心，发誓要报仇",
                "两人成为死敌，多次交手"
            ])
        elif relationship_type == RelationshipType.MENTOR:
            history.extend([
                f"{character2.name}拜{character1.name}为师",
                "{character1.name}开始传授{character2.name}修炼心得",
                "在师父的指导下，{character2.name}修为大进",
                "师徒关系日益深厚"
            ])
        
        return history
    
    def update_relationship(self, relationship: Relationship, 
                          new_intimacy: Optional[int] = None,
                          new_trust: Optional[int] = None,
                          new_type: Optional[RelationshipType] = None) -> Relationship:
        """更新关系"""
        if new_intimacy is not None:
            relationship.intimacy_level = max(1, min(10, new_intimacy))
        if new_trust is not None:
            relationship.trust_level = max(1, min(10, new_trust))
        if new_type is not None:
            relationship.relationship_type = new_type
        
        relationship.updated_at = datetime.now()
        
        # 更新描述
        # 这里需要重新生成描述，简化处理
        relationship.description = f"关系已更新，亲密度：{relationship.intimacy_level}，信任度：{relationship.trust_level}"
        
        return relationship
    
    def get_relationship_network(self, character: Character, 
                               relationships: List[Relationship]) -> Dict[str, Any]:
        """获取角色关系网络"""
        network = {
            "character_id": character.id,
            "character_name": character.name,
            "relationships": [],
            "network_stats": {
                "total_relationships": 0,
                "friends": 0,
                "enemies": 0,
                "mentors": 0,
                "disciples": 0,
                "family": 0,
                "lovers": 0,
                "rivals": 0,
                "allies": 0
            }
        }
        
        for rel in relationships:
            if rel.character1_id == character.id or rel.character2_id == character.id:
                network["relationships"].append({
                    "id": rel.id,
                    "other_character_id": (rel.character2_id if rel.character1_id == character.id 
                                          else rel.character1_id),
                    "type": rel.relationship_type.value,
                    "intimacy": rel.intimacy_level,
                    "trust": rel.trust_level,
                    "description": rel.description
                })
                
                # 更新统计
                network["network_stats"]["total_relationships"] += 1
                network["network_stats"][rel.relationship_type.value.lower()] += 1
        
        return network
    
    def find_relationship_path(self, character1: Character, character2: Character,
                             relationships: List[Relationship], max_depth: int = 3) -> List[List[str]]:
        """查找两个角色间的关系路径"""
        # 构建关系图
        graph = {}
        for rel in relationships:
            if rel.character1_id not in graph:
                graph[rel.character1_id] = []
            if rel.character2_id not in graph:
                graph[rel.character2_id] = []
            
            graph[rel.character1_id].append((rel.character2_id, rel.relationship_type))
            graph[rel.character2_id].append((rel.character1_id, rel.relationship_type))
        
        # 使用BFS查找路径
        paths = []
        queue = [(character1.id, [character1.id])]
        visited = set()
        
        while queue and len(paths) < 10:  # 限制路径数量
            current_id, path = queue.pop(0)
            
            if current_id == character2.id and len(path) > 1:
                paths.append(path)
                continue
            
            if len(path) >= max_depth + 1:
                continue
            
            if current_id in visited:
                continue
            
            visited.add(current_id)
            
            for neighbor_id, rel_type in graph.get(current_id, []):
                if neighbor_id not in path:  # 避免循环
                    queue.append((neighbor_id, path + [neighbor_id]))
        
        return paths
    
    def analyze_relationship_dynamics(self, relationships: List[Relationship]) -> Dict[str, Any]:
        """分析关系动态"""
        analysis = {
            "total_relationships": len(relationships),
            "relationship_types": {},
            "average_intimacy": 0,
            "average_trust": 0,
            "conflict_relationships": [],
            "strong_relationships": [],
            "weak_relationships": []
        }
        
        if not relationships:
            return analysis
        
        intimacy_sum = 0
        trust_sum = 0
        
        for rel in relationships:
            # 统计关系类型
            rel_type = rel.relationship_type.value
            analysis["relationship_types"][rel_type] = analysis["relationship_types"].get(rel_type, 0) + 1
            
            # 计算平均值
            intimacy_sum += rel.intimacy_level
            trust_sum += rel.trust_level
            
            # 分类关系
            if rel.relationship_type in [RelationshipType.ENEMY, RelationshipType.RIVAL]:
                analysis["conflict_relationships"].append(rel.id)
            elif rel.intimacy_level >= 8 and rel.trust_level >= 8:
                analysis["strong_relationships"].append(rel.id)
            elif rel.intimacy_level <= 3 or rel.trust_level <= 3:
                analysis["weak_relationships"].append(rel.id)
        
        analysis["average_intimacy"] = intimacy_sum / len(relationships)
        analysis["average_trust"] = trust_sum / len(relationships)
        
        return analysis
    
    def predict_relationship_evolution(self, relationship: Relationship) -> List[str]:
        """预测关系演变"""
        predictions = []
        
        # 根据当前关系类型和强度预测
        if relationship.relationship_type == RelationshipType.FRIEND:
            if relationship.intimacy_level >= 8 and relationship.trust_level >= 8:
                predictions.append("可能发展为道侣关系")
            elif relationship.intimacy_level <= 3:
                predictions.append("关系可能疏远")
        elif relationship.relationship_type == RelationshipType.RIVAL:
            if relationship.intimacy_level >= 7:
                predictions.append("可能化敌为友")
            elif relationship.intimacy_level <= 2:
                predictions.append("可能成为死敌")
        elif relationship.relationship_type == RelationshipType.MENTOR:
            if relationship.intimacy_level >= 8:
                predictions.append("师徒关系可能发展为父子关系")
            elif relationship.intimacy_level <= 3:
                predictions.append("师徒关系可能破裂")
        
        # 根据信任度预测
        if relationship.trust_level >= 8:
            predictions.append("信任度很高，关系稳定")
        elif relationship.trust_level <= 3:
            predictions.append("信任度很低，关系可能破裂")
        
        return predictions
