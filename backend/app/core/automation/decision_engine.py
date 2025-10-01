"""
智能决策引擎
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum


class RewriteStrategy(str, Enum):
    """重写策略枚举"""
    NONE = "none"
    LOGIC_FIX = "logic_fix"
    CONFLICT_ENHANCEMENT = "conflict_enhancement"
    CHARACTER_DEVELOPMENT = "character_development"
    PLOT_REFINEMENT = "plot_refinement"
    MINOR_ADJUSTMENT = "minor_adjustment"
    MAJOR_REWRITE = "major_rewrite"


@dataclass
class DecisionResult:
    """决策结果"""
    should_rewrite: bool
    strategy: RewriteStrategy
    priority: int  # 1-10, 10为最高优先级
    reason: str
    target_modules: List[str]  # 需要重写的模块
    confidence: float  # 决策置信度 0-1


class IntelligentDecisionEngine:
    """智能决策引擎"""
    
    def __init__(self):
        # 评分阈值配置
        self.thresholds = {
            "excellent": 8.5,
            "good": 7.0,
            "acceptable": 6.0,
            "poor": 4.0
        }
        
        # 各维度权重
        self.dimension_weights = {
            "logic_consistency": 0.3,
            "dramatic_conflict": 0.2,
            "character_consistency": 0.2,
            "writing_quality": 0.15,
            "innovation": 0.1,
            "user_preference": 0.05
        }
    
    async def analyze_scores(self, scores: Dict[str, Any]) -> DecisionResult:
        """分析评分并做出决策"""
        total_score = scores.get('total_score', 0)
        dimension_scores = scores.get('scores', {})
        
        # 分析各维度得分
        low_scores = []
        for dimension, score in dimension_scores.items():
            if score < self.thresholds['acceptable']:
                low_scores.append((dimension, score))
        
        # 按分数排序，找出最需要改进的维度
        low_scores.sort(key=lambda x: x[1])
        
        # 决策逻辑
        if total_score >= self.thresholds['excellent']:
            return DecisionResult(
                should_rewrite=False,
                strategy=RewriteStrategy.NONE,
                priority=1,
                reason="内容质量优秀，无需重写",
                target_modules=[],
                confidence=0.9
            )
        
        elif total_score >= self.thresholds['good']:
            # 检查是否有明显的问题维度
            if low_scores and low_scores[0][1] < self.thresholds['poor']:
                strategy, modules = self._get_strategy_for_dimension(low_scores[0][0])
                return DecisionResult(
                    should_rewrite=True,
                    strategy=strategy,
                    priority=6,
                    reason=f"总体质量良好，但{low_scores[0][0]}需要改进",
                    target_modules=modules,
                    confidence=0.7
                )
            else:
                return DecisionResult(
                    should_rewrite=False,
                    strategy=RewriteStrategy.NONE,
                    priority=2,
                    reason="内容质量良好，无需重写",
                    target_modules=[],
                    confidence=0.8
                )
        
        elif total_score >= self.thresholds['acceptable']:
            # 需要改进，但问题不严重
            if low_scores:
                strategy, modules = self._get_strategy_for_dimension(low_scores[0][0])
                return DecisionResult(
                    should_rewrite=True,
                    strategy=strategy,
                    priority=7,
                    reason=f"内容可接受，但{low_scores[0][0]}需要改进",
                    target_modules=modules,
                    confidence=0.8
                )
            else:
                return DecisionResult(
                    should_rewrite=True,
                    strategy=RewriteStrategy.MINOR_ADJUSTMENT,
                    priority=5,
                    reason="内容可接受，但整体需要小幅调整",
                    target_modules=['world', 'character', 'plot'],
                    confidence=0.6
                )
        
        else:
            # 内容质量较差，需要大幅改进
            if len(low_scores) >= 3:
                return DecisionResult(
                    should_rewrite=True,
                    strategy=RewriteStrategy.MAJOR_REWRITE,
                    priority=10,
                    reason="内容质量较差，需要大幅重写",
                    target_modules=['world', 'character', 'plot'],
                    confidence=0.9
                )
            elif low_scores:
                strategy, modules = self._get_strategy_for_dimension(low_scores[0][0])
                return DecisionResult(
                    should_rewrite=True,
                    strategy=strategy,
                    priority=9,
                    reason=f"内容质量较差，{low_scores[0][0]}需要重点改进",
                    target_modules=modules,
                    confidence=0.8
                )
            else:
                return DecisionResult(
                    should_rewrite=True,
                    strategy=RewriteStrategy.MAJOR_REWRITE,
                    priority=8,
                    reason="内容质量较差，需要全面改进",
                    target_modules=['world', 'character', 'plot'],
                    confidence=0.7
                )
    
    def _get_strategy_for_dimension(self, dimension: str) -> tuple[RewriteStrategy, List[str]]:
        """根据维度获取重写策略"""
        strategy_map = {
            "logic_consistency": (RewriteStrategy.LOGIC_FIX, ['world', 'character', 'plot']),
            "dramatic_conflict": (RewriteStrategy.CONFLICT_ENHANCEMENT, ['plot']),
            "character_consistency": (RewriteStrategy.CHARACTER_DEVELOPMENT, ['character']),
            "writing_quality": (RewriteStrategy.MINOR_ADJUSTMENT, ['world', 'character', 'plot']),
            "innovation": (RewriteStrategy.PLOT_REFINEMENT, ['plot', 'world']),
            "user_preference": (RewriteStrategy.MINOR_ADJUSTMENT, ['world', 'character', 'plot'])
        }
        
        return strategy_map.get(dimension, (RewriteStrategy.MINOR_ADJUSTMENT, ['world', 'character', 'plot']))
    
    async def determine_character_count(self, world_view: Dict[str, Any]) -> int:
        """智能决定角色数量"""
        # 分析世界观复杂度
        complexity_factors = []
        
        # 检查地点数量
        locations = world_view.get('locations', [])
        complexity_factors.append(len(locations))
        
        # 检查组织数量
        organizations = world_view.get('organizations', [])
        complexity_factors.append(len(organizations))
        
        # 检查功法数量
        techniques = world_view.get('techniques', [])
        complexity_factors.append(len(techniques))
        
        # 计算复杂度分数
        complexity_score = sum(complexity_factors)
        
        # 根据复杂度决定角色数量
        if complexity_score >= 20:
            return 5  # 高复杂度，需要更多角色
        elif complexity_score >= 10:
            return 4  # 中等复杂度
        elif complexity_score >= 5:
            return 3  # 低复杂度
        else:
            return 2  # 简单设定，最少角色
    
    async def should_continue_iteration(self, iteration: int, scores: Dict[str, Any], 
                                      max_iterations: int = 5) -> bool:
        """判断是否应该继续迭代"""
        # 达到最大迭代次数
        if iteration >= max_iterations:
            return False
        
        # 内容质量已经很好
        total_score = scores.get('total_score', 0)
        if total_score >= self.thresholds['excellent']:
            return False
        
        # 检查是否有明显改进空间
        dimension_scores = scores.get('scores', {})
        low_scores = [score for score in dimension_scores.values() if score < self.thresholds['good']]
        
        # 如果还有多个维度需要改进，继续迭代
        return len(low_scores) > 1
    
    async def get_optimization_priority(self, scores: Dict[str, Any]) -> List[str]:
        """获取优化优先级列表"""
        dimension_scores = scores.get('scores', {})
        
        # 按分数排序，分数越低优先级越高
        sorted_dimensions = sorted(
            dimension_scores.items(),
            key=lambda x: x[1]
        )
        
        return [dimension for dimension, score in sorted_dimensions]
    
    async def calculate_confidence(self, scores: Dict[str, Any], 
                                 previous_scores: Optional[Dict[str, Any]] = None) -> float:
        """计算决策置信度"""
        total_score = scores.get('total_score', 0)
        
        # 基础置信度基于总分
        base_confidence = min(total_score / 10.0, 1.0)
        
        # 如果有历史分数，考虑改进趋势
        if previous_scores:
            previous_total = previous_scores.get('total_score', 0)
            improvement = total_score - previous_total
            
            # 如果有改进，增加置信度
            if improvement > 0:
                base_confidence += min(improvement / 10.0, 0.2)
            # 如果退步，降低置信度
            elif improvement < -1:
                base_confidence -= 0.1
        
        return max(0.0, min(1.0, base_confidence))
