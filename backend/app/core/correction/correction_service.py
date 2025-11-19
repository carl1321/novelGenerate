"""
修正智能体服务
用于根据逻辑检查结果对详细剧情进行智能修正
"""

import json
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional

from app.utils.llm_client import get_llm_client
from app.utils.prompt_manager import PromptManager
from app.core.detailed_plot.detailed_plot_models import DetailedPlotStatus
from app.utils.logger import debug_log, info_log, error_log


class CorrectionService:
    """修正智能体服务"""
    
    def __init__(self):
        self.llm_client = get_llm_client()
        self.prompt_manager = PromptManager()
    
    async def correct_detailed_plot(
        self, 
        content: str, 
        detailed_plot_id: str, 
        issues: List[Dict[str, Any]],
        user_prompt: str = "",
        corrected_by: str = "system"
    ) -> Dict[str, Any]:
        """
        对详细剧情进行智能修正
        
        Args:
            content: 原始详细剧情内容
            detailed_plot_id: 详细剧情ID
            issues: 问题清单列表
            user_prompt: 用户修正要求
            corrected_by: 修正者
            
        Returns:
            修正结果字典
        """
        try:
            debug_log("开始修正详细剧情", f"ID: {detailed_plot_id}")
            
            # 获取修正prompt
            prompt = self.prompt_manager.get_correction_prompt(
                content=content, 
                issues=issues,
                user_prompt=user_prompt
            )
            
            # 调用LLM进行修正
            response = await self.llm_client.generate_text(
                prompt=prompt,
                temperature=0.3,  # 使用较低的温度以确保修正的准确性
                max_tokens=20000
            )
            
            debug_log("LLM修正响应", f"长度: {len(response)}")
            
            # 直接使用LLM响应作为修正后的内容
            corrected_content = response.strip()
            
            # 计算字数变化
            original_word_count = len(content)
            corrected_word_count = len(corrected_content)
            word_count_change = corrected_word_count - original_word_count
            
            # 构建修正详情
            corrections_made = []
            for issue in issues:
                issue_dict = issue if isinstance(issue, dict) else issue.dict()
                corrections_made.append({
                    "issue_category": issue_dict.get('category', '未知'),
                    "issue_description": issue_dict.get('description', '无描述'),
                    "correction_method": "智能修正",
                    "correction_details": f"根据问题描述'{issue_dict.get('description', '')}'进行了针对性修正"
                })
            
            # 构建修正历史记录
            correction_history_entry = {
                "id": f"correction_hist_{uuid.uuid4().hex[:8]}",
                "detailed_plot_id": detailed_plot_id,
                "original_content": content,
                "corrected_content": corrected_content,
                "logic_check_result": {"issues": issues},
                "corrections_made": corrections_made,
                "correction_summary": f"修正了{len(issues)}个问题{'，同时考虑了用户修正要求' if user_prompt.strip() else ''}",
                "word_count_change": word_count_change,
                "quality_improvement": "修正了逻辑问题，提升了内容质量和一致性",
                "correction_notes": f"使用简化修正智能体进行修正{'，包含用户自定义修正要求' if user_prompt.strip() else ''}",
                "corrected_by": corrected_by,
                "corrected_at": datetime.now().isoformat()
            }
            
            info_log("修正完成", f"ID: {detailed_plot_id}, 字数变化: {word_count_change}")
            
            return {
                "correction_status": "completed",
                "corrected_content": corrected_content,
                "corrections_made": corrections_made,
                "correction_summary": f"修正了{len(issues)}个问题{'，同时考虑了用户修正要求' if user_prompt.strip() else ''}",
                "word_count_change": word_count_change,
                "quality_improvement": "修正了逻辑问题，提升了内容质量和一致性",
                "correction_notes": f"使用简化修正智能体进行修正{'，包含用户自定义修正要求' if user_prompt.strip() else ''}",
                "corrected_by": corrected_by,
                "correction_history": correction_history_entry
            }
            
        except Exception as e:
            error_log("修正失败", f"ID: {detailed_plot_id}, 错误: {str(e)}")
            return {
                "correction_status": "failed",
                "error_message": str(e),
                "corrected_by": corrected_by
            }
    


# 创建全局实例
correction_service = CorrectionService()
