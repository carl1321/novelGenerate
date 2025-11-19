"""
逻辑检查引擎
"""
import json
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime

from app.core.logic.models import (
    LogicCheckResult, LogicIssue, LogicDimension, LogicIssueSeverity,
    LogicStatus, LogicDimensionScore, LogicScoringRules
)
from app.utils.llm_client import get_llm_client
from app.utils.prompt_manager import PromptManager
from app.utils.dynamic_parser import dynamic_parser


class LogicIssueClassifier:
    """逻辑问题分类器"""
    
    def __init__(self):
        self.category_keywords = {
            "修炼体系": ["境界", "功法", "灵根", "修炼", "天劫", "突破"],
            "角色行为": ["性格", "行为", "决定", "能力", "关系", "成长"],
            "世界观": ["规则", "地理", "历史", "文化", "门派", "组织"],
            "时间线": ["时间", "顺序", "年龄", "进度", "事件"],
            "因果关系": ["原因", "结果", "动机", "冲突", "解决"]
        }
        
        self.severity_keywords = {
            LogicIssueSeverity.HIGH: ["严重", "错误", "矛盾", "不可能", "违反"],
            LogicIssueSeverity.MEDIUM: ["问题", "不合理", "不当", "需要"],
            LogicIssueSeverity.LOW: ["建议", "可以", "考虑", "优化"]
        }
    
    def classify_issue(self, issue_text: str) -> LogicIssue:
        """分类逻辑问题"""
        category = self._determine_category(issue_text)
        severity = self._determine_severity(issue_text)
        dimension = self._map_category_to_dimension(category)
        
        return LogicIssue(
            category=category,
            severity=severity,
            description=issue_text,
            dimension=dimension,
            auto_fixable=self._is_auto_fixable(issue_text)
        )
    
    def _determine_category(self, text: str) -> str:
        """确定问题分类"""
        for category, keywords in self.category_keywords.items():
            if any(keyword in text for keyword in keywords):
                return category
        return "其他"
    
    def _determine_severity(self, text: str) -> LogicIssueSeverity:
        """确定问题严重程度"""
        for severity, keywords in self.severity_keywords.items():
            if any(keyword in text for keyword in keywords):
                return severity
        return LogicIssueSeverity.MEDIUM
    
    def _map_category_to_dimension(self, category: str) -> LogicDimension:
        """将分类映射到维度"""
        mapping = {
            "修炼体系": LogicDimension.CULTIVATION_LOGIC,
            "角色行为": LogicDimension.CHARACTER_LOGIC,
            "世界观": LogicDimension.WORLD_LOGIC,
            "时间线": LogicDimension.TIMELINE_LOGIC,
            "因果关系": LogicDimension.CAUSALITY_LOGIC
        }
        return mapping.get(category, LogicDimension.CAUSALITY_LOGIC)
    
    def _is_auto_fixable(self, text: str) -> bool:
        """判断是否可自动修复"""
        auto_fixable_keywords = ["格式", "标点", "用词", "表达"]
        return any(keyword in text for keyword in auto_fixable_keywords)


class LogicScoringEngine:
    """逻辑评分引擎"""
    
    def __init__(self, rules: Optional[LogicScoringRules] = None):
        self.rules = rules or LogicScoringRules()
    
    def calculate_dimension_scores(self, issues: List[LogicIssue]) -> Dict[str, float]:
        """计算各维度分数"""
        dimension_issues = {}
        
        # 按维度分组问题
        for issue in issues:
            dimension = issue.dimension.value
            if dimension not in dimension_issues:
                dimension_issues[dimension] = []
            dimension_issues[dimension].append(issue)
        
        # 计算各维度分数
        dimension_scores = {}
        for dimension in LogicDimension:
            dimension_name = dimension.value
            issues_in_dimension = dimension_issues.get(dimension_name, [])
            
            # 基础分数100分
            base_score = 100.0
            
            # 根据问题严重程度扣分
            for issue in issues_in_dimension:
                penalty = self.rules.severity_penalties.get(issue.severity, 0.0)
                base_score -= penalty
            
            # 确保分数不低于0
            dimension_scores[dimension_name] = max(0.0, base_score)
        
        return dimension_scores
    
    def calculate_overall_score(self, dimension_scores: Dict[str, float]) -> float:
        """计算总分"""
        total_score = 0.0
        total_weight = 0.0
        
        for dimension in LogicDimension:
            dimension_name = dimension.value
            score = dimension_scores.get(dimension_name, 100.0)
            weight = self.rules.dimension_weights.get(dimension, 0.0)
            
            total_score += score * weight
            total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0.0
    
    def determine_status(self, score: float, issues: List[LogicIssue]) -> LogicStatus:
        """根据分数和问题确定状态"""
        # 有严重问题直接判为未通过
        if any(issue.severity == LogicIssueSeverity.HIGH for issue in issues):
            return LogicStatus.FAILED
        
        # 根据分数判断
        if score >= self.rules.status_thresholds["通过"]:  # >= 80分
            return LogicStatus.PASSED
        elif score >= self.rules.status_thresholds["警告"]:  # 60-79分
            return LogicStatus.WARNING
        else:  # < 60分
            return LogicStatus.FAILED


