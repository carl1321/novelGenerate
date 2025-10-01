"""
进化重写API路由
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from pydantic import BaseModel

from app.core.evolution.service import EvolutionService

router = APIRouter()
evolution_service = EvolutionService()


class ProblemAnalysisRequest(BaseModel):
    """问题分析请求"""
    content: Dict[str, Any]
    scores: Dict[str, Any]


class RewriteSuggestionRequest(BaseModel):
    """重写建议请求"""
    content: Dict[str, Any]
    problems: Dict[str, Any]


class ABTestRequest(BaseModel):
    """A/B测试请求"""
    content: Dict[str, Any]
    suggestions: Dict[str, Any]


class ContentOptimizationRequest(BaseModel):
    """内容优化请求"""
    content: Dict[str, Any]
    target_scores: Dict[str, Any]


@router.post("/analyze-problems")
async def analyze_problems(request: ProblemAnalysisRequest):
    """分析内容问题"""
    try:
        result = await evolution_service.analyze_problems(request.content, request.scores)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-rewrite-suggestions")
async def generate_rewrite_suggestions(request: RewriteSuggestionRequest):
    """生成重写建议"""
    try:
        result = await evolution_service.generate_rewrite_suggestions(request.content, request.problems)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-ab-test-versions")
async def generate_ab_test_versions(request: ABTestRequest):
    """生成A/B测试版本"""
    try:
        result = await evolution_service.generate_ab_test_versions(request.content, request.suggestions)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/optimize-content")
async def optimize_content(request: ContentOptimizationRequest):
    """优化内容"""
    try:
        result = await evolution_service.optimize_content(request.content, request.target_scores)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
