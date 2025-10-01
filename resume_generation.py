"""
断点续传生成脚本
"""
import asyncio
import sys
from pathlib import Path
from typing import Optional

# 添加项目路径
project_root = Path('.')
sys.path.insert(0, str(project_root / 'backend'))

from app.core.automation.auto_generator import AutoGenerator
from app.core.automation.progress_manager import ProgressManager, GenerationStage


async def list_available_sessions():
    """列出可用的会话"""
    from app.core.config import settings
    import glob
    
    progress_dir = Path(settings.NOVEL_OUTPUT_DIR)
    progress_files = glob.glob(str(progress_dir / "progress_*.json"))
    
    if not progress_files:
        print("❌ 没有找到可恢复的会话")
        return []
    
    sessions = []
    for file_path in progress_files:
        try:
            manager = ProgressManager()
            manager.progress_file = Path(file_path)
            manager.progress_data = manager._load_progress()
            
            if manager.can_resume():
                sessions.append({
                    'session_id': manager.session_id,
                    'progress': manager.get_progress_percentage(),
                    'current_stage': manager.get_current_stage(),
                    'core_concept': manager.progress_data.get('core_concept', '未知'),
                    'file_path': file_path
                })
        except Exception as e:
            print(f"⚠️ 无法读取会话文件 {file_path}: {e}")
    
    return sessions


async def resume_generation(session_id: str = None, auto_optimize: bool = True):
    """恢复生成"""
    if session_id:
        generator = AutoGenerator(session_id)
    else:
        # 列出可用会话
        sessions = await list_available_sessions()
        if not sessions:
            print("❌ 没有可恢复的会话")
            return
        
        print("📋 可恢复的会话:")
        for i, session in enumerate(sessions):
            print(f"  {i+1}. {session['session_id']} - {session['core_concept']}")
            print(f"     进度: {session['progress']:.1f}% - {session['current_stage']}")
        
        # 选择会话
        try:
            choice = int(input("\n请选择要恢复的会话 (输入数字): ")) - 1
            if 0 <= choice < len(sessions):
                selected_session = sessions[choice]
                generator = AutoGenerator(selected_session['session_id'])
            else:
                print("❌ 无效选择")
                return
        except (ValueError, KeyboardInterrupt):
            print("❌ 取消操作")
            return
    
    # 显示当前进度
    progress_info = generator.get_progress_info()
    print(f"\n📊 会话信息:")
    print(f"  - 会话ID: {progress_info['session_id']}")
    print(f"  - 核心概念: {progress_info['core_concept']}")
    print(f"  - 当前进度: {progress_info['progress_percentage']:.1f}%")
    print(f"  - 当前阶段: {progress_info['current_stage']}")
    print(f"  - 已完成阶段: {', '.join(progress_info['completed_stages'])}")
    
    if progress_info['errors']:
        print(f"\n⚠️ 之前的错误:")
        for error in progress_info['errors'][-3:]:  # 只显示最近3个错误
            print(f"  - {error['stage']}: {error['error']}")
    
    # 确认恢复
    try:
        confirm = input(f"\n是否继续生成? (y/N): ").lower()
        if confirm != 'y':
            print("❌ 取消恢复")
            return
    except KeyboardInterrupt:
        print("❌ 取消恢复")
        return
    
    # 开始恢复生成
    try:
        result = await generator.generate_novel(
            core_concept=progress_info['core_concept'],
            auto_optimize=auto_optimize,
            resume=True
        )
        
        print("\n✅ 生成完成!")
        print(f"📊 生成结果摘要:")
        print(f"  - 世界观: {result.get('world_view', {}).get('name', '未知')}")
        print(f"  - 角色数量: {len(result.get('characters', []))}")
        print(f"  - 反派数量: {len(result.get('main_antagonists', [])) + len(result.get('secondary_antagonists', []))}")
        print(f"  - 剧情段落: {len(result.get('plot_outline', {}).get('plot_segments', []))}")
        print(f"  - 章节数量: {len(result.get('chapters', []))}")
        
        # 清理进度文件
        generator.cleanup_progress()
        
    except Exception as e:
        print(f"❌ 恢复生成失败: {e}")
        import traceback
        traceback.print_exc()


async def start_new_generation():
    """开始新的生成"""
    try:
        core_concept = input("请输入核心概念: ").strip()
        if not core_concept:
            print("❌ 核心概念不能为空")
            return
        
        auto_optimize = input("是否启用自动优化? (Y/n): ").lower() != 'n'
        
        generator = AutoGenerator()
        result = await generator.generate_novel(
            core_concept=core_concept,
            auto_optimize=auto_optimize,
            resume=False
        )
        
        print("\n✅ 生成完成!")
        print(f"📊 生成结果摘要:")
        print(f"  - 世界观: {result.get('world_view', {}).get('name', '未知')}")
        print(f"  - 角色数量: {len(result.get('characters', []))}")
        print(f"  - 反派数量: {len(result.get('main_antagonists', [])) + len(result.get('secondary_antagonists', []))}")
        print(f"  - 剧情段落: {len(result.get('plot_outline', {}).get('plot_segments', []))}")
        print(f"  - 章节数量: {len(result.get('chapters', []))}")
        
    except KeyboardInterrupt:
        print("\n❌ 生成被中断，可以使用断点续传功能恢复")
    except Exception as e:
        print(f"❌ 生成失败: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """主函数"""
    print("🚀 小说生成系统 - 断点续传版")
    print("=" * 50)
    
    try:
        choice = input("请选择操作:\n1. 开始新的生成\n2. 恢复之前的生成\n3. 查看可用会话\n请输入选择 (1-3): ").strip()
        
        if choice == '1':
            await start_new_generation()
        elif choice == '2':
            await resume_generation()
        elif choice == '3':
            sessions = await list_available_sessions()
            if sessions:
                print("\n📋 可恢复的会话:")
                for i, session in enumerate(sessions):
                    print(f"  {i+1}. {session['session_id']} - {session['core_concept']}")
                    print(f"     进度: {session['progress']:.1f}% - {session['current_stage']}")
            else:
                print("❌ 没有可恢复的会话")
        else:
            print("❌ 无效选择")
            
    except KeyboardInterrupt:
        print("\n❌ 操作被中断")
    except Exception as e:
        print(f"❌ 程序错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