class LogicCheckEngine:
    """逻辑检查引擎"""
    
    def __init__(self):
        self.llm_client = get_llm_client()
        self.prompt_manager = PromptManager()
        self.classifier = LogicIssueClassifier()
        self.scoring_engine = LogicScoringEngine()
    
    async def check_logic(self, content: str, checked_by: str = "system") -> LogicCheckResult:
        """执行逻辑检查"""
        try:
            # 1. 调用LLM进行逻辑分析
            prompt = self.prompt_manager.get_logic_check_prompt(content)
            response = await self.llm_client.generate_text(
                prompt=prompt,
                temperature=0.3,
                max_tokens=20000
            )
            
            # 2. 解析LLM响应
            analysis_data = self._parse_llm_response(response)
            
            # 3. 分类问题
            issues = []
            for issue_data in analysis_data.get("issues_found", []):
                issue = self.classifier.classify_issue(issue_data.get("description", ""))
                # 更新从LLM解析的详细信息
                issue.location = issue_data.get("location", "")
                issue.suggestion = issue_data.get("suggestion", "")
                issues.append(issue)
            
            # 4. 计算各维度分数
            dimension_scores = self.scoring_engine.calculate_dimension_scores(issues)
            
            # 5. 计算总分
            overall_score = self.scoring_engine.calculate_overall_score(dimension_scores)
            
            # 6. 判断状态
            status = self.scoring_engine.determine_status(overall_score, issues)
            
            # 7. 生成建议
            recommendations = analysis_data.get("recommendations", [])
            
            return LogicCheckResult(
                overall_status=status,
                logic_score=overall_score,
                issues_found=issues,
                dimension_scores=dimension_scores,
                summary=analysis_data.get("summary", ""),
                recommendations=recommendations,
                checked_at=datetime.now(),
                checked_by=checked_by
            )
            
        except Exception as e:
            # 返回错误结果
            return LogicCheckResult(
                overall_status=LogicStatus.FAILED,
                logic_score=0.0,
                issues_found=[],
                dimension_scores={},
                summary=f"逻辑检查失败: {str(e)}",
                recommendations=["请检查内容格式或联系管理员"],
                checked_at=datetime.now(),
                checked_by=checked_by
            )
    
    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """解析LLM响应"""
        try:
            # 尝试解析JSON
            if response.strip().startswith('{'):
                return json.loads(response)
            
            # 如果不是JSON格式，尝试提取JSON部分
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            
            # 如果都失败，返回默认结构
            return {
                "overall_status": "无法解析",
                "issues_found": [],
                "dimension_scores": {},
                "summary": "LLM响应格式错误",
                "recommendations": []
            }
            
        except Exception as e:
            return {
                "overall_status": "解析错误",
                "issues_found": [],
                "dimension_scores": {},
                "summary": f"解析LLM响应失败: {str(e)}",
                "recommendations": []
            }
    
    def generate_recommendations(self, issues: List[LogicIssue]) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        # 按严重程度分组问题
        high_issues = [issue for issue in issues if issue.severity == LogicIssueSeverity.HIGH]
        medium_issues = [issue for issue in issues if issue.severity == LogicIssueSeverity.MEDIUM]
        
        if high_issues:
            recommendations.append(f"发现{len(high_issues)}个严重问题，需要优先处理")
        
        if medium_issues:
            recommendations.append(f"发现{len(medium_issues)}个中等问题，建议改进")
        
        # 按维度给出建议
        dimension_issues = {}
        for issue in issues:
            dimension = issue.dimension.value
            if dimension not in dimension_issues:
                dimension_issues[dimension] = 0
            dimension_issues[dimension] += 1
        
        for dimension, count in dimension_issues.items():
            if count > 0:
                recommendations.append(f"{dimension}方面发现{count}个问题，需要重点关注")
        
        return recommendations
