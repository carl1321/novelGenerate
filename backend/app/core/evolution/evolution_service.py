"""
进化智能体服务
用于对详细剧情进行智能进化和优化
"""

import json
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional

from app.utils.llm_client import get_llm_client
from app.utils.prompt_manager import PromptManager
from app.core.detailed_plot.detailed_plot_models import DetailedPlotStatus
from app.utils.logger import debug_log, info_log, error_log


class EvolutionService:
    """进化智能体服务"""
    
    def __init__(self):
        self.llm_client = get_llm_client()
        self.prompt_manager = PromptManager()
    
    async def evolve_detailed_plot(
        self, 
        content: str, 
        detailed_plot_id: str, 
        evolution_type: str = "general",
        evolved_by: str = "system"
    ) -> Dict[str, Any]:
        """
        对详细剧情进行智能进化
        
        Args:
            content: 原始详细剧情内容
            detailed_plot_id: 详细剧情ID
            evolution_type: 进化类型
            evolved_by: 进化者
            
        Returns:
            进化结果字典
        """
        try:
            debug_log("开始进化详细剧情", f"ID: {detailed_plot_id}, 类型: {evolution_type}")
            
            # 获取进化prompt
            prompt = self.prompt_manager.get_evolution_prompt(
                content=content, 
                evolution_type=evolution_type
            )
            
            # 调用LLM进行进化
            response = await self.llm_client.generate_text(
                prompt=prompt,
                temperature=0.7,  # 使用稍高的温度以增加创造性
                max_tokens=20000
            )
            
            debug_log("LLM进化响应", f"长度: {len(response)}")
            
            # 解析LLM响应
            evolution_data = self._parse_llm_response(response)
            
            # 计算字数变化
            original_word_count = len(content)
            evolved_word_count = len(evolution_data.get("evolved_content", ""))
            word_count_change = evolved_word_count - original_word_count
            
            # 构建进化历史记录
            evolution_history_entry = {
                "id": f"evolution_hist_{uuid.uuid4().hex[:8]}",
                "detailed_plot_id": detailed_plot_id,
                "evolution_type": evolution_type,
                "original_content": content,
                "evolved_content": evolution_data.get("evolved_content", ""),
                "improvements": evolution_data.get("improvements", {}),
                "evolution_summary": evolution_data.get("evolution_summary", ""),
                "word_count_change": word_count_change,
                "quality_score": evolution_data.get("quality_score", 0.0),
                "evolution_notes": evolution_data.get("evolution_notes", ""),
                "evolved_by": evolved_by,
                "evolved_at": datetime.now()
            }
            
            info_log("进化完成", f"ID: {detailed_plot_id}, 字数变化: {word_count_change}")
            
            return {
                "evolution_status": "completed",
                "evolution_type": evolution_type,
                "evolved_content": evolution_data.get("evolved_content", ""),
                "improvements": evolution_data.get("improvements", {}),
                "evolution_summary": evolution_data.get("evolution_summary", ""),
                "word_count_change": word_count_change,
                "quality_score": evolution_data.get("quality_score", 0.0),
                "evolution_notes": evolution_data.get("evolution_notes", ""),
                "evolved_by": evolved_by,
                "evolution_history": evolution_history_entry
            }
            
        except Exception as e:
            error_log("进化失败", f"ID: {detailed_plot_id}, 错误: {str(e)}")
            return {
                "evolution_status": "failed",
                "error_message": str(e),
                "evolution_type": evolution_type,
                "evolved_by": evolved_by
            }
    
    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """解析LLM响应"""
        try:
            # 尝试提取JSON部分
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                return json.loads(json_str)
            else:
                # 如果没有找到JSON，返回默认结构
                return {
                    "evolved_content": response,
                    "improvements": {},
                    "evolution_summary": "进化完成",
                    "quality_score": 0.0,
                    "evolution_notes": "无法解析详细进化信息"
                }
        except json.JSONDecodeError as e:
            error_log("JSON解析失败", f"错误: {str(e)}")
            return {
                "evolved_content": response,
                "improvements": {},
                "evolution_summary": "进化完成",
                "quality_score": 0.0,
                "evolution_notes": f"解析错误: {str(e)}"
            }
    
    def get_evolution_types(self) -> List[Dict[str, str]]:
        """获取可用的进化类型"""
        return [
            {"value": "general", "label": "综合进化", "description": "全面提升剧情质量"},
            {"value": "dialogue", "label": "对话优化", "description": "重点优化对话表达"},
            {"value": "action", "label": "动作强化", "description": "重点强化动作描写"},
            {"value": "description", "label": "描写美化", "description": "重点美化环境描写"},
            {"value": "conflict", "label": "冲突强化", "description": "重点强化戏剧冲突"},
            {"value": "character", "label": "角色深化", "description": "重点深化角色塑造"}
        ]


# 创建全局实例
evolution_service = EvolutionService()
