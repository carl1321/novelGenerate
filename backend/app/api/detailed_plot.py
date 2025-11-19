"""
详细剧情API端点
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from datetime import datetime

from app.core.detailed_plot.detailed_plot_models import (
    DetailedPlotRequest, DetailedPlotResponse, DetailedPlotListResponse, DetailedPlotStatus
)
from pydantic import BaseModel, Field

class CorrectionRequest(BaseModel):
    """修正请求模型"""
    correction_prompt: Optional[str] = Field(default="", description="用户修正要求")

from app.core.detailed_plot.detailed_plot_engine import DetailedPlotEngine
from app.core.detailed_plot.detailed_plot_database import DetailedPlotDatabase
from app.core.chapter_engine.chapter_database import ChapterOutlineDatabase
from app.core.plot_engine.plot_database import PlotOutlineDatabase
from app.core.logic.service import LogicReflectionService
from app.core.logic.models import LogicStatus
from app.core.scoring.intelligent_scoring_service import IntelligentScoringService
from app.core.evolution.evolution_service import evolution_service
from app.core.correction.correction_service import correction_service
from app.utils.file_writer import FileWriter
from app.utils.logger import error_log, debug_log

router = APIRouter()

# 初始化服务
detailed_plot_engine = DetailedPlotEngine()
detailed_plot_database = DetailedPlotDatabase()
logic_service = LogicReflectionService()
scoring_service = IntelligentScoringService()
chapter_database = ChapterOutlineDatabase()
plot_database = PlotOutlineDatabase()
file_writer = FileWriter()


@router.post("/detailed-plots", response_model=DetailedPlotResponse)
async def create_detailed_plot(request: DetailedPlotRequest):
    """生成详细剧情"""
    print(f"🚀 [DEBUG] 开始生成详细剧情")
    print(f"📋 [DEBUG] 请求参数: chapter_outline_id={request.chapter_outline_id}, plot_outline_id={request.plot_outline_id}, title={request.title}")
    
    try:
        print(f"🔍 [DEBUG] 步骤1: 调用详细剧情生成引擎...")
        detailed_plot = await detailed_plot_engine.generate_detailed_plot(request)
        print(f"✅ [DEBUG] 详细剧情生成成功: {detailed_plot.id}")
        
        print(f"🔍 [DEBUG] 步骤2: 构建响应对象...")
        response = DetailedPlotResponse(
            id=detailed_plot.id,
            chapter_outline_id=detailed_plot.chapter_outline_id,
            plot_outline_id=detailed_plot.plot_outline_id,
            title=detailed_plot.title,
            content=detailed_plot.content,
            word_count=detailed_plot.word_count,
            status=detailed_plot.status,
            logic_check_result=detailed_plot.logic_check_result,
            logic_status=detailed_plot.logic_status,
            logic_score=None,
            created_at=detailed_plot.created_at,
            updated_at=detailed_plot.updated_at
        )
        print(f"✅ [DEBUG] 响应对象构建成功")
        
        return response
        
    except Exception as e:
        print(f"❌ [DEBUG] 生成详细剧情失败: {str(e)}")
        print(f"❌ [DEBUG] 错误类型: {type(e).__name__}")
        import traceback
        print(f"❌ [DEBUG] 错误堆栈:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"生成详细剧情失败: {str(e)}")


@router.get("/detailed-plots/{plot_outline_id}", response_model=DetailedPlotListResponse)
async def get_detailed_plots_by_plot_outline(
    plot_outline_id: str,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页大小")
):
    """根据剧情大纲ID获取详细剧情列表"""
    try:
        detailed_plots, total = detailed_plot_database.get_detailed_plots_by_plot_outline(
            plot_outline_id, page, page_size
        )
        
        return DetailedPlotListResponse(
            detailed_plots=[
                DetailedPlotResponse(
                    id=dp.id,
                    chapter_outline_id=dp.chapter_outline_id,
                    plot_outline_id=dp.plot_outline_id,
                    title=dp.title,
                    content=dp.content,
                    word_count=dp.word_count,
                    status=dp.status,
                    logic_check_result=dp.logic_check_result,
                    logic_status=dp.logic_status,
                    scoring_status=dp.scoring_status,
                    total_score=dp.total_score,
                    scoring_result=dp.scoring_result,
                    scoring_feedback=dp.scoring_feedback,
                    scored_at=dp.scored_at,
                    scored_by=dp.scored_by,
                    created_at=dp.created_at,
                    updated_at=dp.updated_at
                )
                for dp in detailed_plots
            ],
            total=total,
            page=page,
            page_size=page_size
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取详细剧情列表失败: {str(e)}")


@router.get("/detailed-plots/chapter/{chapter_outline_id}", response_model=List[DetailedPlotResponse])
async def get_detailed_plots_by_chapter_outline(chapter_outline_id: str):
    """根据章节大纲ID获取详细剧情列表"""
    try:
        detailed_plots = detailed_plot_database.get_detailed_plots_by_chapter_outline(chapter_outline_id)
        
        return [
            DetailedPlotResponse(
                id=dp.id,
                chapter_outline_id=dp.chapter_outline_id,
                plot_outline_id=dp.plot_outline_id,
                title=dp.title,
                content=dp.content,
                word_count=dp.word_count,
                status=dp.status,
                logic_check_result=dp.logic_check_result,
                logic_status=dp.logic_status,
                scoring_status=dp.scoring_status,
                total_score=dp.total_score,
                scoring_result=dp.scoring_result,
                scoring_feedback=dp.scoring_feedback,
                scored_at=dp.scored_at,
                scored_by=dp.scored_by,
                created_at=dp.created_at,
                updated_at=dp.updated_at
            )
            for dp in detailed_plots
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取详细剧情列表失败: {str(e)}")


@router.get("/detailed-plots/detail/{detailed_plot_id}", response_model=DetailedPlotResponse)
async def get_detailed_plot_by_id(detailed_plot_id: str):
    """根据ID获取详细剧情"""
    try:
        detailed_plot = detailed_plot_database.get_detailed_plot_by_id(detailed_plot_id)
        if not detailed_plot:
            raise HTTPException(status_code=404, detail="详细剧情不存在")
        
        return DetailedPlotResponse(
            id=detailed_plot.id,
            chapter_outline_id=detailed_plot.chapter_outline_id,
            plot_outline_id=detailed_plot.plot_outline_id,
            title=detailed_plot.title,
            content=detailed_plot.content,
            word_count=detailed_plot.word_count,
            status=detailed_plot.status,
            logic_check_result=detailed_plot.logic_check_result,
            logic_status=detailed_plot.logic_status,
            scoring_status=detailed_plot.scoring_status,
            total_score=detailed_plot.total_score,
            scoring_result=detailed_plot.scoring_result,
            scoring_feedback=detailed_plot.scoring_feedback,
            scored_at=detailed_plot.scored_at,
            scored_by=detailed_plot.scored_by,
            created_at=detailed_plot.created_at,
            updated_at=detailed_plot.updated_at
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取详细剧情失败: {str(e)}")


@router.put("/detailed-plots/{detailed_plot_id}/status")
async def update_detailed_plot_status(
    detailed_plot_id: str,
    status: DetailedPlotStatus
):
    """更新详细剧情状态"""
    try:
        success = detailed_plot_database.update_detailed_plot_status(detailed_plot_id, status)
        if not success:
            raise HTTPException(status_code=404, detail="详细剧情不存在")
        
        return {"message": "状态更新成功"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新状态失败: {str(e)}")


class DetailedPlotUpdateRequest(BaseModel):
    """详细剧情更新请求模型"""
    title: str = Field(..., description="标题")
    content: str = Field(..., description="内容")
    word_count: Optional[int] = Field(None, description="字数")


@router.put("/detailed-plots/{detailed_plot_id}")
async def update_detailed_plot(
    detailed_plot_id: str,
    request: DetailedPlotUpdateRequest
):
    """更新详细剧情内容"""
    try:
        # 检查详细剧情是否存在
        existing_plot = detailed_plot_database.get_detailed_plot_by_id(detailed_plot_id)
        if not existing_plot:
            raise HTTPException(status_code=404, detail="详细剧情不存在")
        
        # 更新详细剧情内容
        success = detailed_plot_database.update_detailed_plot_content(
            detailed_plot_id=detailed_plot_id,
            content=request.content,
            word_count=request.word_count or len(request.content)
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="更新详细剧情失败")
        
        # 更新标题（如果有变化）
        if request.title != existing_plot.title:
            title_success = detailed_plot_database.update_detailed_plot_title(
                detailed_plot_id=detailed_plot_id,
                title=request.title
            )
            if not title_success:
                debug_log("更新标题失败", f"ID: {detailed_plot_id}")
        
        # 保存编辑版本记录
        version_success = detailed_plot_database.save_detailed_plot_version(
            detailed_plot_id=detailed_plot_id,
            version_type='manual_edit',
            title=f"{request.title}（手动编辑版）",
            content=request.content,
            source_table='detailed_plots',
            source_record_id=detailed_plot_id,
            version_notes="手动编辑修改"
        )
        if version_success:
            debug_log("保存编辑版本成功", f"ID: {detailed_plot_id}")
        else:
            debug_log("保存编辑版本失败", f"ID: {detailed_plot_id}")
        
        return {"message": "详细剧情更新成功"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新详细剧情失败: {str(e)}")


@router.post("/detailed-plots/{detailed_plot_id}/logic-check")
async def check_detailed_plot_logic(detailed_plot_id: str):
    """对详细剧情进行逻辑检查"""
    try:
        # 获取详细剧情
        detailed_plot = detailed_plot_database.get_detailed_plot_by_id(detailed_plot_id)
        if not detailed_plot:
            raise HTTPException(status_code=404, detail="详细剧情不存在")
        
        # 进行逻辑检查
        logic_result = await logic_service.check_logic_detailed(
            content=detailed_plot.content,
            checked_by="manual"
        )
        
        # 更新详细剧情的逻辑检查结果
        print(f"DEBUG: 更新逻辑检查结果 - ID: {detailed_plot_id}, Status: {logic_result.overall_status}")
        success = detailed_plot_database.update_logic_check_result(
            detailed_plot_id=detailed_plot_id,
            logic_check_result=logic_result,
            logic_status=logic_result.overall_status
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="更新逻辑检查结果失败")
        
        print(f"DEBUG: 逻辑检查结果更新成功: {success}")
        
        return {
            "message": "逻辑检查完成",
            "logic_result": logic_result.dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"逻辑检查失败: {str(e)}")


@router.delete("/detailed-plots/{detailed_plot_id}")
async def delete_detailed_plot(detailed_plot_id: str):
    """删除详细剧情及其相关记录"""
    try:
        # 先检查详细剧情是否存在
        detailed_plot = detailed_plot_database.get_detailed_plot_by_id(detailed_plot_id)
        if not detailed_plot:
            raise HTTPException(status_code=404, detail="详细剧情不存在")
        
        # 记录删除前的修正记录数量
        correction_history = detailed_plot_database.get_correction_history(detailed_plot_id)
        correction_count = len(correction_history)
        
        # 执行删除操作
        success = detailed_plot_database.delete_detailed_plot(detailed_plot_id)
        if not success:
            raise HTTPException(status_code=500, detail="删除操作失败")
        
        # 返回详细的删除结果
        message = f"详细剧情删除成功"
        if correction_count > 0:
            message += f"，同时删除了 {correction_count} 条修正记录"
        
        return {
            "message": message,
            "deleted_correction_records": correction_count
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")


@router.post("/detailed-plots/{detailed_plot_id}/scoring")
async def score_detailed_plot(detailed_plot_id: str):
    """对详细剧情进行智能评分"""
    try:
        # 获取详细剧情
        detailed_plot = detailed_plot_database.get_detailed_plot_by_id(detailed_plot_id)
        if not detailed_plot:
            raise HTTPException(status_code=404, detail="详细剧情不存在")
        
        # 进行智能评分
        scoring_result = await scoring_service.score_detailed_plot(
            content=detailed_plot.content,
            detailed_plot_id=detailed_plot_id,
            scored_by="manual"
        )
        
        # 更新详细剧情的评分结果
        success = detailed_plot_database.update_scoring_result(
            detailed_plot_id=detailed_plot_id,
            scoring_status=scoring_result["scoring_status"].value,
            total_score=scoring_result["total_score"],
            scoring_result=scoring_result["scoring_result"],
            scoring_feedback=scoring_result["scoring_feedback"],
            scored_by=scoring_result["scored_by"]
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="更新评分结果失败")
        
        # 保存评分历史
        if "scoring_history" in scoring_result:
            detailed_plot_database.save_scoring_history(scoring_result["scoring_history"])
        
        return {
            "message": "智能评分完成",
            "scoring_result": scoring_result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"智能评分失败: {str(e)}")


@router.get("/detailed-plots/{detailed_plot_id}/scoring-history")
async def get_scoring_history(detailed_plot_id: str):
    """获取详细剧情的评分历史"""
    try:
        history = detailed_plot_database.get_scoring_history(detailed_plot_id)
        return {
            "detailed_plot_id": detailed_plot_id,
            "scoring_history": history
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取评分历史失败: {str(e)}")


@router.post("/detailed-plots/{detailed_plot_id}/evolution")
async def evolve_detailed_plot(detailed_plot_id: str, evolution_type: str = "general"):
    """对详细剧情进行智能进化"""
    try:
        detailed_plot = detailed_plot_database.get_detailed_plot_by_id(detailed_plot_id)
        if not detailed_plot:
            raise HTTPException(status_code=404, detail="详细剧情不存在")
        
        evolution_result = await evolution_service.evolve_detailed_plot(
            content=detailed_plot.content,
            detailed_plot_id=detailed_plot_id,
            evolution_type=evolution_type,
            evolved_by="manual"
        )
        
        if evolution_result["evolution_status"] == "completed":
            # 更新详细剧情内容
            success = detailed_plot_database.update_detailed_plot_content(
                detailed_plot_id=detailed_plot_id,
                content=evolution_result["evolved_content"],
                word_count=len(evolution_result["evolved_content"])
            )
            
            if not success:
                raise HTTPException(status_code=500, detail="更新进化内容失败")
            
            # 保存进化历史
            if "evolution_history" in evolution_result:
                detailed_plot_database.save_evolution_history(evolution_result["evolution_history"])
            
            # 生成进化后的MD文件
            try:
                # 获取更新后的详细剧情数据
                updated_detailed_plot = detailed_plot_database.get_detailed_plot_by_id(detailed_plot_id)
                if updated_detailed_plot:
                    # 构建MD文件数据
                    md_data = {
                        'id': updated_detailed_plot.id,
                        'chapter_outline_id': updated_detailed_plot.chapter_outline_id,
                        'plot_outline_id': updated_detailed_plot.plot_outline_id,
                        'title': updated_detailed_plot.title,
                        'content': updated_detailed_plot.content,
                        'word_count': updated_detailed_plot.word_count,
                        'status': updated_detailed_plot.status.value if updated_detailed_plot.status else '未知',
                        'logic_status': updated_detailed_plot.logic_status.value if updated_detailed_plot.logic_status else '未检查',
                        'logic_check_result': updated_detailed_plot.logic_check_result,
                        'scoring_status': updated_detailed_plot.scoring_status,
                        'total_score': updated_detailed_plot.total_score,
                        'created_at': updated_detailed_plot.created_at.strftime('%Y-%m-%d %H:%M:%S') if updated_detailed_plot.created_at else None,
                        'updated_at': updated_detailed_plot.updated_at.strftime('%Y-%m-%d %H:%M:%S') if updated_detailed_plot.updated_at else None
                    }
                    
                    # 生成MD文件
                    md_file_path = file_writer.write_detailed_plot(md_data)
                    print(f"✅ 进化后MD文件生成成功: {md_file_path}")
                    
            except Exception as e:
                print(f"⚠️ 进化后MD文件生成失败: {str(e)}")
                # 不影响主要流程，继续执行
        
        return {
            "message": "智能进化完成",
            "evolution_result": evolution_result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"智能进化失败: {str(e)}")


@router.get("/detailed-plots/{detailed_plot_id}/evolution-history")
async def get_evolution_history(detailed_plot_id: str):
    """获取详细剧情的进化历史"""
    try:
        history = detailed_plot_database.get_evolution_history(detailed_plot_id)
        return {
            "detailed_plot_id": detailed_plot_id,
            "evolution_history": history
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取进化历史失败: {str(e)}")


@router.get("/evolution-types")
async def get_evolution_types():
    """获取可用的进化类型"""
    try:
        types = evolution_service.get_evolution_types()
        return {
            "evolution_types": types
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取进化类型失败: {str(e)}")


@router.post("/detailed-plots/{detailed_plot_id}/correction")
async def correct_detailed_plot(detailed_plot_id: str, request: CorrectionRequest):
    """对详细剧情进行智能修正"""
    try:
        detailed_plot = detailed_plot_database.get_detailed_plot_by_id(detailed_plot_id)
        if not detailed_plot:
            raise HTTPException(status_code=404, detail="详细剧情不存在")
        
        # 检查是否有逻辑检查结果
        if not detailed_plot.logic_check_result:
            raise HTTPException(status_code=400, detail="请先进行逻辑检查")
        
        # 检查逻辑状态是否为不通过
        if detailed_plot.logic_status == LogicStatus.PASSED:
            raise HTTPException(status_code=400, detail="逻辑检查已通过，无需修正")
        
        # 从逻辑检查结果中提取问题清单
        issues = []
        if detailed_plot.logic_check_result and detailed_plot.logic_check_result.issues_found:
            issues = [issue.dict() for issue in detailed_plot.logic_check_result.issues_found]
        
        correction_result = await correction_service.correct_detailed_plot(
            content=detailed_plot.content,
            detailed_plot_id=detailed_plot_id,
            issues=issues,
            user_prompt=request.correction_prompt,
            corrected_by="manual"
        )
        
        if correction_result["correction_status"] == "completed":
            # 更新详细剧情内容
            success = detailed_plot_database.update_detailed_plot_content(
                detailed_plot_id=detailed_plot_id,
                content=correction_result["corrected_content"],
                word_count=len(correction_result["corrected_content"])
            )
            
            if not success:
                raise HTTPException(status_code=500, detail="更新修正内容失败")
            
            # 保存修正历史
            if "correction_history" in correction_result:
                history_save_success = detailed_plot_database.save_correction_history(correction_result["correction_history"])
                if not history_save_success:
                    error_log("保存修正历史失败", f"ID: {detailed_plot_id}")
                else:
                    debug_log("保存修正历史成功", f"ID: {detailed_plot_id}")
            
            # 保存修正版本记录
            version_success = detailed_plot_database.save_detailed_plot_version(
                detailed_plot_id=detailed_plot_id,
                version_type='correction',
                title=f"{detailed_plot.title}（修正版）",
                content=correction_result["corrected_content"],
                source_table='correction_history',
                source_record_id=correction_result["correction_history"]["id"],
                version_notes=f"修正了{len(issues)}个逻辑问题"
            )
            if version_success:
                debug_log("保存修正版本成功", f"ID: {detailed_plot_id}")
            else:
                debug_log("保存修正版本失败", f"ID: {detailed_plot_id}")
            
            # 生成修正后的MD文件
            try:
                # 获取更新后的详细剧情数据
                updated_detailed_plot = detailed_plot_database.get_detailed_plot_by_id(detailed_plot_id)
                if updated_detailed_plot:
                    # 构建MD文件数据
                    md_data = {
                        'id': updated_detailed_plot.id,
                        'chapter_outline_id': updated_detailed_plot.chapter_outline_id,
                        'plot_outline_id': updated_detailed_plot.plot_outline_id,
                        'title': updated_detailed_plot.title,
                        'content': updated_detailed_plot.content,
                        'word_count': updated_detailed_plot.word_count,
                        'status': updated_detailed_plot.status.value if updated_detailed_plot.status else '未知',
                        'logic_status': updated_detailed_plot.logic_status.value if updated_detailed_plot.logic_status else '未检查',
                        'logic_check_result': updated_detailed_plot.logic_check_result,
                        'scoring_status': updated_detailed_plot.scoring_status,
                        'total_score': updated_detailed_plot.total_score,
                        'created_at': updated_detailed_plot.created_at.strftime('%Y-%m-%d %H:%M:%S') if updated_detailed_plot.created_at else None,
                        'updated_at': updated_detailed_plot.updated_at.strftime('%Y-%m-%d %H:%M:%S') if updated_detailed_plot.updated_at else None
                    }
                    
                    # 生成MD文件
                    md_file_path = file_writer.write_detailed_plot(md_data)
                    print(f"✅ 修正后MD文件生成成功: {md_file_path}")
                    
            except Exception as e:
                print(f"⚠️ 修正后MD文件生成失败: {str(e)}")
                # 不影响主要流程，继续执行
            
            # 修正完成，不自动调用评分或逻辑检查
            debug_log("修正完成", f"ID: {detailed_plot_id}")
        
        return {
            "message": "智能修正完成",
            "correction_result": correction_result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"智能修正失败: {str(e)}")


@router.get("/detailed-plots/{detailed_plot_id}/correction-history")
async def get_correction_history(detailed_plot_id: str):
    """获取详细剧情的修正历史"""
    try:
        history = detailed_plot_database.get_correction_history(detailed_plot_id)
        return {
            "detailed_plot_id": detailed_plot_id,
            "correction_history": history
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取修正历史失败: {str(e)}")
