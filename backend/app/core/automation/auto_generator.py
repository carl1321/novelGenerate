"""
完全自动化生成引擎
"""
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime

from app.core.world.service import WorldService
from app.core.character.service import CharacterService
from app.core.plot.llm_generator import PlotLLMGenerator
from app.core.plot_engine import PlotEngine
from app.core.plot.foreshadowing_system import ForeshadowingSystem
from app.core.plot.chapter_generator import ChapterGenerator
from app.core.scoring.service import ScoringService
from app.core.logic.service import LogicReflectionService
from app.core.automation.decision_engine import IntelligentDecisionEngine
from app.core.automation.rewrite_engine import AutoRewriteEngine
from app.utils.file_writer import FileWriter
from app.core.automation.progress_manager import ProgressManager, GenerationStage
from app.core.event_generator import EventGenerator


class AutoGenerator:
    """完全自动化生成引擎"""
    
    def __init__(self, session_id: str = None):
        self.world_service = WorldService()
        self.character_service = CharacterService()
        self.plot_generator = PlotLLMGenerator()
        self.plot_engine = PlotEngine()  # 新的事件驱动剧情引擎
        self.foreshadowing_system = ForeshadowingSystem()
        self.chapter_generator = ChapterGenerator()
        self.scoring_service = ScoringService()
        self.logic_service = LogicReflectionService()
        self.decision_engine = IntelligentDecisionEngine()
        self.rewrite_engine = AutoRewriteEngine()
        self.file_writer = FileWriter()
        self.progress_manager = ProgressManager(session_id)
        self.event_generator = EventGenerator()
        
        # 配置参数
        self.max_iterations = 5
        self.min_score_threshold = 7.0
        self.auto_character_count = True
        self.enable_chapter_generation = True
        self.target_chapter_count = 20
    
    async def generate_novel(self, core_concept: str, 
                           auto_optimize: bool = True, resume: bool = False) -> Dict[str, Any]:
        """完全自动化生成小说"""
        if resume and self.progress_manager.can_resume():
            print(f"🔄 恢复生成会话: {self.progress_manager.session_id}")
            print(f"📊 当前进度: {self.progress_manager.get_progress_percentage():.1f}%")
            print(f"📍 当前阶段: {self.progress_manager.get_current_stage()}")
        else:
            print(f"🚀 开始自动化生成小说: {core_concept}")
            self.progress_manager.progress_data["core_concept"] = core_concept
            self.progress_manager.save_progress()
        
        print("=" * 60)
        
        try:
            # 检查是否需要恢复
            if resume and self.progress_manager.can_resume():
                content = await self._resume_generation(core_concept, auto_optimize)
            else:
                # 1. 生成初始内容
                print("\n📖 步骤1: 生成初始内容...")
                content = await self._generate_initial_content(core_concept)
            
            if not auto_optimize:
                return await self._finalize_content(content, core_concept)
            
            # 2. 自动优化循环
            print(f"\n🔄 步骤2: 开始自动优化循环 (最多{self.max_iterations}轮)...")
            content = await self._auto_optimization_loop(content, core_concept)
            
            # 3. 生成章节内容（如果启用）
            if self.enable_chapter_generation:
                print("\n📖 步骤3: 生成章节内容...")
                content = await self._generate_chapters(content, core_concept)
            
            # 4. 生成最终内容
            print("\n🎉 步骤4: 生成最终内容...")
            return await self._finalize_content(content, core_concept)
            
        except Exception as e:
            print(f"❌ 自动化生成失败: {e}")
            import traceback
            traceback.print_exc()
            return {"error": str(e), "core_concept": core_concept}
    
    async def _resume_generation(self, core_concept: str, auto_optimize: bool) -> Dict[str, Any]:
        """恢复生成过程"""
        print("🔄 从断点恢复生成...")
        
        # 获取已生成的内容
        content = self.progress_manager.get_generated_content()
        current_stage = self.progress_manager.get_current_stage()
        
        # 根据当前阶段决定从哪里继续
        if current_stage == GenerationStage.WORLDVIEW_GENERATED:
            # 从角色生成开始
            print("📖 继续生成角色...")
            content = await self._generate_characters(content, core_concept)
        elif current_stage == GenerationStage.CHARACTERS_GENERATED:
            # 从剧情大纲开始
            print("📚 继续生成剧情大纲...")
            content = await self._generate_plot_outline(content, core_concept)
        elif current_stage == GenerationStage.PLOT_OUTLINE_GENERATED:
            # 从伏笔网络开始
            print("🔗 继续生成伏笔网络...")
            content = await self._generate_foreshadowing(content, core_concept)
        elif current_stage == GenerationStage.FORESHADOWING_GENERATED:
            # 从反派生成开始
            print("👹 继续生成反派...")
            content = await self._generate_antagonists(content, core_concept)
        elif current_stage == GenerationStage.ANTAGONISTS_GENERATED:
            # 从章节生成开始
            print("📖 继续生成章节...")
            content = await self._generate_chapters(content, core_concept)
        
        # 继续后续步骤
        if auto_optimize and not self.progress_manager.is_stage_completed(GenerationStage.OPTIMIZATION_COMPLETED):
            print(f"\n🔄 继续优化循环...")
            content = await self._auto_optimization_loop(content, core_concept)
        
        return content
    
    def get_progress_info(self) -> Dict[str, Any]:
        """获取当前进度信息"""
        return self.progress_manager.get_resume_info()
    
    def cleanup_progress(self):
        """清理进度文件"""
        self.progress_manager.cleanup()
    
    async def _generate_initial_content(self, core_concept: str) -> Dict[str, Any]:
        """生成初始内容"""
        # 生成世界观
        print("  📖 生成世界观...")
        world_view = await self.world_service.create_world_view(
            core_concept=core_concept,
            description=None,
            additional_requirements={
                "请根据核心概念生成完整的世界观设定",
                "包含力量体系、地理设定、历史背景、文化特色等",
                "确保世界观逻辑自洽且富有想象力"
            }
        )
        print(f"  ✅ 世界观生成完成: {world_view.name}")
        
        # 更新进度
        self.progress_manager.update_stage(GenerationStage.WORLDVIEW_GENERATED, {"world_view": world_view.dict()})
        
        # 智能决定角色数量
        character_count = await self.decision_engine.determine_character_count(world_view.dict())
        print(f"  👥 智能决定生成{character_count}个角色...")
        
        # 生成角色（包括主角、配角、反派等）
        characters = []
        character_types = ["主角", "重要配角", "反派", "导师", "盟友"]
        
        for i in range(character_count):
            char_type = character_types[i] if i < len(character_types) else "次要角色"
            print(f"  👤 生成{char_type}...")
            
            character = await self.character_service.create_character(
                world_view_id=world_view.id,
                character_requirements=[
                    f"请生成一个{char_type}",
                    "角色应该符合世界观的设定，有鲜明的性格特点",
                    "包含基础信息、内在特质、能力设定、社会关系、成长弧线",
                    f"这是第{i+1}个角色，请确保与已有角色有合理的关联",
                    "如果是反派角色，请确保与主角形成鲜明对比，有合理的动机"
                ]
            )
            characters.append(character)
            print(f"  ✅ {char_type}生成完成: {character.name}")
        
        # 更新进度
        self.progress_manager.update_stage(GenerationStage.CHARACTERS_GENERATED, {"characters": [char.dict() for char in characters]})
        
        # 按照新的流程：世界观 → 角色生成 → 剧情大纲 → 章节大纲 → 事件生成 → 剧情生成
        
        # 3. 生成剧情大纲
        print("  📚 生成剧情大纲...")
        plot_outline = await self.plot_generator.generate_plot_outline(
            world_view=world_view.dict(),
            characters=[char.dict() for char in characters],
            requirements={"core_concept": core_concept}
        )
        print(f"  ✅ 剧情大纲生成完成: {plot_outline.title}")
        
        # 保存剧情大纲到MD文件
        print("  💾 保存剧情大纲...")
        plot_outline_file = self.file_writer.write_plot_outline(plot_outline.dict())
        print(f"  ✅ 剧情大纲已保存到: {plot_outline_file}")
        
        # 更新进度
        self.progress_manager.update_stage(GenerationStage.PLOT_OUTLINE_GENERATED, {"plot_outline": plot_outline.dict()})
        
        # 4. 生成章节大纲
        print("  📖 生成章节大纲...")
        chapters = await self.chapter_generator.generate_chapter_series(
            plot_outline=plot_outline.dict(),
            world_view=world_view.dict(),
            characters=[char.dict() for char in characters],
            foreshadowing_network=None,  # 暂时跳过伏笔网络
            world_view_id=world_view.id
        )
        print(f"  ✅ 章节大纲生成完成: {len(chapters)}章")
        
        # 更新进度
        self.progress_manager.update_stage(GenerationStage.CHAPTERS_GENERATED, {"chapters": [chapter.dict() for chapter in chapters]})
        
        # 5. 生成事件序列
        print("  📅 生成事件序列...")
        events = await self.event_generator.generate_event_sequence(
            world_view=world_view.dict(),
            characters=[char.dict() for char in characters],
            plot_outline=plot_outline.dict(),
            event_count=20  # 生成20个事件
        )
        print(f"  ✅ 事件序列生成完成: {len(events)}个事件")
        
        # 保存事件序列到MD文件
        print("  💾 保存事件序列...")
        events_file = self.file_writer.write_events_sequence(events)
        print(f"  ✅ 事件序列已保存到: {events_file}")
        
        # 更新进度
        self.progress_manager.update_stage(GenerationStage.EVENTS_GENERATED, {"events": [event.dict() for event in events]})
        
        # 6. 详细剧情生成（手动交互）
        print("  🎭 详细剧情生成需要手动交互")
        print("  📝 请使用 generate_detailed_plot_for_chapter() 方法选择特定章节生成详细剧情")
        
        # 生成伏笔网络（基于剧情大纲）
        print("  🔮 生成伏笔网络...")
        foreshadowing_network = await self.foreshadowing_system.create_foreshadowing_network(
            plot_outline=plot_outline.dict(),
            characters=[char.dict() for char in characters],
            world_view=world_view.dict()
        )
        print(f"  ✅ 伏笔网络生成完成: {len(foreshadowing_network.setups)}个伏笔")
        
        # 更新进度
        self.progress_manager.update_stage(GenerationStage.FORESHADOWING_GENERATED, {"foreshadowing_network": foreshadowing_network.dict()})
        
        return {
            "world_view": world_view.dict(),
            "characters": [char.dict() for char in characters],
            "plot_outline": plot_outline.dict(),
            "chapters": [chapter.dict() for chapter in chapters],
            "events": [event.dict() for event in events],
            "foreshadowing_network": foreshadowing_network.__dict__,
            "core_concept": core_concept,
            "generation_time": datetime.now().isoformat()
        }
    
    async def _auto_optimization_loop(self, content: Dict[str, Any], 
                                    core_concept: str) -> Dict[str, Any]:
        """自动优化循环"""
        iteration = 0
        previous_scores = None
        
        while iteration < self.max_iterations:
            iteration += 1
            print(f"\n  🔄 第{iteration}轮优化...")
            
            # 评分
            print("    ⭐ 进行内容评分...")
            scores = await self.scoring_service.score_content(content)
            print(f"    📊 当前评分: {scores['total_score']:.1f}/10")
            
            # 决策
            print("    🧠 智能决策分析...")
            decision = await self.decision_engine.analyze_scores(scores)
            print(f"    💡 决策结果: {decision.reason}")
            print(f"    🎯 重写策略: {decision.strategy.value}")
            print(f"    📈 优先级: {decision.priority}/10")
            print(f"    🎯 目标模块: {', '.join(decision.target_modules)}")
            
            # 检查是否应该继续
            should_continue = await self.decision_engine.should_continue_iteration(
                iteration, scores, self.max_iterations
            )
            
            if not should_continue:
                print(f"    ✅ 达到优化目标，停止迭代")
                break
            
            if not decision.should_rewrite:
                print(f"    ✅ 内容质量已达标，无需重写")
                break
            
            # 执行重写
            print(f"    🔧 执行重写: {decision.strategy.value}")
            content = await self.rewrite_engine.rewrite_content(content, decision)
            
            # 更新历史分数
            previous_scores = scores
            
            print(f"    ✅ 第{iteration}轮优化完成")
        
        print(f"\n  🎉 自动优化完成，共进行了{iteration}轮优化")
        return content
    
    async def _generate_chapters(self, content: Dict[str, Any], 
                               core_concept: str) -> Dict[str, Any]:
        """生成章节内容"""
        print(f"📚 开始生成{self.target_chapter_count}章内容...")
        
        try:
            # 获取剧情大纲
            plot_outline = content.get("plot_outline", {})
            if not plot_outline:
                print("⚠️ 没有找到剧情大纲，跳过章节生成")
                return content
            
            # 基于剧情段落生成章节
            chapters = await self.chapter_generator.generate_chapter_series(
                plot_outline=plot_outline,
                world_view=content.get("world_view", {}),
                characters=content.get("characters", []),
                foreshadowing_network=content.get("foreshadowing_network"),
                world_view_id=content.get("world_view", {}).get("id")
            )
            
            # 保存章节内容
            chapter_files = []
            for chapter in chapters:
                chapter_dict = {
                    "chapter_number": chapter.chapter_number,
                    "title": chapter.title,
                    "content": chapter.content,
                    "word_count": chapter.word_count,
                    "key_events": chapter.key_events,
                    "foreshadowing_used": chapter.foreshadowing_used
                }
                
                file_path = self.file_writer.write_novel_chapter(chapter_dict)
                chapter_files.append(file_path)
                print(f"  ✅ 第{chapter.chapter_number}章已保存: {file_path}")
            
            # 更新内容
            content["chapters"] = [chapter.__dict__ for chapter in chapters]
            content["chapter_files"] = chapter_files
            content["chapter_summary"] = self.chapter_generator.get_chapter_summary(chapters)
            
            print(f"🎉 章节生成完成: 共{len(chapters)}章，{sum(c.word_count for c in chapters)}字")
            return content
            
        except Exception as e:
            print(f"❌ 章节生成失败: {e}")
            return content
    
    async def _finalize_content(self, content: Dict[str, Any], 
                              core_concept: str) -> Dict[str, Any]:
        """生成最终内容"""
        # 最终评分
        print("  ⭐ 进行最终评分...")
        final_scores = await self.scoring_service.score_content(content)
        
        # 逻辑检查
        print("  🔍 进行最终逻辑检查...")
        logic_check = await self.logic_service.check_logic_consistency(content)
        
        # 生成分析报告
        print("  📊 生成分析报告...")
        report = await self.logic_service.generate_reflection_report(content)
        
        # 保存文件
        print("  💾 保存生成内容...")
        try:
            # 保存世界观
            world_file = self.file_writer.write_world_view(content['world_view'])
            print(f"    📄 世界观已保存: {world_file}")
            
            # 保存角色档案
            for i, character in enumerate(content['characters']):
                char_file = self.file_writer.write_character_profile(character)
                print(f"    👤 角色{i+1}已保存: {char_file}")
            
            # 保存剧情大纲
            plot_file = self.file_writer.write_plot_outline(content['plot_outline'])
            print(f"    📚 剧情大纲已保存: {plot_file}")
            
            # 保存章节大纲
            if content.get('chapters'):
                chapters_file = self.file_writer.write_chapter_outline(content['chapters'])
                print(f"    📖 章节大纲已保存: {chapters_file}")
            
            # 保存事件序列
            if content.get('events'):
                events_file = self.file_writer.write_events_sequence(content['events'])
                print(f"    📅 事件序列已保存: {events_file}")
            
            # 保存伏笔网络
            if content.get('foreshadowing_network'):
                foreshadowing_file = self.file_writer.write_foreshadowing_network(content['foreshadowing_network'])
                print(f"    🔮 伏笔网络已保存: {foreshadowing_file}")
            
            # 保存分析报告
            report_file = self.file_writer.write_analysis_report({
                "scores": final_scores,
                "logic_check": logic_check,
                "report": report,
                "generation_info": {
                    "core_concept": core_concept,
                    "generation_time": content.get('generation_time'),
                    "total_characters": len(content['characters'])
                }
            })
            print(f"    📊 分析报告已保存: {report_file}")
            
        except Exception as e:
            print(f"    ❌ 保存文件失败: {e}")
        
        # 返回最终结果
        return {
            "content": content,
            "scores": final_scores,
            "logic_check": logic_check,
            "report": report,
            "generation_info": {
                "core_concept": core_concept,
                "generation_time": content.get('generation_time'),
                "total_characters": len(content['characters']),
                "world_name": content['world_view'].get('name', '未知'),
                "plot_title": content['plot_outline'].get('title', '未知')
            }
        }
    
    async def batch_generate(self, core_concepts: List[str], 
                           auto_optimize: bool = True) -> List[Dict[str, Any]]:
        """批量生成多个小说"""
        print(f"🚀 开始批量生成{len(core_concepts)}个小说...")
        print("=" * 60)
        
        results = []
        
        for i, concept in enumerate(core_concepts, 1):
            print(f"\n📖 生成第{i}/{len(core_concepts)}个小说: {concept}")
            print("-" * 40)
            
            try:
                result = await self.generate_novel(concept, auto_optimize)
                results.append(result)
                print(f"✅ 第{i}个小说生成完成")
                
            except Exception as e:
                error_result = {
                    "error": str(e),
                    "core_concept": concept,
                    "generation_info": {
                        "core_concept": concept,
                        "generation_time": datetime.now().isoformat(),
                        "status": "failed"
                    }
                }
                results.append(error_result)
                print(f"❌ 第{i}个小说生成失败: {e}")
        
        print(f"\n🎉 批量生成完成，成功{len([r for r in results if 'error' not in r])}个，失败{len([r for r in results if 'error' in r])}个")
        return results
    
    async def generate_detailed_plot_for_chapter(self, chapter_index: int, 
                                              selected_events: List[str] = None) -> Dict[str, Any]:
        """
        为指定章节生成详细剧情
        
        Args:
            chapter_index: 章节索引（从0开始）
            selected_events: 选择的事件ID列表，如果为None则自动选择相关事件
            
        Returns:
            包含详细剧情的字典
        """
        print(f"🎭 开始为第{chapter_index + 1}章生成详细剧情...")
        
        try:
            # 获取当前进度信息
            resume_info = self.progress_manager.get_resume_info()
            if not resume_info:
                raise Exception("没有找到可用的生成进度，请先运行完整生成流程")
            
            # 从进度中获取必要的数据
            progress_data = resume_info.get('progress', {})
            world_view = progress_data.get('world_view')
            characters = progress_data.get('characters', [])
            chapters = progress_data.get('chapters', [])
            events = progress_data.get('events', [])
            
            if not all([world_view, characters, chapters, events]):
                raise Exception("缺少必要的生成数据，请先运行完整生成流程")
            
            # 检查章节索引是否有效
            if chapter_index >= len(chapters):
                raise Exception(f"章节索引{chapter_index}超出范围，共有{len(chapters)}章")
            
            target_chapter = chapters[chapter_index]
            print(f"  📖 目标章节: {target_chapter.get('title', f'第{chapter_index + 1}章')}")
            
            # 如果没有指定事件，则自动选择相关事件
            if selected_events is None:
                # 根据章节的主要事件选择相关事件
                chapter_events = target_chapter.get('main_events', [])
                if chapter_events:
                    selected_events = chapter_events
                else:
                    # 如果没有指定事件，选择前几个事件
                    selected_events = [event['id'] for event in events[:3]]
            
            print(f"  📅 选择的事件: {len(selected_events)}个")
            
            # 过滤出选择的事件
            filtered_events = [event for event in events if event['id'] in selected_events]
            
            # 使用剧情引擎生成详细剧情
            detailed_plot = await self.plot_engine.generate_plot(
                world_view=world_view,
                characters=characters,
                events=filtered_events,
                plot_requirements={
                    "title": f"{target_chapter.get('title', f'第{chapter_index + 1}章')}的详细剧情",
                    "description": f"基于章节大纲和选择事件的详细剧情",
                    "target_length": 1,  # 只生成一章
                    "chapter_focus": chapter_index
                }
            )
            
            print(f"  ✅ 详细剧情生成完成: {detailed_plot.title}")
            
            # 保存详细剧情到MD文件
            print("  💾 保存详细剧情...")
            plot_file = self.file_writer.write_plot_outline(detailed_plot.dict())
            print(f"  ✅ 详细剧情已保存到: {plot_file}")
            
            # 质量检查
            print("  🔍 进行质量检查...")
            try:
                # 逻辑检查
                logic_result = await self.logic_service.check_plot_logic(
                    plot_outline=detailed_plot.dict(),
                    characters=characters,
                    world_view=world_view
                )
                print(f"  📊 逻辑检查完成: {logic_result.get('score', 0)}/10")
                
                # 质量评分
                scoring_result = await self.scoring_service.score_plot(
                    plot_outline=detailed_plot.dict(),
                    characters=characters,
                    world_view=world_view
                )
                print(f"  ⭐ 质量评分完成: {scoring_result.get('overall_score', 0)}/10")
                
            except Exception as e:
                print(f"  ⚠️ 质量检查出现异常: {e}")
            
            return {
                "chapter_index": chapter_index,
                "chapter": target_chapter,
                "selected_events": selected_events,
                "detailed_plot": detailed_plot.dict(),
                "logic_check": logic_result if 'logic_result' in locals() else None,
                "scoring_result": scoring_result if 'scoring_result' in locals() else None,
                "plot_file": plot_file
            }
            
        except Exception as e:
            print(f"  ❌ 详细剧情生成失败: {e}")
            raise e
    
    def list_available_chapters(self) -> List[Dict[str, Any]]:
        """
        列出可用的章节供用户选择
        
        Returns:
            章节列表
        """
        try:
            resume_info = self.progress_manager.get_resume_info()
            if not resume_info:
                print("❌ 没有找到可用的生成进度")
                return []
            
            progress_data = resume_info.get('progress', {})
            chapters = progress_data.get('chapters', [])
            
            if not chapters:
                print("❌ 没有找到章节数据")
                return []
            
            print(f"📚 找到{len(chapters)}个章节:")
            for i, chapter in enumerate(chapters):
                print(f"  {i + 1}. {chapter.get('title', f'第{i + 1}章')}")
                print(f"     摘要: {chapter.get('summary', '无摘要')[:100]}...")
                print(f"     主要事件: {len(chapter.get('main_events', []))}个")
                print()
            
            return chapters
            
        except Exception as e:
            print(f"❌ 获取章节列表失败: {e}")
            return []
    
    def list_available_events(self) -> List[Dict[str, Any]]:
        """
        列出可用的事件供用户选择
        
        Returns:
            事件列表
        """
        try:
            resume_info = self.progress_manager.get_resume_info()
            if not resume_info:
                print("❌ 没有找到可用的生成进度")
                return []
            
            progress_data = resume_info.get('progress', {})
            events = progress_data.get('events', [])
            
            if not events:
                print("❌ 没有找到事件数据")
                return []
            
            print(f"📅 找到{len(events)}个事件:")
            for i, event in enumerate(events):
                print(f"  {i + 1}. {event.get('title', f'事件{i + 1}')}")
                print(f"     类型: {event.get('event_type', '未知')}")
                print(f"     重要性: {event.get('importance', '未知')}")
                print(f"     描述: {event.get('description', '无描述')[:100]}...")
                print()
            
            return events
            
        except Exception as e:
            print(f"❌ 获取事件列表失败: {e}")
            return []
    
    async def quick_generate(self, core_concept: str) -> Dict[str, Any]:
        """快速生成（不进行优化）"""
        print(f"⚡ 快速生成模式: {core_concept}")
        return await self.generate_novel(core_concept, auto_optimize=False)
