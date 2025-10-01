"""
逻辑反思API路由
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from pydantic import BaseModel

from app.core.logic.service import LogicReflectionService

router = APIRouter()
logic_service = LogicReflectionService()


class LogicCheckRequest(BaseModel):
    """逻辑检查请求"""
    content: Dict[str, Any]


class ReflectionReportRequest(BaseModel):
    """反思报告请求"""
    content: Dict[str, Any]


@router.post("/check-logic")
async def check_logic_consistency(request: LogicCheckRequest):
    """检查逻辑一致性"""
    try:
        result = await logic_service.check_logic_consistency(request.content)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-report")
async def generate_reflection_report(request: ReflectionReportRequest):
    """生成反思报告"""
    try:
        result = await logic_service.generate_reflection_report(request.content)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
