"""
章节大纲生成引擎 - 简化版（基于事件驱动）
"""
import json
import uuid
import time
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.utils.llm_client import get_llm_client
from app.utils.prompt_manager import PromptManager
from .chapter_models_simplified import (
    ChapterOutline, ChapterOutlineRequest, ChapterOutlineResponse,
    Scene, ChapterStatus, PlotFunction
)
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../prompts'))
try:
    from chapter_outline_generation import get_chapter_outline_prompt
except ImportError:
    # 如果导入失败，使用默认的prompt函数
    def get_chapter_outline_prompt(*args, **kwargs):
        return "生成事件驱动章节大纲的prompt"


class ChapterOutlineEngine:
    """章节大纲生成引擎 - 基于事件驱动"""
    
    def __init__(self):
        self.llm_client = None
        self.prompt_manager = None
        self.chapter_database = None
    
    def _ensure_initialized(self):
        """延迟初始化LLM客户端和数据库"""
        if self.llm_client is None:
            self.llm_client = get_llm_client()
            self.prompt_manager = PromptManager()
        
        if self.chapter_database is None:
            from .chapter_database import ChapterOutlineDatabase
            self.chapter_database = ChapterOutlineDatabase()
    
    async def generate_event_driven_chapters(self, plot_outline_id: str, worldview_id: str = None, 
                                           chapter_count: int = 5, start_chapter: int = 1,
                                           event_selection_strategy: str = "auto",
                                           selected_events: List[str] = None,
                                           character_focus: List[str] = None,
                                           additional_requirements: str = "") -> List[ChapterOutline]:
        """生成事件驱动的章节大纲"""
        self._ensure_initialized()
        
        print(f"🎯 开始生成事件驱动的章节大纲...")
        print(f"📊 剧情大纲ID: {plot_outline_id}")
        print(f"📊 章节数量: {chapter_count}")
        
        # TODO: 实现事件驱动的章节生成逻辑
        # 1. 获取剧情大纲、世界观、事件、角色信息
        # 2. 根据事件选择策略选择事件
        # 3. 调用LLM生成章节大纲
        # 4. 解析并返回结果
        
        return []
    
    async def generate_enhanced_chapter_outlines(self, plot_outline: dict, world_view: dict = None, 
                                               characters: list = None, related_events: list = None,
                                               event_integration_mode: str = "auto",
                                               chapter_count: int = None, start_chapter: int = 1,
                                               act_belonging: str = None, additional_requirements: str = "",
                                               generate_event_mappings: bool = True) -> ChapterOutlineResponse:
        """生成增强的章节大纲（基于事件驱动）"""
        self._ensure_initialized()
        
        start_time = time.time()
        
        print(f"🎯 开始生成增强的章节大纲...")
        print(f"📊 剧情大纲ID: {getattr(plot_outline, 'id', '未知')}")
        print(f"📊 章节数量: {chapter_count}")
        
        try:
            # 1. 参数验证和默认值处理
            if chapter_count is None:
                chapter_count = 5
            
            # 2. 转换对象为字典格式
            # 转换剧情大纲
            plot_outline_dict = plot_outline
            if hasattr(plot_outline, 'dict'):
                plot_outline_dict = plot_outline.dict()
            elif hasattr(plot_outline, '__dict__'):
                plot_outline_dict = plot_outline.__dict__
            
            # 转换世界观
            worldview_dict = world_view or {}
            if hasattr(world_view, 'dict'):
                worldview_dict = world_view.dict()
            elif hasattr(world_view, '__dict__'):
                worldview_dict = world_view.__dict__
            
            # 转换事件列表
            events_list = []
            for event in (related_events or []):
                if hasattr(event, 'dict'):
                    events_list.append(event.dict())
                elif hasattr(event, '__dict__'):
                    events_list.append(event.__dict__)
                else:
                    events_list.append(event)
            
            print(f"📊 事件列表详情:")
            print(f"  - 原始事件数量: {len(related_events or [])}")
            print(f"  - 转换后事件数量: {len(events_list)}")
            for i, event in enumerate(events_list):
                print(f"    事件{i+1}: {event.get('title', '无标题')} (ID: {event.get('id', '无ID')})")
            
            # 转换角色列表
            characters_list = []
            for char in (characters or []):
                if hasattr(char, 'dict'):
                    characters_list.append(char.dict())
                elif hasattr(char, '__dict__'):
                    characters_list.append(char.__dict__)
                else:
                    characters_list.append(char)
            
            # 3. 构建prompt（事件驱动版，移除世界观和角色信息）
            prompt = get_chapter_outline_prompt(
                plot_outline=plot_outline_dict,
                events=events_list,
                chapter_count=chapter_count,
                start_chapter=start_chapter,
                act_belonging=act_belonging,
                additional_requirements=additional_requirements
            )
            
            print(f"📝 Prompt长度: {len(prompt)} 字符")
            print(f"📝 完整Prompt内容:")
            print("=" * 100)
            print(prompt)
            print("=" * 100)
            
            # 4. 调用LLM生成章节大纲
            print("🤖 调用LLM生成章节大纲...")
            content = await self.llm_client.generate_text(
                prompt=prompt,
                temperature=0.8,
                max_tokens=50000
            )
            
            print(f"📄 LLM响应长度: {len(content)} 字符")
            
            # 5. 解析JSON响应
            try:
                # 尝试直接解析JSON
                batch_data = json.loads(content)
            except json.JSONDecodeError as e:
                print(f"❌ JSON解析失败: {e}")
                print(f"📄 LLM响应内容: {content[:500]}...")
                
                # 尝试修复常见的JSON问题
                fixed_content = content
                
                # 修复未终止的字符串
                import re
                # 查找未终止的字符串并截断
                fixed_content = re.sub(r'"[^"]*$', '"', fixed_content, flags=re.MULTILINE)
                
                # 尝试提取JSON部分
                json_match = re.search(r'\{.*\}', fixed_content, re.DOTALL)
                if json_match:
                    json_str = json_match.group()
                    try:
                        batch_data = json.loads(json_str)
                        print("✅ 成功从响应中提取JSON")
                    except json.JSONDecodeError as e2:
                        print(f"❌ 提取的JSON仍然无效: {e2}")
                        print(f"📄 尝试修复的JSON: {json_str[:200]}...")
                        
                        # 最后尝试：手动构建基本的章节结构
                        print("🔄 尝试手动构建章节结构...")
                        batch_data = self._build_fallback_chapters(chapter_count, start_chapter, act_belonging)
                else:
                    print("🔄 未找到JSON结构，使用备用方案...")
                    batch_data = self._build_fallback_chapters(chapter_count, start_chapter, act_belonging)
            
            # 6. 解析章节数据
            chapters_data = batch_data.get("chapters", [])
            if len(chapters_data) == 0:
                raise ValueError("LLM未生成任何章节大纲")
            
            print(f"📚 解析到 {len(chapters_data)} 个章节")
            
            # 7. 转换为ChapterOutline对象
            chapters = []
            # 获取下一个可用的章节编号
            next_chapter_number = self.chapter_database.get_next_chapter_number(getattr(plot_outline, 'id', 'unknown'))
            
            for i, chapter_data in enumerate(chapters_data):
                try:
                    # 生成章节ID
                    chapter_id = f"chapter_{uuid.uuid4().hex[:8]}"
                    
                    # 解析场景（事件驱动版），确保所有字段都有内容
                    scenes = []
                    for j, scene_data in enumerate(chapter_data.get("key_scenes", [])):
                        scene = Scene(
                            scene_title=scene_data.get("scene_title", f"第{next_chapter_number + i}章场景{j + 1}"),
                            scene_description=scene_data.get("scene_description", f"第{next_chapter_number + i}章场景{j + 1}描述")
                        )
                        scenes.append(scene)
                    
                    # 获取核心事件名称（LLM生成的事件标题）
                    core_event_name = chapter_data.get("core_event", "")
                    
                    # 验证核心事件是否在可用事件列表中
                    validated_core_event = self._validate_core_event(core_event_name, events_list)
                    
                    # 创建章节对象（事件驱动版），使用自动递增的章节编号
                    chapter = ChapterOutline(
                        id=chapter_id,
                        plot_outline_id=getattr(plot_outline, 'id', 'unknown'),
                        chapter_number=next_chapter_number + i,  # 使用自动递增的章节编号
                        title=chapter_data.get("title", f"第{next_chapter_number + i}章"),
                        act_belonging=chapter_data.get("act_belonging", act_belonging or "第一幕"),
                        chapter_summary=chapter_data.get("chapter_summary", f"第{next_chapter_number + i}章概要"),
                        core_event=validated_core_event,
                        key_scenes=scenes,
                        status=ChapterStatus.OUTLINE,
                        created_at=datetime.now(),
                        updated_at=datetime.now()
                    )
                    chapters.append(chapter)
                        
                except Exception as e:
                    print(f"❌ 解析章节 {i+1} 失败: {e}")
                    continue
            
            if len(chapters) == 0:
                raise ValueError("未能成功解析任何章节大纲")
            
            generation_time = time.time() - start_time
            
            print(f"✅ 成功生成 {len(chapters)} 个章节大纲，耗时 {generation_time:.2f} 秒")
            
            return ChapterOutlineResponse(
                success=True,
                chapters=chapters,
                message=f"成功生成{len(chapters)}个章节大纲",
                generation_time=generation_time
            )
            
        except Exception as e:
            print(f"❌ 生成章节大纲失败: {e}")
            generation_time = time.time() - start_time
            
            return ChapterOutlineResponse(
                success=False,
                chapters=[],
                message=f"生成失败: {str(e)}",
                generation_time=generation_time
            )
    
    def _validate_core_event(self, core_event_name: str, events_list: List[Dict[str, Any]]) -> str:
        """验证核心事件名称，返回事件名称而不是ID"""
        if not core_event_name or not events_list:
            return ""
        
        # 首先检查是否是事件ID，如果是则转换为事件标题
        for event in events_list:
            if event.get('id') == core_event_name:
                return event.get('title', '')
        
        # 尝试精确匹配事件标题
        for event in events_list:
            if event.get('title') == core_event_name:
                return event.get('title', '')
        
        # 尝试模糊匹配事件标题
        core_event_lower = core_event_name.lower()
        for event in events_list:
            event_title = event.get('title', '').lower()
            if core_event_lower in event_title or event_title in core_event_lower:
                return event.get('title', '')
        
        # 如果都没有匹配到，返回LLM生成的事件名称（可能是新编造的事件）
        return core_event_name
    
    def _match_core_event_id(self, core_event_name: str, events_list: List[Dict[str, Any]]) -> str:
        """匹配核心事件名称到实际的事件ID（保留此方法以兼容其他代码）"""
        if not core_event_name or not events_list:
            return ""
        
        # 尝试精确匹配事件标题
        for event in events_list:
            if event.get('title') == core_event_name:
                return event.get('id', '')
        
        # 尝试模糊匹配事件标题
        core_event_lower = core_event_name.lower()
        for event in events_list:
            event_title = event.get('title', '').lower()
            if core_event_lower in event_title or event_title in core_event_lower:
                return event.get('id', '')
        
        # 如果都没有匹配到，返回空字符串（LLM可能编造了新事件）
        return ""
    
    def _build_fallback_chapters(self, chapter_count: int, start_chapter: int, act_belonging: str = None) -> dict:
        """构建备用的章节结构"""
        chapters = []
        for i in range(chapter_count):
            chapter_num = start_chapter + i
            chapter = {
                "chapter_number": chapter_num,
                "title": f"第{chapter_num}章",
                "act_belonging": act_belonging or "第一幕",
                "chapter_summary": f"第{chapter_num}章概要，描述主要情节发展。",
                "core_event": f"核心事件{chapter_num}",
                "key_scenes": [
                    {
                        "scene_title": f"第{chapter_num}章场景1",
                        "scene_description": f"第{chapter_num}章场景1描述，展现主要情节。"
                    }
                ]
            }
            chapters.append(chapter)
        
        return {"chapters": chapters}
    
    def _get_valid_plot_function(self, plot_function: str) -> str:
        """获取有效的剧情功能值"""
        valid_functions = [
            "背景介绍", "引发事件", "上升行动", "高潮", "回落行动", "结局",
            "角色发展", "世界观构建", "伏笔设置", "呼应前文", "过渡"
        ]
        
        # 如果输入值在有效列表中，直接返回
        if plot_function in valid_functions:
            return plot_function
        
        # 尝试模糊匹配
        plot_function_lower = plot_function.lower()
        for valid_func in valid_functions:
            if valid_func in plot_function_lower or plot_function_lower in valid_func:
                return valid_func
        
        # 默认返回"背景介绍"
        return "背景介绍"
    


# 创建全局实例
chapter_engine = ChapterOutlineEngine()