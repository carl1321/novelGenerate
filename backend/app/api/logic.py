"""
逻辑反思API路由
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from pydantic import BaseModel

from app.core.logic.service import LogicReflectionService
from app.core.logic.models import LogicCheckResult, LogicStatus, LogicCheckRequest as LogicCheckRequestModel

router = APIRouter()
logic_service = LogicReflectionService()


class LogicCheckRequest(BaseModel):
    """逻辑检查请求（兼容旧接口）"""
    content: str


class ReflectionReportRequest(BaseModel):
    """反思报告请求"""
    content: str


class LogicStatusUpdateRequest(BaseModel):
    """逻辑状态更新请求"""
    status: LogicStatus
    reason: str = None
    reviewer: str = "system"


@router.post("/check-logic")
async def check_logic_consistency(request: LogicCheckRequest):
    """检查逻辑一致性（兼容旧接口）"""
    try:
        result = await logic_service.check_logic_consistency(request.content)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/check-logic-detailed")
async def check_logic_detailed(request: LogicCheckRequestModel):
    """详细逻辑检查（新接口）"""
    try:
        result = await logic_service.check_logic_detailed(
            content=request.content,
            checked_by=request.check_type
        )
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


@router.get("/logic-statuses")
async def get_logic_statuses():
    """获取所有逻辑状态"""
    return {
        "statuses": [
            {"value": status.value, "label": status.value}
            for status in LogicStatus
        ]
    }
