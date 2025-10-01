#!/usr/bin/env python3
"""
小说生成智能体框架使用示例
"""
import asyncio
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "backend"))

from app.core.world.service import WorldService
from app.core.character.service import CharacterService
from app.core.plot.llm_generator import PlotLLMGenerator
from app.core.scoring.service import ScoringService
from app.core.logic.service import LogicReflectionService


async def demonstrate_novel_generation():
    """演示小说生成功能"""
    print("🚀 小说生成智能体框架演示")
    print("=" * 50)
    
    # 检查环境变量
    from app.core.config import settings
    
    if not settings.AZURE_OPENAI_API_KEY or not settings.AZURE_OPENAI_ENDPOINT or not settings.AZURE_OPENAI_DEPLOYMENT_NAME:
        print("❌ 缺少必要的环境变量:")
        if not settings.AZURE_OPENAI_API_KEY:
            print("   - AZURE_OPENAI_API_KEY")
        if not settings.AZURE_OPENAI_ENDPOINT:
            print("   - AZURE_OPENAI_ENDPOINT")
        if not settings.AZURE_OPENAI_DEPLOYMENT_NAME:
            print("   - AZURE_OPENAI_DEPLOYMENT_NAME")
        print("\n请设置以下环境变量:")
        print("export AZURE_OPENAI_API_KEY='your_api_key'")
        print("export AZURE_OPENAI_ENDPOINT='https://your-resource.openai.azure.com/'")
        print("export AZURE_OPENAI_DEPLOYMENT_NAME='your_deployment_name'")
        return
    
    try:
        # 示例核心概念
        core_concepts = [
            "一个现代都市修仙世界，科技与修仙并存，主角是程序员意外获得修仙传承",
            "一个古代修仙世界，主角是废材少年，通过努力和机缘逆天改命",
            "一个末世修仙世界，灵气复苏后人类重新修炼，主角在废墟中崛起"
        ]
        
        print("📝 示例核心概念:")
        for i, concept in enumerate(core_concepts, 1):
            print(f"   {i}. {concept}")
        
        # 让用户选择或输入自定义概念
        choice = input("\n请选择示例概念 (1-3) 或输入自定义概念: ").strip()
        
        if choice in ['1', '2', '3']:
            core_concept = core_concepts[int(choice) - 1]
        else:
            core_concept = choice if choice else core_concepts[0]
        
        print(f"\n🎯 使用核心概念: {core_concept}")
        
        # 1. 创建世界观
        print("\n📖 步骤1: 创建世界观")
        world_service = WorldService()
        
        world_view = await world_service.create_world_view(
            core_concept=core_concept,
            description=None,
            additional_requirements={
                "请根据核心概念生成一个完整、自洽且富有想象力的世界观",
                "包含独特的修炼体系、地理设定、历史背景、文化特色等",
                "确保世界观逻辑合理且适合小说创作",
                "为后续的角色和剧情发展提供丰富的背景"
            }
        )
        
        print(f"✅ 世界观创建成功: {world_view.name}")
        
        # 2. 创建主要角色
        print("\n👥 步骤2: 创建主要角色")
        character_service = CharacterService()
        
        # 创建主角
        protagonist = await character_service.create_character(
            world_view_id=world_view.id,
            character_requirements={
                "请根据世界观和核心概念生成一个精彩的主角",
                "主角应该符合世界观的设定，有鲜明的性格特点",
                "包含详细的背景故事、目标设定、成长潜力等",
                "确保角色有血有肉，能够支撑整个故事的发展"
            }
        )
        
        print(f"✅ 主角创建成功: {protagonist.name}")
        
        # 创建重要配角
        print("\n正在创建重要配角...")
        supporting_characters = []
        
        # 导师角色
        mentor = await character_service.create_character(
            world_view_id=world_view.id,
            character_requirements={
                "请生成一个导师类型的角色",
                "可以是主角的师父、前辈或引路人",
                "角色应该有能力指导主角成长",
                "性格要符合导师的设定，有智慧和经验"
            }
        )
        supporting_characters.append(mentor)
        print(f"✅ 导师角色: {mentor.name}")
        
        # 反派角色
        antagonist = await character_service.create_character(
            world_view_id=world_view.id,
            character_requirements={
                "请生成一个反派角色",
                "可以是主角的敌人、竞争对手或对立势力",
                "角色应该有足够的威胁性和复杂性",
                "背景和动机要合理，不是单纯的恶人"
            }
        )
        supporting_characters.append(antagonist)
        print(f"✅ 反派角色: {antagonist.name}")
        
        all_characters = [protagonist] + supporting_characters
        
        # 3. 生成剧情大纲
        print("\n📚 步骤3: 生成剧情大纲")
        plot_generator = PlotLLMGenerator()
        
        plot_outline = await plot_generator.generate_plot_outline(
            world_view=world_view.dict(),
            characters=[char.dict() for char in all_characters],
            requirements={
                "请根据世界观和角色生成一个完整的剧情大纲",
                "剧情要符合核心概念，有清晰的起承转合",
                "包含主要冲突、关键事件、角色发展等",
                "确保剧情逻辑合理且引人入胜，适合小说创作"
            }
        )
        
        print(f"✅ 剧情大纲生成成功: {plot_outline.title}")
        
        # 4. 生成具体剧情节点
        print("\n🎭 步骤4: 生成具体剧情节点")
        
        # 开篇剧情
        opening_plot = await plot_generator.generate_plot_node({
            "title": "故事开篇",
            "description": "主角的初始状态和故事开始的关键事件",
            "characters": [protagonist.name],
            "location": "根据世界观设定",
            "conflict_type": "个人成长",
            "importance": 9,
            "请生成一个引人入胜的开篇剧情节点",
            "要能够快速吸引读者，展现主角的特点和世界观"
        })
        
        print(f"✅ 开篇剧情: {opening_plot.title}")
        
        # 高潮剧情
        climax_plot = await plot_generator.generate_plot_node({
            "title": "故事高潮",
            "description": "故事的主要冲突和转折点",
            "characters": [char.name for char in all_characters],
            "location": "根据剧情需要",
            "conflict_type": "正邪对立",
            "importance": 10,
            "请生成一个紧张刺激的高潮剧情节点",
            "要体现主角的成长和主要冲突的解决"
        })
        
        print(f"✅ 高潮剧情: {climax_plot.title}")
        
        # 5. 内容评分
        print("\n⭐ 步骤5: 内容评分")
        scoring_service = ScoringService()
        
        content_for_scoring = {
            "world_view": world_view.dict(),
            "characters": [char.dict() for char in all_characters],
            "plot": plot_outline.dict(),
            "plot_nodes": [opening_plot.dict(), climax_plot.dict()]
        }
        
        scores = await scoring_service.score_content(content_for_scoring)
        print(f"✅ 内容评分完成:")
        print(f"   总分: {scores['total_score']:.1f}/10")
        for dimension, score in scores['scores'].items():
            print(f"   {dimension}: {score:.1f}/10")
        
        # 6. 逻辑检查
        print("\n🔍 步骤6: 逻辑检查")
        logic_service = LogicReflectionService()
        
        logic_check = await logic_service.check_logic_consistency(content_for_scoring)
        print(f"✅ 逻辑检查完成: {logic_check['status']}")
        
        # 7. 生成分析报告
        print("\n📊 步骤7: 生成分析报告")
        
        report = await logic_service.generate_reflection_report(content_for_scoring)
        print(f"✅ 分析报告生成完成: {report['status']}")
        
        print("\n🎉 小说生成演示完成！")
        print("=" * 50)
        print("📁 生成的文件已保存到 novel/ 目录下:")
        print("   - 世界观设计_*.md")
        print("   - 角色档案_*.md")
        print("   - 剧情大纲_*.md")
        print("   - 分析报告_*.md")
        print(f"\n💡 基于核心概念: '{core_concept}'")
        print("   系统已生成完整的小说设定，您可以查看这些文件了解详细内容")
        
        # 显示生成的角色列表
        print(f"\n👥 生成的角色:")
        for i, char in enumerate(all_characters, 1):
            print(f"   {i}. {char.name} ({char.cultivation_level.value}) - {char.background[:50]}...")
        
    except Exception as e:
        print(f"❌ 生成过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # 设置环境变量（请根据实际情况修改）
    os.environ.setdefault('AZURE_OPENAI_API_KEY', 'your_azure_openai_api_key_here')
    os.environ.setdefault('AZURE_OPENAI_ENDPOINT', 'https://your-resource-name.openai.azure.com/')
    os.environ.setdefault('AZURE_OPENAI_DEPLOYMENT_NAME', 'your-deployment-name')
    os.environ.setdefault('AZURE_OPENAI_API_VERSION', '2024-02-15-preview')
    
    asyncio.run(demonstrate_novel_generation())