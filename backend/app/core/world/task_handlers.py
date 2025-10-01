"""
世界观任务处理器
"""
import os
from typing import Dict, Any
from app.core.world.llm_generator import LLMWorldGenerator
from app.core.automation.progress_manager import ProgressManager
from app.utils.file_writer import FileWriter


async def process_worldview_task(task_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """处理世界观生成任务"""
    try:
        print(f"🌍 开始生成世界观任务 {task_id}")
        
        # 获取参数
        core_concept = data['core_concept']
        description = data['description']
        additional_requirements = data['additional_requirements']
        
        # 初始化生成器
        from app.core.world.rule_engine import RuleEngine
        rule_engine = RuleEngine()
        world_generator = LLMWorldGenerator(rule_engine)
        
        # 生成世界观
        result = await world_generator.generate_world_view(
            core_concept,
            description,
            additional_requirements
        )
        
        # 保存到进度管理器
        progress_manager = ProgressManager('current_session')
        progress_manager.update_stage("WORLDVIEW_GENERATED", {"world_view": result.dict()})
        
        # 保存MD文件
        file_writer = FileWriter()
        file_writer.write_world_view(result)
        
        # 读取生成的MD文件内容
        md_file_path = f"novel/world_view_{result.id}.md"
        md_content = ""
        if os.path.exists(md_file_path):
            with open(md_file_path, 'r', encoding='utf-8') as f:
                md_content = f.read()
        
        print(f"✅ 世界观任务 {task_id} 生成完成")
        
        return {
            "world_view": result.dict(),
            "md_content": md_content,
            "md_file_path": md_file_path
        }
        
    except Exception as e:
        print(f"❌ 世界观任务 {task_id} 生成失败: {e}")
        raise
