"""
逻辑检查相关数据模型
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class LogicStatus(str, Enum):
    """逻辑检查状态枚举"""
    PENDING = "待检查"
    CHECKING = "检查中"
    PASSED = "通过"
    WARNING = "警告"
    FAILED = "未通过"
    MANUAL_REVIEW = "人工审核"


class LogicIssueSeverity(str, Enum):
    """逻辑问题严重程度枚举"""
    HIGH = "高"
    MEDIUM = "中"
    LOW = "低"


class LogicDimension(str, Enum):
    """逻辑检查维度枚举"""
    CULTIVATION_LOGIC = "修炼逻辑"
    CHARACTER_LOGIC = "角色逻辑"
    WORLD_LOGIC = "世界观逻辑"
    TIMELINE_LOGIC = "时间线逻辑"
    CAUSALITY_LOGIC = "因果关系逻辑"


class LogicIssue(BaseModel):
    """逻辑问题模型"""
    category: str = Field(..., description="问题分类")
    severity: LogicIssueSeverity = Field(..., description="严重程度")
    description: str = Field(..., description="问题描述")
    location: str = Field("", description="问题位置")
    suggestion: str = Field("", description="修改建议")
    auto_fixable: bool = Field(False, description="是否可自动修复")
    dimension: LogicDimension = Field(..., description="所属维度")


class LogicDimensionScore(BaseModel):
    """逻辑维度评分模型"""
    dimension: LogicDimension = Field(..., description="维度名称")
    score: float = Field(0.0, ge=0.0, le=100.0, description="维度分数")
    weight: float = Field(0.0, ge=0.0, le=1.0, description="维度权重")
    issues_count: int = Field(0, description="问题数量")


class LogicCheckResult(BaseModel):
    """逻辑检查结果模型"""
    overall_status: LogicStatus = Field(..., description="整体状态")
    logic_score: float = Field(0.0, ge=0.0, le=100.0, description="逻辑总分")
    issues_found: List[LogicIssue] = Field(default_factory=list, description="发现的问题")
    dimension_scores: Dict[str, float] = Field(default_factory=dict, description="各维度评分")
    summary: str = Field("", description="检查总结")
    recommendations: List[str] = Field(default_factory=list, description="改进建议")
    checked_at: datetime = Field(default_factory=datetime.now, description="检查时间")
    checked_by: str = Field("system", description="检查者")


class LogicCheckHistory(BaseModel):
    """逻辑检查历史记录模型"""
    id: str = Field(..., description="记录ID")
    detailed_plot_id: str = Field(..., description="详细剧情ID")
    check_type: str = Field(..., description="检查类型：auto/manual")
    logic_score: float = Field(..., description="逻辑分数")
    overall_status: LogicStatus = Field(..., description="检查状态")
    issues_count: int = Field(0, description="问题数量")
    checked_by: str = Field(..., description="检查者")
    checked_at: datetime = Field(default_factory=datetime.now, description="检查时间")
    result: Optional[LogicCheckResult] = Field(None, description="检查结果详情")


class LogicScoringRules(BaseModel):
    """逻辑评分规则模型"""
    dimension_weights: Dict[LogicDimension, float] = Field(
        default_factory=lambda: {
            LogicDimension.CULTIVATION_LOGIC: 0.25,
            LogicDimension.CHARACTER_LOGIC: 0.20,
            LogicDimension.WORLD_LOGIC: 0.20,
            LogicDimension.TIMELINE_LOGIC: 0.15,
            LogicDimension.CAUSALITY_LOGIC: 0.20
        },
        description="各维度权重"
    )
    severity_penalties: Dict[LogicIssueSeverity, float] = Field(
        default_factory=lambda: {
            LogicIssueSeverity.HIGH: 20.0,
            LogicIssueSeverity.MEDIUM: 10.0,
            LogicIssueSeverity.LOW: 5.0
        },
        description="严重程度扣分"
    )
    status_thresholds: Dict[str, float] = Field(
        default_factory=lambda: {
            "通过": 80.0,
            "警告": 60.0,
            "未通过": 0.0
        },
        description="状态判断阈值"
    )


class LogicCheckRequest(BaseModel):
    """逻辑检查请求模型"""
    content: str = Field(..., description="待检查内容")
    check_type: str = Field("auto", description="检查类型")
    force_recheck: bool = Field(False, description="是否强制重新检查")


class LogicStatusUpdateRequest(BaseModel):
    """逻辑状态更新请求模型"""
    status: LogicStatus = Field(..., description="新状态")
    reason: Optional[str] = Field(None, description="状态变更原因")
    reviewer: str = Field(..., description="审核人")
