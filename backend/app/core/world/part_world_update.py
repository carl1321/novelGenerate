"""
部分世界观更新器
"""
import json
import logging
from typing import Dict, List, Any, Optional

from app.utils.llm_client import get_llm_client
from app.utils.prompt_manager import PromptManager

logger = logging.getLogger(__name__)


class PartialWorldUpdateService:
    """部分世界观更新器"""
    
    def __init__(self):
        self.llm_client = get_llm_client()
        self.prompt_manager = PromptManager()
    
    async def update_partial_worldview(
        self,
        existing_worldview: Dict[str, Any],
        update_dimensions: List[str],
        update_description: str,
        additional_context: Optional[Dict[str, Any]] = None,
        merge_mode: str = "merge"  # "merge" 或 "replace"
    ) -> Dict[str, Any]:
        """
        部分更新世界观
        
        Args:
            existing_worldview: 现有世界观数据
            update_dimensions: 要更新的维度列表 ['power_system', 'geography', 'culture', 'history']
            update_description: 更新描述
            additional_context: 额外上下文
            
        Returns:
            更新后的世界观数据
        """
        
        logger.info(f"开始部分更新世界观，更新维度: {update_dimensions}")
        
        # 1. 获取部分更新提示词
        prompt = self.prompt_manager.get_partial_update_prompt(
            existing_worldview=existing_worldview,
            update_dimensions=update_dimensions,
            update_description=update_description,
            additional_context=additional_context
        )
        
        # 2. 调用LLM生成更新内容
        messages = [
            {"role": "system", "content": "你是一个专业的世界观设计师，擅长基于现有设定进行部分更新。"},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = await self.llm_client.generate_chat(messages)
            logger.info("LLM生成内容成功")
            logger.info(f"LLM原始响应长度: {len(response)} 字符")
            logger.info(f"LLM原始响应前500字符: {response[:500]}")
        except Exception as e:
            logger.error(f"LLM生成内容失败: {e}")
            raise
        
        # 3. 解析LLM响应
        try:
            new_data = json.loads(response)
            logger.info(f"LLM响应解析成功，返回维度: {list(new_data.keys())}")
            
            # 详细记录每个维度的内容
            for dimension in update_dimensions:
                if dimension in new_data:
                    dimension_data = new_data[dimension]
                    logger.info(f"维度 {dimension} 数据:")
                    if isinstance(dimension_data, dict):
                        for key, value in dimension_data.items():
                            if isinstance(value, list):
                                logger.info(f"  {key}: {len(value)} 项")
                                if len(value) > 0:
                                    logger.info(f"    示例: {value[0] if isinstance(value[0], dict) else str(value[0])[:100]}")
                            else:
                                logger.info(f"  {key}: {str(value)[:100]}")
                    else:
                        logger.info(f"  数据类型: {type(dimension_data)}, 内容: {str(dimension_data)[:200]}")
                else:
                    logger.warning(f"维度 {dimension} 未在LLM响应中找到")
                    
        except json.JSONDecodeError as e:
            logger.error(f"LLM响应解析失败: {e}")
            logger.error(f"原始响应: {response[:500]}...")
            raise ValueError("LLM响应格式错误")
        
        # 4. 获取更新模式
        update_mode = new_data.pop('update_mode', 'merge')  # 默认为合并模式
        logger.info(f"LLM指定的更新模式: {update_mode}")
        
        # 5. 合并数据
        logger.info(f"开始合并数据，更新维度: {update_dimensions}")
        logger.info(f"现有世界观数据: {existing_worldview}")
        logger.info(f"LLM返回的新数据: {new_data}")
        
        merged_data = self._merge_worldview_data(existing_worldview, new_data, update_dimensions, update_mode)
        
        logger.info(f"合并后的数据: {merged_data}")
        
        logger.info(f"部分更新完成，更新了 {len(update_dimensions)} 个维度")
        return merged_data
    
    def _merge_worldview_data(
        self, 
        existing_data: Dict[str, Any], 
        new_data: Dict[str, Any], 
        update_dimensions: List[str],
        update_mode: str = "merge"
    ) -> Dict[str, Any]:
        """
        合并世界观数据
        
        Args:
            existing_data: 现有数据
            new_data: 新生成的数据
            update_dimensions: 要更新的维度列表
            
        Returns:
            合并后的数据
        """
        merged_data = existing_data.copy()
        
        for dimension in update_dimensions:
            if dimension in new_data:
                if update_mode == "replace":
                    # 替换模式：直接替换整个维度
                    merged_data[dimension] = new_data[dimension]
                    logger.info(f"替换维度 {dimension}")
                else:
                    # 合并模式：合并维度数据
                    merged_data[dimension] = self._merge_dimension_data(
                        existing_data.get(dimension, {}),
                        new_data[dimension],
                        dimension
                    )
                    logger.info(f"合并维度 {dimension}")
            else:
                logger.warning(f"LLM未返回维度 {dimension} 的数据")
        
        return merged_data
    
    def _merge_dimension_data(
        self, 
        existing_dimension: Dict[str, Any], 
        new_dimension: Dict[str, Any], 
        dimension_name: str
    ) -> Dict[str, Any]:
        """
        合并单个维度的数据
        
        Args:
            existing_dimension: 现有维度数据
            new_dimension: 新维度数据
            dimension_name: 维度名称
            
        Returns:
            合并后的维度数据
        """
        merged_dimension = existing_dimension.copy()
        
        # 定义每个维度的数组字段
        array_fields = {
            'power_system': ['cultivation_realms', 'energy_types', 'technique_categories'],
            'geography': ['regions', 'main_regions', 'special_locations'],
            'culture': ['organizations'],
            'history': ['historical_events', 'cultural_features', 'current_conflicts']
        }
        
        if dimension_name in array_fields:
            # 对于数组字段，合并数组内容
            for field in array_fields[dimension_name]:
                if field in new_dimension:
                    existing_array = merged_dimension.get(field, [])
                    new_array = new_dimension[field]
                    
                    # 合并数组：保留原有内容，添加新内容
                    if isinstance(existing_array, list) and isinstance(new_array, list):
                        merged_dimension[field] = existing_array + new_array
                        logger.info(f"合并 {dimension_name}.{field}: 原有 {len(existing_array)} 个，新增 {len(new_array)} 个")
                    else:
                        merged_dimension[field] = new_array
                else:
                    # 如果新数据中没有这个字段，保留原有数据
                    pass
        else:
            # 对于非数组字段，直接替换
            merged_dimension = new_dimension
        
        return merged_dimension
    
    async def update_single_dimension(
        self,
        existing_worldview: Dict[str, Any],
        dimension: str,
        update_description: str
    ) -> Dict[str, Any]:
        """
        更新单个维度
        
        Args:
            existing_worldview: 现有世界观数据
            dimension: 要更新的维度
            update_description: 更新描述
            
        Returns:
            更新后的世界观数据
        """
        
        logger.info(f"开始更新单个维度: {dimension}")
        
        # 获取维度专用提示词
        prompt = self.prompt_manager.get_dimension_specific_prompt(
            dimension=dimension,
            existing_data=existing_worldview.get(dimension, {}),
            update_description=update_description
        )
        
        # 调用LLM
        messages = [
            {"role": "system", "content": f"你是一个专业的{dimension}设计师。"},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = await self.llm_client.generate_chat(messages)
            logger.info(f"维度 {dimension} LLM生成成功")
        except Exception as e:
            logger.error(f"维度 {dimension} LLM生成失败: {e}")
            raise
        
        # 解析并合并
        try:
            new_dimension_data = json.loads(response)
            merged_data = existing_worldview.copy()
            merged_data[dimension] = new_dimension_data
            logger.info(f"维度 {dimension} 更新完成")
            return merged_data
        except json.JSONDecodeError as e:
            logger.error(f"维度 {dimension} 更新失败: {e}")
            logger.error(f"原始响应: {response[:500]}...")
            raise ValueError(f"维度 {dimension} 更新响应格式错误")
