"""
评分系统API路由
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from pydantic import BaseModel

from app.core.scoring.service import ScoringService

router = APIRouter()
scoring_service = ScoringService()


class ScoringRequest(BaseModel):
    """评分请求"""
    content: Dict[str, Any]


@router.post("/score")
async def score_content(request: ScoringRequest):
    """对内容进行多维度评分"""
    try:
        result = await scoring_service.score_content(request.content)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
