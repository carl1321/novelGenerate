"""
剧情大纲生成引擎
"""
import json
import uuid
import time
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.utils import llm_client
from app.utils.prompt_manager import PromptManager
from app.core.plot_engine.plot_models import (
    PlotOutline, ChapterOutline, PlotOutlineRequest, PlotOutlineResponse,
    PlotStatus, PlotStructure
)
from app.core.plot_engine.plot_engine_utils import PlotEngineUtils


class PlotEngine:
    """剧情大纲生成引擎"""
    
    def __init__(self):
        self.prompt_manager = PromptManager()
    
    async def generate_plot_outline(self, request: PlotOutlineRequest) -> PlotOutlineResponse:
        """生成剧情大纲"""
        start_time = time.time()
        
        try:
            # 1. 获取世界观和角色信息
            world_view = await self._get_worldview_info(request.worldview_id)
            characters = await self._get_characters_info(request.character_ids)
            
            # 2. 生成剧情大纲
            plot_outline = await self._generate_plot_structure(request, world_view, characters)
            
            # 3. 生成章节大纲
            chapters = await self._generate_chapter_outlines(plot_outline, world_view, characters)
            plot_outline.chapters = chapters
            
            # 4. 生成角色发展弧线
            character_arcs = await self._generate_character_arcs(characters, plot_outline)
            plot_outline.character_arcs = character_arcs
            
            # 5. 更新状态和元数据
            plot_outline.status = PlotStatus.PLANNING
            plot_outline.updated_at = datetime.now()
            
            generation_time = time.time() - start_time
            
            return PlotOutlineResponse(
                success=True,
                plot_outline=plot_outline,
                message="剧情大纲生成成功",
                generation_time=generation_time
            )
            
        except Exception as e:
            generation_time = time.time() - start_time
            return PlotOutlineResponse(
                success=False,
                plot_outline=None,
                message=f"剧情大纲生成失败: {str(e)}",
                generation_time=generation_time
            )
    
    async def _get_worldview_info(self, worldview_id: str) -> Dict[str, Any]:
        """获取世界观信息"""
        # TODO: 从数据库获取世界观信息
        # 这里先返回模拟数据
        return {
            "id": worldview_id,
            "name": "九霄归元界",
            "description": "一个修仙世界",
            "power_system": "灵枢修炼体系",
            "culture": "修仙文化"
        }
    
    async def _get_characters_info(self, character_ids: List[str]) -> List[Dict[str, Any]]:
        """获取角色信息"""
        # TODO: 从数据库获取角色信息
        # 这里先返回模拟数据
        characters = []
        for char_id in character_ids:
            characters.append({
                "id": char_id,
                "name": f"角色{char_id}",
                "role_type": "主角",
                "background": "角色背景",
                "personality": "角色性格"
            })
        return characters
    
    async def _generate_plot_structure(self, 
                                     request: PlotOutlineRequest,
                                     world_view: Dict[str, Any],
                                     characters: List[Dict[str, Any]]) -> PlotOutline:
        """生成剧情结构"""
        # 构建生成提示词
        prompt = PlotEngineUtils.build_plot_structure_prompt(request, world_view, characters)
        
        # 调用LLM生成
        response = await llm_client.generate_chat(
            messages=[
                {"role": "system", "content": "你是一个专业的剧情大纲设计师，擅长根据世界观和角色信息设计完整的剧情结构。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=4000
        )
        
        # 解析响应
        plot_data = PlotEngineUtils.parse_plot_response(response)
        
        # 创建剧情大纲对象
        plot_outline = PlotOutline(
            id=f"plot_{uuid.uuid4().hex[:8]}",
            title=request.title,
            description=request.description,
            worldview_id=request.worldview_id,
            character_ids=request.character_ids,
            structure_type=request.structure_type,
            total_chapters=request.total_chapters,
            target_word_count=request.target_word_count,
            main_conflict=request.main_conflict,
            theme=request.theme,
            tone=request.tone,
            created_by="system"
        )
        
        return plot_outline
    
    async def _generate_chapter_outlines(self,
                                       plot_outline: PlotOutline,
                                       world_view: Dict[str, Any],
                                       characters: List[Dict[str, Any]]) -> List[ChapterOutline]:
        """生成章节大纲"""
        chapters = []
        
        # 根据剧情结构类型生成章节
        if plot_outline.structure_type == PlotStructure.THREE_ACT:
            chapter_templates = PlotEngineUtils.get_three_act_structure(plot_outline.total_chapters)
        elif plot_outline.structure_type == PlotStructure.FIVE_ACT:
            chapter_templates = PlotEngineUtils.get_five_act_structure(plot_outline.total_chapters)
        else:
            chapter_templates = PlotEngineUtils.get_freeform_structure(plot_outline.total_chapters)
        
        # 为每个章节生成详细大纲
        for i, template in enumerate(chapter_templates, 1):
            chapter = await self._generate_single_chapter_outline(
                plot_outline, template, i, world_view, characters
            )
            chapters.append(chapter)
        
        return chapters
    
    async def _generate_single_chapter_outline(self,
                                             plot_outline: PlotOutline,
                                             template: Dict[str, Any],
                                             chapter_number: int,
                                             world_view: Dict[str, Any],
                                             characters: List[Dict[str, Any]]) -> ChapterOutline:
        """生成单个章节大纲"""
        # 构建章节生成提示词
        prompt = PlotEngineUtils.build_chapter_prompt(plot_outline, template, chapter_number, world_view, characters)
        
        # 调用LLM生成
        response = await llm_client.generate_chat(
            messages=[
                {"role": "system", "content": "你是一个专业的章节大纲设计师，擅长设计具体章节的详细内容。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        # 解析响应
        chapter_data = PlotEngineUtils.parse_chapter_response(response)
        
        # 创建章节大纲对象
        chapter = ChapterOutline(
            id=f"chapter_{uuid.uuid4().hex[:8]}",
            plot_outline_id=plot_outline.id,
            chapter_number=chapter_number,
            title=chapter_data.get("title", f"第{chapter_number}章"),
            summary=chapter_data.get("summary", ""),
            main_events=chapter_data.get("main_events", []),
            key_scenes=chapter_data.get("key_scenes", []),
            participating_characters=chapter_data.get("participating_characters", []),
            character_development=chapter_data.get("character_development", {}),
            conflict_escalation=chapter_data.get("conflict_escalation", ""),
            plot_advancement=chapter_data.get("plot_advancement", ""),
            foreshadowing=chapter_data.get("foreshadowing", []),
            estimated_word_count=chapter_data.get("estimated_word_count", 5000)
        )
        
        return chapter
    
    async def _generate_character_arcs(self,
                                     characters: List[Dict[str, Any]],
                                     plot_outline: PlotOutline) -> Dict[str, str]:
        """生成角色发展弧线"""
        character_arcs = {}
        
        for character in characters:
            char_id = character["id"]
            char_name = character["name"]
            
            # 构建角色发展提示词
            prompt = f"""
            为角色 {char_name} 设计完整的发展弧线。
            
            角色信息：
            - 姓名：{char_name}
            - 角色类型：{character.get('role_type', '未知')}
            - 背景：{character.get('background', '未知')}
            - 性格：{character.get('personality', '未知')}
            
            剧情信息：
            - 主题：{plot_outline.theme}
            - 主要冲突：{plot_outline.main_conflict}
            - 总章节数：{plot_outline.total_chapters}
            
            请设计该角色在整个剧情中的发展轨迹，包括：
            1. 初始状态
            2. 成长过程
            3. 关键转折点
            4. 最终归宿
            
            请简洁明了地描述角色发展弧线。
            """
            
            # 调用LLM生成
            response = await llm_client.generate_chat(
                messages=[
                    {"role": "system", "content": "你是一个专业的角色发展设计师，擅长设计角色的成长轨迹。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            character_arcs[char_id] = response.strip()
        
        return character_arcs
