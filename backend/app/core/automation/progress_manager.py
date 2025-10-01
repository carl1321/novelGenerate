"""
进度管理器 - 支持断点续传
"""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
from enum import Enum

from app.core.config import settings


class GenerationStage(str, Enum):
    """生成阶段枚举"""
    INITIALIZING = "初始化"
    WORLDVIEW_GENERATED = "世界观已生成"
    CHARACTERS_GENERATED = "角色已生成"
    EVENTS_GENERATED = "事件已生成"
    PLOT_GENERATED = "剧情已生成"
    PLOT_OUTLINE_GENERATED = "剧情大纲已生成"
    FORESHADOWING_GENERATED = "伏笔网络已生成"
    CHAPTERS_GENERATED = "章节已生成"
    OPTIMIZATION_COMPLETED = "优化完成"
    FINALIZATION_COMPLETED = "最终化完成"
    COMPLETED = "生成完成"


class ProgressManager:
    """进度管理器"""
    
    def __init__(self, session_id: str = None):
        # 使用固定的session文件，方便断点续传
        self.session_id = session_id or "current_session"
        self.progress_file = Path(settings.NOVEL_OUTPUT_DIR) / f"progress_{self.session_id}.json"
        self.progress_data = self._load_progress()
    
    def _load_progress(self) -> Dict[str, Any]:
        """加载进度数据"""
        if self.progress_file.exists():
            try:
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载进度文件失败: {e}")
                return self._create_empty_progress()
        return self._create_empty_progress()
    
    def _create_empty_progress(self) -> Dict[str, Any]:
        """创建空的进度数据"""
        return {
            "session_id": self.session_id,
            "core_concept": "",
            "current_stage": GenerationStage.INITIALIZING,
            "completed_stages": [],
            "generated_content": {},
            "files_created": {},
            "errors": [],
            "start_time": datetime.now().isoformat(),
            "last_update": datetime.now().isoformat(),
            "total_stages": len(GenerationStage) - 1  # 减去INITIALIZING
        }
    
    def save_progress(self):
        """保存进度"""
        self.progress_data["last_update"] = datetime.now().isoformat()
        try:
            with open(self.progress_file, 'w', encoding='utf-8') as f:
                json.dump(self.progress_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存进度失败: {e}")
    
    def update_stage(self, stage: GenerationStage, content: Dict[str, Any] = None):
        """更新当前阶段"""
        if stage not in self.progress_data["completed_stages"]:
            self.progress_data["completed_stages"].append(stage)
        
        self.progress_data["current_stage"] = stage
        
        # 只记录阶段的基本信息，不记录具体内容
        if content:
            # 只记录文件名和数量等基本信息
            stage_info = self._extract_stage_info(stage, content)
            self.progress_data["generated_content"][stage] = stage_info
        
        self.save_progress()
        print(f"✅ 阶段完成: {stage}")
    
    def _extract_stage_info(self, stage: GenerationStage, content: Dict[str, Any]) -> Dict[str, Any]:
        """提取阶段的基本信息，不保存完整内容"""
        stage_info = {
            "stage": stage.value,
            "timestamp": datetime.now().isoformat(),
            "files_count": 0,
            "file_types": []
        }
        
        if stage == GenerationStage.WORLDVIEW_GENERATED:
            stage_info["world_name"] = content.get("name", "未知世界观")
            stage_info["files_count"] = 1
            stage_info["file_types"] = ["世界观设计"]
            
        elif stage == GenerationStage.CHARACTERS_GENERATED:
            characters = content.get("characters", [])
            stage_info["characters_count"] = len(characters)
            stage_info["files_count"] = len(characters)
            stage_info["file_types"] = ["角色档案"]
            if characters:
                stage_info["main_character"] = characters[0].get("name", "未知主角")
                
        elif stage == GenerationStage.PLOT_GENERATED:
            stage_info["files_count"] = 1
            stage_info["file_types"] = ["情节大纲"]
            
        elif stage == GenerationStage.CHAPTERS_GENERATED:
            chapters = content.get("chapters", [])
            stage_info["chapters_count"] = len(chapters)
            stage_info["files_count"] = len(chapters)
            stage_info["file_types"] = ["章节内容"]
            
        return stage_info
    
    def scan_novel_directory(self) -> Dict[str, Any]:
        """扫描novel目录，获取实际生成的文件信息"""
        import os
        import glob
        
        novel_dir = "novel"
        if not os.path.exists(novel_dir):
            return {"error": "novel目录不存在"}
        
        files_info = {
            "worldview_files": [],
            "character_files": [],
            "plot_files": [],
            "chapter_files": [],
            "other_files": []
        }
        
        # 扫描各种类型的文件
        worldview_files = glob.glob(os.path.join(novel_dir, "*世界观设计*.md"))
        character_files = glob.glob(os.path.join(novel_dir, "*角色档案*.md"))
        plot_files = glob.glob(os.path.join(novel_dir, "*情节大纲*.md"))
        chapter_files = glob.glob(os.path.join(novel_dir, "*章节*.md"))
        other_files = glob.glob(os.path.join(novel_dir, "*.md"))
        
        # 过滤掉已分类的文件
        other_files = [f for f in other_files if f not in worldview_files + character_files + plot_files + chapter_files]
        
        files_info["worldview_files"] = [os.path.basename(f) for f in worldview_files]
        files_info["character_files"] = [os.path.basename(f) for f in character_files]
        files_info["plot_files"] = [os.path.basename(f) for f in plot_files]
        files_info["chapter_files"] = [os.path.basename(f) for f in chapter_files]
        files_info["other_files"] = [os.path.basename(f) for f in other_files]
        
        # 统计信息
        files_info["total_files"] = len(worldview_files) + len(character_files) + len(plot_files) + len(chapter_files) + len(other_files)
        files_info["scan_time"] = datetime.now().isoformat()
        
        return files_info
    
    def get_resume_info(self) -> Dict[str, Any]:
        """获取断点续传信息，包含文件扫描结果"""
        resume_info = {
            "session_id": self.progress_data.get("session_id"),
            "core_concept": self.progress_data.get("core_concept"),
            "completed_stages": self.progress_data.get("completed_stages", []),
            "current_stage": self.progress_data.get("current_stage"),
            "created_at": self.progress_data.get("created_at"),
            "last_updated": self.progress_data.get("last_updated"),
            "files_created": self.progress_data.get("files_created", {}),
            "generated_content": self.progress_data.get("generated_content", {}),
            "novel_directory_scan": self.scan_novel_directory()
        }
        return resume_info
    
    def _make_serializable(self, obj):
        """将对象转换为JSON可序列化的格式"""
        if isinstance(obj, dict):
            return {key: self._make_serializable(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._make_serializable(item) for item in obj]
        elif isinstance(obj, datetime):
            return obj.isoformat()
        elif hasattr(obj, 'dict'):  # Pydantic模型
            return self._make_serializable(obj.dict())
        elif hasattr(obj, '__dict__'):  # 其他对象
            return self._make_serializable(obj.__dict__)
        elif hasattr(obj, 'mapping'):  # mappingproxy类型
            return self._make_serializable(dict(obj))
        else:
            return obj
    
    def add_file(self, file_type: str, file_path: str):
        """添加生成的文件"""
        if file_type not in self.progress_data["files_created"]:
            self.progress_data["files_created"][file_type] = []
        self.progress_data["files_created"][file_type].append(file_path)
        self.save_progress()
    
    def add_error(self, error: str, stage: str = None):
        """添加错误信息"""
        error_info = {
            "error": error,
            "stage": stage or self.progress_data["current_stage"],
            "timestamp": datetime.now().isoformat()
        }
        self.progress_data["errors"].append(error_info)
        self.save_progress()
    
    def get_completed_stages(self) -> List[GenerationStage]:
        """获取已完成的阶段"""
        return [GenerationStage(stage) for stage in self.progress_data["completed_stages"]]
    
    def get_current_stage(self) -> GenerationStage:
        """获取当前阶段"""
        return GenerationStage(self.progress_data["current_stage"])
    
    def get_generated_content(self, stage: GenerationStage = None) -> Dict[str, Any]:
        """获取生成的内容"""
        if stage:
            return self.progress_data["generated_content"].get(stage, {})
        return self.progress_data["generated_content"]
    
    def is_stage_completed(self, stage: GenerationStage) -> bool:
        """检查阶段是否已完成"""
        return stage in self.get_completed_stages()
    
    def get_progress_percentage(self) -> float:
        """获取进度百分比"""
        completed = len(self.get_completed_stages())
        total = self.progress_data["total_stages"]
        return (completed / total) * 100 if total > 0 else 0
    
    def can_resume(self) -> bool:
        """检查是否可以恢复"""
        return len(self.get_completed_stages()) > 0 and self.get_current_stage() != GenerationStage.COMPLETED
    
    def get_resume_info(self) -> Dict[str, Any]:
        """获取恢复信息"""
        return {
            "session_id": self.session_id,
            "current_stage": self.get_current_stage(),
            "completed_stages": [stage.value for stage in self.get_completed_stages()],
            "progress_percentage": self.get_progress_percentage(),
            "can_resume": self.can_resume(),
            "files_created": self.progress_data["files_created"],
            "errors": self.progress_data["errors"]
        }
    
    def cleanup(self):
        """清理进度文件"""
        if self.progress_file.exists():
            try:
                os.remove(self.progress_file)
                print(f"✅ 进度文件已清理: {self.progress_file}")
            except Exception as e:
                print(f"清理进度文件失败: {e}")
    
    def get_next_stage(self) -> Optional[GenerationStage]:
        """获取下一个需要执行的阶段"""
        completed = self.get_completed_stages()
        all_stages = list(GenerationStage)
        
        for stage in all_stages:
            if stage not in completed and stage != GenerationStage.INITIALIZING:
                return stage
        
        return None
