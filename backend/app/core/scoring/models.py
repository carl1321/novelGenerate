"""
评分智能体数据模型
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field


class ScoringType(str, Enum):
    """评分类型枚举"""
    INTELLIGENT = "intelligent"
    MANUAL = "manual"
    AUTO = "auto"


class ScoringLevel(str, Enum):
    """评分等级枚举"""
    EXCELLENT = "优秀"
    GOOD = "良好"
    AVERAGE = "一般"
    POOR = "较差"
    VERY_POOR = "很差"


class DimensionMapping(BaseModel):
    """维度映射模型"""
    id: str = Field(..., description="维度ID")
    technical_name: str = Field(..., description="技术名称")
    display_name: str = Field(..., description="显示名称")
    description: Optional[str] = Field(None, description="维度描述")
    color_code: Optional[str] = Field(None, description="颜色代码")
    weight: float = Field(1.0, description="权重")
    is_active: bool = Field(True, description="是否启用")


class ScoringDimension(BaseModel):
    """评分维度详情模型"""
    id: str = Field(..., description="维度详情ID")
    scoring_record_id: str = Field(..., description="评分记录ID")
    dimension_name: str = Field(..., description="维度技术名称")
    dimension_display_name: str = Field(..., description="维度显示名称")
    score: float = Field(..., ge=0, le=100, description="维度分数")
    feedback: Optional[str] = Field(None, description="维度反馈")
    weight: float = Field(1.0, description="权重")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")


class ScoringRecord(BaseModel):
    """评分记录主模型"""
    id: str = Field(..., description="评分记录ID")
    detailed_plot_id: str = Field(..., description="详细剧情ID")
    scorer_id: str = Field("system", description="评分者ID")
    scoring_type: ScoringType = Field(ScoringType.INTELLIGENT, description="评分类型")
    total_score: float = Field(..., ge=0, le=100, description="总分")
    scoring_level: ScoringLevel = Field(..., description="评分等级")
    overall_feedback: Optional[str] = Field(None, description="总体反馈")
    improvement_suggestions: Optional[List[str]] = Field(None, description="改进建议")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")

    def calculate_scoring_level(self) -> ScoringLevel:
        """计算评分等级"""
        if self.total_score >= 90:
            return ScoringLevel.EXCELLENT
        elif self.total_score >= 80:
            return ScoringLevel.GOOD
        elif self.total_score >= 70:
            return ScoringLevel.AVERAGE
        elif self.total_score >= 60:
            return ScoringLevel.POOR
        else:
            return ScoringLevel.VERY_POOR


class ScoringResult(BaseModel):
    """评分结果完整模型"""
    scoring_record: ScoringRecord = Field(..., description="评分记录")
    dimensions: List[ScoringDimension] = Field(..., description="各维度详情")


class ScoringRequest(BaseModel):
    """评分请求模型"""
    detailed_plot_id: str = Field(..., description="详细剧情ID")
    scorer_id: str = Field("system", description="评分者ID")
    scoring_type: ScoringType = Field(ScoringType.INTELLIGENT, description="评分类型")


class ScoringCreateRequest(BaseModel):
    """创建评分请求模型"""
    detailed_plot_id: str = Field(..., description="详细剧情ID")
    scorer_id: str = Field("system", description="评分者ID")
    scoring_type: ScoringType = Field(ScoringType.INTELLIGENT, description="评分类型")
    detailed_plot_content: str = Field(..., description="详细剧情内容")


class ScoringResponse(BaseModel):
    """评分响应模型"""
    scoring_record: ScoringRecord = Field(..., description="评分记录")
    dimensions: List[ScoringDimension] = Field(..., description="各维度详情")
    overall_feedback: str = Field(..., description="总体反馈")
    improvement_suggestions: List[str] = Field(..., description="改进建议")


class ScoringListResponse(BaseModel):
    """评分列表响应模型"""
    scoring_records: List[ScoringRecord] = Field(..., description="评分记录列表")
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页")
    page_size: int = Field(..., description="每页大小")


class DimensionScore(BaseModel):
    """维度分数模型（用于前端显示）"""
    dimension_name: str = Field(..., description="维度技术名称")
    dimension_display_name: str = Field(..., description="维度显示名称")
    score: float = Field(..., ge=0, le=100, description="分数")
    feedback: Optional[str] = Field(None, description="反馈")
    color_code: Optional[str] = Field(None, description="颜色代码")
    weight: float = Field(1.0, description="权重")


class ScoringDisplayData(BaseModel):
    """评分显示数据模型"""
    total_score: float = Field(..., description="总分")
    scoring_level: ScoringLevel = Field(..., description="评分等级")
    overall_feedback: str = Field(..., description="总体反馈")
    improvement_suggestions: List[str] = Field(..., description="改进建议")
    dimensions: List[DimensionScore] = Field(..., description="各维度分数")
