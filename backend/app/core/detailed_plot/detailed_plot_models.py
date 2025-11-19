"""
详细剧情相关模型
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum
from app.core.logic.models import LogicCheckResult, LogicStatus
from typing import Union


class DetailedPlotStatus(str, Enum):
    """详细剧情状态枚举"""
    DRAFT = "草稿"
    COMPLETED = "已完成"
    PUBLISHED = "已发布"
    LOGIC_CHECKING = "逻辑检查中"
    LOGIC_WARNING = "逻辑警告"
    LOGIC_ERROR = "逻辑错误"
    MANUAL_REVIEW = "人工审核"


class ScoringStatus(str, Enum):
    """评分状态枚举"""
    NOT_SCORED = "未评分"
    SCORING = "评分中"
    COMPLETED = "已完成"
    FAILED = "评分失败"


class DetailedPlot(BaseModel):
    """详细剧情模型"""
    id: str = Field(..., description="详细剧情ID")
    chapter_outline_id: str = Field(..., description="所属章节大纲ID")
    plot_outline_id: str = Field(..., description="所属剧情大纲ID")
    title: str = Field(..., description="详细剧情标题")
    content: str = Field(..., description="详细剧情内容")
    word_count: int = Field(default=0, description="字数统计")
    status: DetailedPlotStatus = Field(default=DetailedPlotStatus.DRAFT, description="状态")
    logic_check_result: Optional[LogicCheckResult] = Field(default=None, description="逻辑检查结果")
    logic_status: Optional[LogicStatus] = Field(default=None, description="逻辑检查状态")
    # 评分智能体相关字段
    scoring_status: Optional[ScoringStatus] = Field(default=ScoringStatus.NOT_SCORED, description="评分状态")
    total_score: Optional[float] = Field(default=None, ge=0.0, le=100.0, description="总分")
    scoring_result: Optional[Dict[str, Any]] = Field(default=None, description="详细评分结果")
    scoring_feedback: Optional[str] = Field(default=None, description="评分反馈")
    scored_at: Optional[datetime] = Field(default=None, description="评分时间")
    scored_by: Optional[str] = Field(default=None, description="评分者")
    created_at: Optional[datetime] = Field(default=None, description="创建时间")
    updated_at: Optional[datetime] = Field(default=None, description="更新时间")


class DetailedPlotRequest(BaseModel):
    """详细剧情生成请求"""
    chapter_outline_id: str = Field(..., description="章节大纲ID")
    plot_outline_id: str = Field(..., description="剧情大纲ID")
    title: str = Field(..., description="详细剧情标题")
    additional_requirements: Optional[str] = Field(None, description="额外要求")
    enable_logic_check: bool = Field(default=True, description="是否启用逻辑检查")


class DetailedPlotResponse(BaseModel):
    """详细剧情响应"""
    id: str = Field(..., description="详细剧情ID")
    chapter_outline_id: str = Field(..., description="所属章节大纲ID")
    plot_outline_id: str = Field(..., description="所属剧情大纲ID")
    title: str = Field(..., description="详细剧情标题")
    content: str = Field(..., description="详细剧情内容")
    word_count: int = Field(default=0, description="字数统计")
    status: DetailedPlotStatus = Field(default=DetailedPlotStatus.DRAFT, description="状态")
    logic_check_result: Optional[LogicCheckResult] = Field(default=None, description="逻辑检查结果")
    logic_status: Optional[LogicStatus] = Field(default=None, description="逻辑检查状态")
    # 评分智能体相关字段
    scoring_status: Optional[ScoringStatus] = Field(default=ScoringStatus.NOT_SCORED, description="评分状态")
    total_score: Optional[float] = Field(default=None, ge=0.0, le=100.0, description="总分")
    scoring_result: Optional[Dict[str, Any]] = Field(default=None, description="详细评分结果")
    scoring_feedback: Optional[str] = Field(default=None, description="评分反馈")
    scored_at: Optional[datetime] = Field(default=None, description="评分时间")
    scored_by: Optional[str] = Field(default=None, description="评分者")
    created_at: Optional[datetime] = Field(default=None, description="创建时间")
    updated_at: Optional[datetime] = Field(default=None, description="更新时间")


class DetailedPlotListResponse(BaseModel):
    """详细剧情列表响应"""
    detailed_plots: List[DetailedPlotResponse] = Field(..., description="详细剧情列表")
    total: int = Field(..., description="总数")
    page: int = Field(..., description="页码")
    page_size: int = Field(..., description="每页大小")
