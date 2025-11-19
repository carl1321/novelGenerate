"""
Markdown文件生成器 - 用于生成剧情大纲等内容的MD文件
"""
import os
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path


class MarkdownGenerator:
    """Markdown文件生成器"""
    
    def __init__(self, output_dir: str = "novel"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def generate_plot_outline_md(self, plot_outline: Dict[str, Any]) -> str:
        """生成剧情大纲的Markdown文件"""
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"剧情大纲_{plot_outline.get('title', '未命名')}_{timestamp}.md"
        filepath = self.output_dir / filename
        
        # 生成Markdown内容
        content = self._build_plot_outline_content(plot_outline)
        
        # 写入文件
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return str(filepath)
    
    def _build_plot_outline_content(self, plot_outline: Dict[str, Any]) -> str:
        """构建剧情大纲的Markdown内容"""
        content = []
        
        # 标题和基本信息
        content.append(f"# {plot_outline.get('title', '未命名剧情大纲')}")
        content.append("")
        content.append(f"**创建时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        content.append(f"**世界观ID**: {plot_outline.get('worldview_id', '未知')}")
        content.append(f"**状态**: {plot_outline.get('status', '草稿')}")
        content.append("")
        
        # 剧情大纲要求
        content.append("## 📋 剧情大纲要求")
        content.append("")
        content.append(f"- **故事基调**: {plot_outline.get('story_tone', '未知')}")
        content.append(f"- **叙事结构**: {plot_outline.get('narrative_structure', '未知')}")
        content.append(f"- **故事结构**: {plot_outline.get('story_structure', '未知')}")
        content.append(f"- **目标字数**: {plot_outline.get('target_word_count', 0):,}字")
        content.append(f"- **预计章节数**: {plot_outline.get('estimated_chapters', 0)}章")
        content.append("")
        
        # 故事简介
        if plot_outline.get('description'):
            content.append("## 📖 故事简介")
            content.append("")
            content.append(plot_outline.get('description', ''))
            content.append("")
        
        # 故事框架
        story_framework = plot_outline.get('story_framework', {})
        if story_framework:
            content.append("## 🏗️ 故事框架")
            content.append("")
            content.append(f"**结构类型**: {story_framework.get('structure_type', '未知')}")
            content.append(f"**叙事风格**: {story_framework.get('narrative_style', '未知')}")
            content.append(f"**高潮位置**: {story_framework.get('climax_position', 0):.1%}")
            content.append(f"**结局位置**: {story_framework.get('resolution_position', 0):.1%}")
            content.append("")
            
            # 幕次结构
            acts = story_framework.get('acts', [])
            if acts:
                content.append("### 幕次结构")
                content.append("")
                for act in acts:
                    content.append(f"#### 第{act.get('act_number', 0)}幕: {act.get('act_name', '未知')}")
                    content.append(f"- **位置**: {act.get('start_position', 0):.1%} - {act.get('end_position', 0):.1%}")
                    content.append(f"- **目的**: {act.get('purpose', '未知')}")
                    content.append(f"- **情感基调**: {act.get('emotional_tone', '未知')}")
                    content.append(f"- **预计章节**: {act.get('estimated_chapters', 0)}章")
                    content.append(f"- **预计字数**: {act.get('estimated_words', 0):,}字")
                    content.append("")
                    
                    # 关键事件
                    key_events = act.get('key_events', [])
                    if key_events:
                        content.append("**关键事件**:")
                        for event in key_events:
                            content.append(f"- {event}")
                        content.append("")
                    
                    # 世界观元素
                    worldview_elements = act.get('worldview_elements', [])
                    if worldview_elements:
                        content.append("**世界观元素**:")
                        for element in worldview_elements:
                            content.append(f"- {element}")
                        content.append("")
            
            # 转折点
            turning_points = story_framework.get('turning_points', [])
            if turning_points:
                content.append("### 转折点")
                content.append("")
                for point in turning_points:
                    content.append(f"#### {point.get('title', '未知转折点')}")
                    content.append(f"- **类型**: {point.get('point_type', '未知')}")
                    content.append(f"- **位置**: {point.get('position', 0):.1%}")
                    content.append(f"- **描述**: {point.get('description', '未知')}")
                    content.append(f"- **影响**: {point.get('impact', '未知')}")
                    content.append(f"- **世界观联系**: {point.get('worldview_connection', '未知')}")
                    content.append("")
        
        # 角色定位
        character_positions = plot_outline.get('character_positions', {})
        if character_positions:
            content.append("## 👥 角色定位")
            content.append("")
            for char_name, position in character_positions.items():
                content.append(f"### {char_name}")
                content.append(f"- **基本位置**: {position.get('position', '未知')}")
                content.append(f"- **基本功能**: {position.get('function', '未知')}")
                content.append(f"- **发展轨迹**: {position.get('development_arc', '未知')}")
                content.append(f"- **世界观联系**: {position.get('worldview_connection', '未知')}")
                content.append("")
                
                # 关键时刻
                key_moments = position.get('key_moments', [])
                if key_moments:
                    content.append("**关键时刻**:")
                    for moment in key_moments:
                        content.append(f"- {moment}")
                    content.append("")
        
        
        # 核心剧情块
        plot_blocks = plot_outline.get('plot_blocks', [])
        if plot_blocks:
            content.append("## 📚 核心剧情块")
            content.append("")
            for i, block in enumerate(plot_blocks, 1):
                content.append(f"### {i}. {block.get('plot_name', '未知剧情块')}")
                content.append(f"**描述**: {block.get('description', '未知')}")
                content.append(f"**情感基调**: {block.get('emotional_tone', '未知')}")
                content.append(f"**故事功能**: {block.get('plot_function', '未知')}")
                content.append(f"**预计章节**: {block.get('estimated_chapters', 0)}章")
                content.append(f"**预计字数**: {block.get('estimated_words', 0):,}字")
                content.append("")
                
                # 参与角色
                participating_characters = block.get('participating_characters', [])
                if participating_characters:
                    content.append("**参与角色**:")
                    for char in participating_characters:
                        content.append(f"- {char}")
                    content.append("")
                
                # 世界观元素
                worldview_elements = block.get('worldview_elements', [])
                if worldview_elements:
                    content.append("**世界观元素**:")
                    for element in worldview_elements:
                        content.append(f"- {element}")
                    content.append("")
                
                # 关键事件
                key_events = block.get('key_events', [])
                if key_events:
                    content.append("**关键事件**:")
                    for event in key_events:
                        content.append(f"- {event}")
                    content.append("")
                
                # 伏笔设置
                foreshadowing = block.get('foreshadowing', [])
                if foreshadowing:
                    content.append("**伏笔设置**:")
                    for foreshadow in foreshadowing:
                        content.append(f"- {foreshadow}")
                    content.append("")
        
        # 故事脉络
        story_flow = plot_outline.get('story_flow', {})
        if story_flow:
            content.append("## 🌊 故事脉络")
            content.append("")
            content.append(f"**整体走向**: {story_flow.get('overall_direction', '未知')}")
            content.append(f"**主题发展**: {story_flow.get('thematic_progression', '未知')}")
            content.append(f"**世界观演变**: {story_flow.get('worldview_evolution', '未知')}")
            content.append(f"**冲突发展**: {story_flow.get('conflict_progression', '未知')}")
            content.append(f"**情感发展**: {story_flow.get('emotional_journey', '未知')}")
            content.append("")
            
            # 角色发展脉络
            character_arcs = story_flow.get('character_arcs', {})
            if character_arcs:
                content.append("### 角色发展脉络")
                content.append("")
                for char_name, arc in character_arcs.items():
                    content.append(f"- **{char_name}**: {arc}")
                content.append("")
        
        
        # 结尾
        content.append("---")
        content.append("")
        content.append("*此剧情大纲由AI生成，仅供参考*")
        
        return "\n".join(content)
