"""
详细剧情生成引擎
"""
import uuid
from typing import Dict, Any, Optional
from datetime import datetime

from app.utils.llm_client import get_llm_client
from app.core.detailed_plot.detailed_plot_models import DetailedPlot, DetailedPlotRequest, DetailedPlotStatus
from app.core.detailed_plot.detailed_plot_database import DetailedPlotDatabase
from app.core.chapter_engine.chapter_database import ChapterOutlineDatabase
from app.core.plot_engine.plot_database import PlotOutlineDatabase
from app.core.world.database import WorldViewDatabase
from app.core.character.database import CharacterDatabase
from app.core.event_generator.event_database import EventDatabase
from app.core.logic.service import LogicReflectionService
from app.core.logic.models import LogicStatus
from app.utils.prompt_manager import PromptManager
from app.utils.file_writer import FileWriter


class DetailedPlotEngine:
    """详细剧情生成引擎"""
    
    def __init__(self):
        self.llm_client = get_llm_client()
        self.detailed_plot_database = DetailedPlotDatabase()
        self.chapter_database = ChapterOutlineDatabase()
        self.plot_database = PlotOutlineDatabase()
        self.world_database = WorldViewDatabase()
        self.character_database = CharacterDatabase()
        self.event_database = EventDatabase()
        self.logic_service = LogicReflectionService()
        self.prompt_manager = PromptManager()
        self.file_writer = FileWriter()
    
    async def generate_detailed_plot(self, request: DetailedPlotRequest) -> DetailedPlot:
        """生成详细剧情"""
        print(f"🔍 [DEBUG] 详细剧情生成引擎开始工作")
        print(f"📋 [DEBUG] 请求: {request.title}")
        
        try:
            # 1. 获取章节大纲信息
            print(f"🔍 [DEBUG] 步骤1: 获取章节大纲信息...")
            chapter_outline = self.chapter_database.get_chapter_outline(request.chapter_outline_id)
            if not chapter_outline:
                raise ValueError(f"章节大纲不存在: {request.chapter_outline_id}")
            print(f"✅ [DEBUG] 章节大纲获取成功: {chapter_outline.title}")
            print(f"📋 [DEBUG] 章节事件: {getattr(chapter_outline, 'main_events', '无事件')}")
            
            # 2. 获取剧情大纲信息
            print(f"🔍 [DEBUG] 步骤2: 获取剧情大纲信息...")
            plot_outline = self.plot_database.get_plot_outline(request.plot_outline_id)
            if not plot_outline:
                raise ValueError(f"剧情大纲不存在: {request.plot_outline_id}")
            print(f"✅ [DEBUG] 剧情大纲获取成功: {plot_outline.title}")
            
            # 3. 获取世界观信息
            print(f"🔍 [DEBUG] 步骤3: 获取世界观信息...")
            world_view = self.world_database.get_worldview(plot_outline.worldview_id)
            if not world_view:
                raise ValueError(f"世界观不存在: {plot_outline.worldview_id}")
            print(f"✅ [DEBUG] 世界观获取成功: {world_view.get('name', '未知世界观')}")
            
            # 4. 获取角色信息
            print(f"🔍 [DEBUG] 步骤4: 获取角色信息...")
            characters = self.character_database.get_characters_by_worldview(plot_outline.worldview_id)
            print(f"✅ [DEBUG] 角色信息获取成功: {len(characters)}个角色")
            
            # 5. 获取相关事件信息 - 新增
            print(f"🔍 [DEBUG] 步骤5: 获取相关事件信息...")
            events = []
            if hasattr(chapter_outline, 'key_scenes') and chapter_outline.key_scenes:
                # 从章节场景中提取关联的事件ID
                related_event_ids = []
                for scene in chapter_outline.key_scenes:
                    if hasattr(scene, 'related_events') and scene.related_events:
                        related_event_ids.extend(scene.related_events)
                
                # 去重并获取事件详情
                unique_event_ids = list(set(related_event_ids))
                if unique_event_ids:
                    for event_id in unique_event_ids:
                        event = self.event_database.get_event_by_id(event_id)
                        if event:
                            events.append(event)
                print(f"✅ [DEBUG] 相关事件获取成功: {len(events)}个事件")
            else:
                print(f"⚠️ [DEBUG] 章节无关键场景或关联事件")
            
            # 6. 构建生成提示
            print(f"🔍 [DEBUG] 步骤6: 构建生成提示...")
            prompt = self.prompt_manager.get_detailed_plot_prompt(
                chapter_outline=chapter_outline,
                plot_outline=plot_outline,
                world_view=world_view,
                characters=characters,
                events=events,
                additional_requirements=request.additional_requirements
            )
            print(f"✅ [DEBUG] 提示构建成功: {len(prompt)}字符")
            
            # 7. 调用LLM生成详细剧情
            print(f"🔍 [DEBUG] 步骤7: 调用LLM生成详细剧情...")
            response = await self.llm_client.generate_text(
                prompt=prompt,
                temperature=0.7,
                max_tokens=12000
            )
            print(f"✅ [DEBUG] LLM响应获取成功: {len(response) if response else 0}字符")
            
            # 8. 解析响应
            print(f"🔍 [DEBUG] 步骤8: 解析响应...")
            detailed_plot_content = self._parse_detailed_plot_response(response)
            print(f"✅ [DEBUG] 响应解析成功: {len(detailed_plot_content)}字符")
            
            # 9. 创建详细剧情对象（不进行自动逻辑检查）
            print(f"🔍 [DEBUG] 步骤9: 创建详细剧情对象...")
            detailed_plot_id = f"detailed_plot_{request.chapter_outline_id}_{uuid.uuid4().hex[:8]}"
            
            detailed_plot = DetailedPlot(
                id=detailed_plot_id,
                chapter_outline_id=request.chapter_outline_id,
                plot_outline_id=request.plot_outline_id,
                title=request.title,
                content=detailed_plot_content,
                word_count=len(detailed_plot_content),
                status=DetailedPlotStatus.DRAFT,
                logic_check_result=None,
                logic_status=None,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            print(f"✅ [DEBUG] 详细剧情对象创建成功: {detailed_plot_id}")
            
            # 10. 保存到数据库
            print(f"🔍 [DEBUG] 步骤10: 保存到数据库...")
            self.detailed_plot_database.save_detailed_plot(detailed_plot)
            print(f"✅ [DEBUG] 数据库保存成功")
            
            # 11. 生成MD文件
            print(f"🔍 [DEBUG] 步骤10: 生成MD文件...")
            try:
                md_file_path = self.file_writer.write_detailed_plot(detailed_plot.dict())
                print(f"✅ [DEBUG] MD文件生成成功: {md_file_path}")
            except Exception as e:
                print(f"⚠️ [DEBUG] MD文件生成失败: {str(e)}")
                # 不影响主要流程，继续执行
            
            return detailed_plot
            
        except Exception as e:
            print(f"❌ [DEBUG] 详细剧情生成失败: {str(e)}")
            print(f"❌ [DEBUG] 错误类型: {type(e).__name__}")
            import traceback
            print(f"❌ [DEBUG] 错误堆栈:")
            traceback.print_exc()
            raise e
    
    
    def _parse_detailed_plot_response(self, response: str) -> str:
        """解析LLM响应"""
        # 简单的响应解析，直接返回内容
        return response.strip()
