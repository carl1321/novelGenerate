"""
文件输出工具
"""
import os
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path

from app.core.config import settings


class FileWriter:
    """文件输出工具类"""
    
    def __init__(self):
        # 获取项目根目录（backend的上级目录）
        current_dir = Path(__file__).parent  # backend/app/utils
        backend_dir = current_dir.parent.parent  # backend
        project_root = backend_dir.parent  # project_root
        self.output_dir = project_root / settings.NOVEL_OUTPUT_DIR
        self.output_dir.mkdir(exist_ok=True)
    
    def write_world_view(self, world_view: Dict[str, Any], filename: Optional[str] = None) -> str:
        """写入世界观设计文档"""
        if not filename:
            # 优先使用世界观ID，如果没有则使用时间戳
            worldview_id = world_view.get('id') or world_view.get('worldview_id')
            if worldview_id:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"世界观设计_{worldview_id}_{timestamp}.md"
            else:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"世界观设计_{timestamp}.md"
        
        file_path = self.output_dir / filename
        
        content = self._format_world_view(world_view)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return str(file_path)
    
    def write_character_profile(self, character: Dict[str, Any], filename: Optional[str] = None) -> str:
        """写入角色档案文档"""
        if not filename:
            character_name = character.get('name', '未命名角色')
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"角色档案_{character_name}_{timestamp}.md"
        
        file_path = self.output_dir / filename
        
        content = self._format_character_profile(character)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return str(file_path)
    
    def write_plot_outline(self, plot: Dict[str, Any], filename: Optional[str] = None) -> str:
        """写入剧情大纲文档"""
        if not filename:
            plot_title = plot.get('title', '未命名剧情')
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"剧情大纲_{plot_title}_{timestamp}.md"
        
        file_path = self.output_dir / filename
        
        content = self._format_plot_outline(plot)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return str(file_path)
    
    def write_analysis_report(self, report_data: Dict[str, Any], filename: Optional[str] = None) -> str:
        """写入分析报告文档"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"分析报告_{timestamp}.md"
        
        file_path = self.output_dir / filename
        
        content = self._format_analysis_report(report_data)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return str(file_path)
    
    def write_novel_chapter(self, chapter: Dict[str, Any], filename: Optional[str] = None) -> str:
        """写入小说章节文档"""
        if not filename:
            chapter_title = chapter.get('title', '未命名章节')
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"章节_{chapter_title}_{timestamp}.md"
        
        file_path = self.output_dir / filename
        
        content = self._format_novel_chapter(chapter)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return str(file_path)
    
    def write_events_sequence(self, events: List[Any], filename: Optional[str] = None) -> str:
        """写入事件序列文档"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"事件序列_{timestamp}.md"
        
        file_path = self.output_dir / filename
        
        content = self._format_events_sequence(events)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return str(file_path)
    
    def write_detailed_plot(self, detailed_plot: Dict[str, Any], filename: Optional[str] = None) -> str:
        """写入详细剧情文档"""
        if not filename:
            plot_title = detailed_plot.get('title', '未命名详细剧情')
            plot_id = detailed_plot.get('id', '')
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"详细剧情_{plot_title}_{plot_id}_{timestamp}.md"
        
        file_path = self.output_dir / filename
        
        content = self._format_detailed_plot(detailed_plot)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return str(file_path)
    
    def write_analysis_report(self, report: Dict[str, Any], filename: Optional[str] = None) -> str:
        
        file_path = self.output_dir / filename
        
        content = self._format_analysis_report(report)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return str(file_path)
    
    def _format_world_view(self, world_view: Dict[str, Any]) -> str:
        """格式化世界观设计文档"""
        content = f"""# {world_view.get('name', '世界观设计')}

## 基本信息

- **创建时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 世界观描述

{world_view.get('description', '暂无描述')}

## 力量体系

{self._format_power_system(world_view.get('power_system', {}))}

## 地理设定

{self._format_geography(world_view.get('geography', {}))}

## 社会组织

{self._format_society(world_view.get('culture', {}))}

## 历史文化

{self._format_history_culture(world_view.get('history', {}))}

---
*本文档由小说生成智能体框架自动生成*
"""
        return content
    
    def _format_analysis_report(self, report_data: Dict[str, Any]) -> str:
        """格式化分析报告为Markdown"""
        content = []
        
        # 标题
        content.append("# 小说生成分析报告")
        content.append("")
        
        # 生成信息
        generation_info = report_data.get('generation_info', {})
        if generation_info:
            content.append("## 生成信息")
            content.append("")
            content.append(f"- **核心概念**: {generation_info.get('core_concept', '未知')}")
            content.append(f"- **世界观名称**: {generation_info.get('world_name', '未知')}")
            content.append(f"- **剧情标题**: {generation_info.get('plot_title', '未知')}")
            content.append(f"- **角色数量**: {generation_info.get('total_characters', 0)}")
            content.append(f"- **生成时间**: {generation_info.get('generation_time', '未知')}")
            content.append("")
        
        # 评分信息
        scores = report_data.get('scores', {})
        if scores:
            content.append("## 内容评分")
            content.append("")
            content.append(f"**总分**: {scores.get('total_score', 0):.1f}/10")
            content.append("")
            
            dimension_scores = scores.get('scores', {})
            if dimension_scores:
                content.append("### 各维度评分")
                content.append("")
                for dimension, score in dimension_scores.items():
                    content.append(f"- **{dimension}**: {score:.1f}/10")
                content.append("")
        
        # 逻辑检查
        logic_check = report_data.get('logic_check', {})
        if logic_check:
            content.append("## 逻辑检查")
            content.append("")
            content.append(f"**状态**: {logic_check.get('status', '未知')}")
            content.append("")
            
            analysis = logic_check.get('analysis', '')
            if analysis:
                content.append("### 检查结果")
                content.append("")
                content.append(analysis)
                content.append("")
        
        # 反思报告
        report = report_data.get('report', {})
        if report:
            content.append("## 反思报告")
            content.append("")
            
            report_content = report.get('content', '')
            if report_content:
                content.append(report_content)
                content.append("")
        
        return "\n".join(content)
    
    def _format_detailed_plot(self, detailed_plot: Dict[str, Any]) -> str:
        """格式化详细剧情文档"""
        content = f"""# {detailed_plot.get('title', '未命名详细剧情')}

## 基本信息

- **详细剧情ID**: {detailed_plot.get('id', '未知')}
- **章节大纲ID**: {detailed_plot.get('chapter_outline_id', '未知')}
- **剧情大纲ID**: {detailed_plot.get('plot_outline_id', '未知')}
- **字数**: {detailed_plot.get('word_count', 0)} 字
- **状态**: {detailed_plot.get('status', '未知')}
- **创建时间**: {detailed_plot.get('created_at', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}
- **更新时间**: {detailed_plot.get('updated_at', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}

## 详细剧情内容

{detailed_plot.get('content', '暂无内容')}

## 逻辑检查结果

- **逻辑状态**: {detailed_plot.get('logic_status', '未检查')}
- **逻辑分数**: {detailed_plot.get('logic_score', 'N/A')}
- **检查结果**: {detailed_plot.get('logic_check_result', '暂无检查结果')}

## 评分信息

- **评分状态**: {detailed_plot.get('scoring_status', '未评分')}
- **总分**: {detailed_plot.get('total_score', 'N/A')}

---
*本文档由小说生成智能体框架自动生成*
"""
        return content
    
    def _format_character_profile(self, character: Dict[str, Any]) -> str:
        """格式化角色档案文档 - 使用简化的5个维度结构"""
        # 从metadata中获取简化的信息
        metadata = character.get('metadata', {})
        
        content = f"""# {character.get('name', '未命名角色')} - 角色档案

## 1. 基础信息

- **姓名**: {character.get('name', '未命名')}
- **年龄**: {character.get('age', '未知')}岁
- **性别**: {character.get('gender', '未知')}
- **外貌**: {metadata.get('appearance', '暂无描述')}

## 2. 内在特质

- **性格**: {', '.join(metadata.get('personality', [])) if metadata.get('personality') else '暂无设定'}
- **价值观**: {metadata.get('values', '暂无设定')}
- **恐惧**: {metadata.get('fears', '暂无设定')}
- **欲望**: {metadata.get('desires', '暂无设定')}

## 3. 能力设定

- **技能**: {', '.join(metadata.get('skills', [])) if metadata.get('skills') else '暂无设定'}
- **弱点**: {', '.join(metadata.get('weaknesses', [])) if metadata.get('weaknesses') else '暂无设定'}
- **成长潜力**: {metadata.get('growth_potential', '暂无设定')}

## 4. 社会关系

- **家族**: {metadata.get('family', '暂无设定')}
- **师门**: {character.get('organization_id', '暂无设定')}
- **朋友**: {', '.join(metadata.get('friends', [])) if metadata.get('friends') else '暂无设定'}
- **敌人**: {', '.join(metadata.get('enemies', [])) if metadata.get('enemies') else '暂无设定'}

## 5. 成长弧线

- **初始状态**: {metadata.get('initial_state', '暂无设定')}
- **转折点**: {metadata.get('turning_point', '暂无设定')}
- **最终目标**: {metadata.get('final_goal', '暂无设定')}

---
*本文档由小说生成智能体框架自动生成*
"""
        return content
    
    def _format_analysis_report(self, report_data: Dict[str, Any]) -> str:
        """格式化分析报告为Markdown"""
        content = []
        
        # 标题
        content.append("# 小说生成分析报告")
        content.append("")
        
        # 生成信息
        generation_info = report_data.get('generation_info', {})
        if generation_info:
            content.append("## 生成信息")
            content.append("")
            content.append(f"- **核心概念**: {generation_info.get('core_concept', '未知')}")
            content.append(f"- **世界观名称**: {generation_info.get('world_name', '未知')}")
            content.append(f"- **剧情标题**: {generation_info.get('plot_title', '未知')}")
            content.append(f"- **角色数量**: {generation_info.get('total_characters', 0)}")
            content.append(f"- **生成时间**: {generation_info.get('generation_time', '未知')}")
            content.append("")
        
        # 评分信息
        scores = report_data.get('scores', {})
        if scores:
            content.append("## 内容评分")
            content.append("")
            content.append(f"**总分**: {scores.get('total_score', 0):.1f}/10")
            content.append("")
            
            dimension_scores = scores.get('scores', {})
            if dimension_scores:
                content.append("### 各维度评分")
                content.append("")
                for dimension, score in dimension_scores.items():
                    content.append(f"- **{dimension}**: {score:.1f}/10")
                content.append("")
        
        # 逻辑检查
        logic_check = report_data.get('logic_check', {})
        if logic_check:
            content.append("## 逻辑检查")
            content.append("")
            content.append(f"**状态**: {logic_check.get('status', '未知')}")
            content.append("")
            
            analysis = logic_check.get('analysis', '')
            if analysis:
                content.append("### 检查结果")
                content.append("")
                content.append(analysis)
                content.append("")
        
        # 反思报告
        report = report_data.get('report', {})
        if report:
            content.append("## 反思报告")
            content.append("")
            
            report_content = report.get('content', '')
            if report_content:
                content.append(report_content)
                content.append("")
        
        return "\n".join(content)
    
    def _format_plot_outline(self, plot: Dict[str, Any]) -> str:
        """格式化剧情大纲文档"""
        content = f"""# {plot.get('title', '剧情大纲')}

## 基本信息

- **创建时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **目标长度**: {plot.get('target_length', '未知')}章节
- **当前进度**: {plot.get('current_progress', 0)}%

## 剧情描述

{plot.get('description', '暂无描述')}

## 主要主题

{self._format_list(plot.get('themes', []))}

## 剧情弧线

{self._format_plot_arcs(plot.get('plot_arcs', []))}

## 伏笔设计

{self._format_foreshadowing(plot.get('foreshadowing', []))}

## 主要角色

{self._format_list(plot.get('main_characters', []))}

## 主要冲突

{self._format_list(plot.get('main_conflicts', []))}

---
*本文档由小说生成智能体框架自动生成*
"""
        return content
    
    def _format_analysis_report(self, report_data: Dict[str, Any]) -> str:
        """格式化分析报告为Markdown"""
        content = []
        
        # 标题
        content.append("# 小说生成分析报告")
        content.append("")
        
        # 生成信息
        generation_info = report_data.get('generation_info', {})
        if generation_info:
            content.append("## 生成信息")
            content.append("")
            content.append(f"- **核心概念**: {generation_info.get('core_concept', '未知')}")
            content.append(f"- **世界观名称**: {generation_info.get('world_name', '未知')}")
            content.append(f"- **剧情标题**: {generation_info.get('plot_title', '未知')}")
            content.append(f"- **角色数量**: {generation_info.get('total_characters', 0)}")
            content.append(f"- **生成时间**: {generation_info.get('generation_time', '未知')}")
            content.append("")
        
        # 评分信息
        scores = report_data.get('scores', {})
        if scores:
            content.append("## 内容评分")
            content.append("")
            content.append(f"**总分**: {scores.get('total_score', 0):.1f}/10")
            content.append("")
            
            dimension_scores = scores.get('scores', {})
            if dimension_scores:
                content.append("### 各维度评分")
                content.append("")
                for dimension, score in dimension_scores.items():
                    content.append(f"- **{dimension}**: {score:.1f}/10")
                content.append("")
        
        # 逻辑检查
        logic_check = report_data.get('logic_check', {})
        if logic_check:
            content.append("## 逻辑检查")
            content.append("")
            content.append(f"**状态**: {logic_check.get('status', '未知')}")
            content.append("")
            
            analysis = logic_check.get('analysis', '')
            if analysis:
                content.append("### 检查结果")
                content.append("")
                content.append(analysis)
                content.append("")
        
        # 反思报告
        report = report_data.get('report', {})
        if report:
            content.append("## 反思报告")
            content.append("")
            
            report_content = report.get('content', '')
            if report_content:
                content.append(report_content)
                content.append("")
        
        return "\n".join(content)
    
    def _format_novel_chapter(self, chapter: Dict[str, Any]) -> str:
        """格式化小说章节文档"""
        content = f"""# {chapter.get('title', '未命名章节')}

## 章节信息

- **章节编号**: {chapter.get('chapter_number', '未知')}
- **字数**: {chapter.get('word_count', 0)}字
- **创作时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 章节内容

{chapter.get('content', '暂无内容')}

## 出场角色

{self._format_list(chapter.get('characters', []))}

## 发生地点

{chapter.get('location', '未知地点')}

## 关键事件

{self._format_list(chapter.get('key_events', []))}

## 伏笔回收

{self._format_list(chapter.get('foreshadowing_payoff', []))}

---
*本文档由小说生成智能体框架自动生成*
"""
        return content
    
    def _format_analysis_report(self, report_data: Dict[str, Any]) -> str:
        """格式化分析报告为Markdown"""
        content = []
        
        # 标题
        content.append("# 小说生成分析报告")
        content.append("")
        
        # 生成信息
        generation_info = report_data.get('generation_info', {})
        if generation_info:
            content.append("## 生成信息")
            content.append("")
            content.append(f"- **核心概念**: {generation_info.get('core_concept', '未知')}")
            content.append(f"- **世界观名称**: {generation_info.get('world_name', '未知')}")
            content.append(f"- **剧情标题**: {generation_info.get('plot_title', '未知')}")
            content.append(f"- **角色数量**: {generation_info.get('total_characters', 0)}")
            content.append(f"- **生成时间**: {generation_info.get('generation_time', '未知')}")
            content.append("")
        
        # 评分信息
        scores = report_data.get('scores', {})
        if scores:
            content.append("## 内容评分")
            content.append("")
            content.append(f"**总分**: {scores.get('total_score', 0):.1f}/10")
            content.append("")
            
            dimension_scores = scores.get('scores', {})
            if dimension_scores:
                content.append("### 各维度评分")
                content.append("")
                for dimension, score in dimension_scores.items():
                    content.append(f"- **{dimension}**: {score:.1f}/10")
                content.append("")
        
        # 逻辑检查
        logic_check = report_data.get('logic_check', {})
        if logic_check:
            content.append("## 逻辑检查")
            content.append("")
            content.append(f"**状态**: {logic_check.get('status', '未知')}")
            content.append("")
            
            analysis = logic_check.get('analysis', '')
            if analysis:
                content.append("### 检查结果")
                content.append("")
                content.append(analysis)
                content.append("")
        
        # 反思报告
        report = report_data.get('report', {})
        if report:
            content.append("## 反思报告")
            content.append("")
            
            report_content = report.get('content', '')
            if report_content:
                content.append(report_content)
                content.append("")
        
        return "\n".join(content)
    
    def _format_analysis_report(self, report: Dict[str, Any]) -> str:
        """格式化分析报告文档"""
        content = f"""# {report.get('title', '分析报告')}

## 报告信息

- **报告类型**: {report.get('type', '未知')}
- **生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **分析对象**: {report.get('target', '未知')}

## 分析结果

{report.get('analysis', '暂无分析结果')}

## 问题列表

{self._format_list(report.get('issues', []))}

## 改进建议

{self._format_list(report.get('suggestions', []))}

## 评分详情

{self._format_scores(report.get('scores', {}))}

---
*本文档由小说生成智能体框架自动生成*
"""
        return content
    
    def _format_analysis_report(self, report_data: Dict[str, Any]) -> str:
        """格式化分析报告为Markdown"""
        content = []
        
        # 标题
        content.append("# 小说生成分析报告")
        content.append("")
        
        # 生成信息
        generation_info = report_data.get('generation_info', {})
        if generation_info:
            content.append("## 生成信息")
            content.append("")
            content.append(f"- **核心概念**: {generation_info.get('core_concept', '未知')}")
            content.append(f"- **世界观名称**: {generation_info.get('world_name', '未知')}")
            content.append(f"- **剧情标题**: {generation_info.get('plot_title', '未知')}")
            content.append(f"- **角色数量**: {generation_info.get('total_characters', 0)}")
            content.append(f"- **生成时间**: {generation_info.get('generation_time', '未知')}")
            content.append("")
        
        # 评分信息
        scores = report_data.get('scores', {})
        if scores:
            content.append("## 内容评分")
            content.append("")
            content.append(f"**总分**: {scores.get('total_score', 0):.1f}/10")
            content.append("")
            
            dimension_scores = scores.get('scores', {})
            if dimension_scores:
                content.append("### 各维度评分")
                content.append("")
                for dimension, score in dimension_scores.items():
                    content.append(f"- **{dimension}**: {score:.1f}/10")
                content.append("")
        
        # 逻辑检查
        logic_check = report_data.get('logic_check', {})
        if logic_check:
            content.append("## 逻辑检查")
            content.append("")
            content.append(f"**状态**: {logic_check.get('status', '未知')}")
            content.append("")
            
            analysis = logic_check.get('analysis', '')
            if analysis:
                content.append("### 检查结果")
                content.append("")
                content.append(analysis)
                content.append("")
        
        # 反思报告
        report = report_data.get('report', {})
        if report:
            content.append("## 反思报告")
            content.append("")
            
            report_content = report.get('content', '')
            if report_content:
                content.append(report_content)
                content.append("")
        
        return "\n".join(content)
    
    def _format_rules(self, rules: list) -> str:
        """格式化规则列表"""
        if not rules:
            return "暂无规则设定"
        
        content = ""
        for rule in rules:
            content += f"- **{rule.get('name', '未命名规则')}**: {rule.get('content', '无描述')}\n"
        
        return content
    
    def _format_analysis_report(self, report_data: Dict[str, Any]) -> str:
        """格式化分析报告为Markdown"""
        content = []
        
        # 标题
        content.append("# 小说生成分析报告")
        content.append("")
        
        # 生成信息
        generation_info = report_data.get('generation_info', {})
        if generation_info:
            content.append("## 生成信息")
            content.append("")
            content.append(f"- **核心概念**: {generation_info.get('core_concept', '未知')}")
            content.append(f"- **世界观名称**: {generation_info.get('world_name', '未知')}")
            content.append(f"- **剧情标题**: {generation_info.get('plot_title', '未知')}")
            content.append(f"- **角色数量**: {generation_info.get('total_characters', 0)}")
            content.append(f"- **生成时间**: {generation_info.get('generation_time', '未知')}")
            content.append("")
        
        # 评分信息
        scores = report_data.get('scores', {})
        if scores:
            content.append("## 内容评分")
            content.append("")
            content.append(f"**总分**: {scores.get('total_score', 0):.1f}/10")
            content.append("")
            
            dimension_scores = scores.get('scores', {})
            if dimension_scores:
                content.append("### 各维度评分")
                content.append("")
                for dimension, score in dimension_scores.items():
                    content.append(f"- **{dimension}**: {score:.1f}/10")
                content.append("")
        
        # 逻辑检查
        logic_check = report_data.get('logic_check', {})
        if logic_check:
            content.append("## 逻辑检查")
            content.append("")
            content.append(f"**状态**: {logic_check.get('status', '未知')}")
            content.append("")
            
            analysis = logic_check.get('analysis', '')
            if analysis:
                content.append("### 检查结果")
                content.append("")
                content.append(analysis)
                content.append("")
        
        # 反思报告
        report = report_data.get('report', {})
        if report:
            content.append("## 反思报告")
            content.append("")
            
            report_content = report.get('content', '')
            if report_content:
                content.append(report_content)
                content.append("")
        
        return "\n".join(content)
    
    def _format_locations(self, locations: list) -> str:
        """格式化地点列表"""
        if not locations:
            return "暂无地点设定"
        
        content = ""
        for location in locations:
            content += f"### {location.get('name', '未命名地点')}\n"
            content += f"- **类型**: {location.get('location_type', '未知')}\n"
            content += f"- **描述**: {location.get('description', '无描述')}\n"
            if location.get('resources'):
                content += f"- **资源**: {', '.join(location['resources'])}\n"
            content += "\n"
        
        return content
    
    def _format_analysis_report(self, report_data: Dict[str, Any]) -> str:
        """格式化分析报告为Markdown"""
        content = []
        
        # 标题
        content.append("# 小说生成分析报告")
        content.append("")
        
        # 生成信息
        generation_info = report_data.get('generation_info', {})
        if generation_info:
            content.append("## 生成信息")
            content.append("")
            content.append(f"- **核心概念**: {generation_info.get('core_concept', '未知')}")
            content.append(f"- **世界观名称**: {generation_info.get('world_name', '未知')}")
            content.append(f"- **剧情标题**: {generation_info.get('plot_title', '未知')}")
            content.append(f"- **角色数量**: {generation_info.get('total_characters', 0)}")
            content.append(f"- **生成时间**: {generation_info.get('generation_time', '未知')}")
            content.append("")
        
        # 评分信息
        scores = report_data.get('scores', {})
        if scores:
            content.append("## 内容评分")
            content.append("")
            content.append(f"**总分**: {scores.get('total_score', 0):.1f}/10")
            content.append("")
            
            dimension_scores = scores.get('scores', {})
            if dimension_scores:
                content.append("### 各维度评分")
                content.append("")
                for dimension, score in dimension_scores.items():
                    content.append(f"- **{dimension}**: {score:.1f}/10")
                content.append("")
        
        # 逻辑检查
        logic_check = report_data.get('logic_check', {})
        if logic_check:
            content.append("## 逻辑检查")
            content.append("")
            content.append(f"**状态**: {logic_check.get('status', '未知')}")
            content.append("")
            
            analysis = logic_check.get('analysis', '')
            if analysis:
                content.append("### 检查结果")
                content.append("")
                content.append(analysis)
                content.append("")
        
        # 反思报告
        report = report_data.get('report', {})
        if report:
            content.append("## 反思报告")
            content.append("")
            
            report_content = report.get('content', '')
            if report_content:
                content.append(report_content)
                content.append("")
        
        return "\n".join(content)
    
    def _format_organizations(self, organizations: list) -> str:
        """格式化组织列表"""
        if not organizations:
            return "暂无组织设定"
        
        content = ""
        for org in organizations:
            content += f"### {org.get('name', '未命名组织')}\n"
            content += f"- **类型**: {org.get('org_type', '未知')}\n"
            content += f"- **描述**: {org.get('description', '无描述')}\n"
            content += f"- **实力等级**: {org.get('power_level', '未知')}\n"
            content += "\n"
        
        return content
    
    def _format_analysis_report(self, report_data: Dict[str, Any]) -> str:
        """格式化分析报告为Markdown"""
        content = []
        
        # 标题
        content.append("# 小说生成分析报告")
        content.append("")
        
        # 生成信息
        generation_info = report_data.get('generation_info', {})
        if generation_info:
            content.append("## 生成信息")
            content.append("")
            content.append(f"- **核心概念**: {generation_info.get('core_concept', '未知')}")
            content.append(f"- **世界观名称**: {generation_info.get('world_name', '未知')}")
            content.append(f"- **剧情标题**: {generation_info.get('plot_title', '未知')}")
            content.append(f"- **角色数量**: {generation_info.get('total_characters', 0)}")
            content.append(f"- **生成时间**: {generation_info.get('generation_time', '未知')}")
            content.append("")
        
        # 评分信息
        scores = report_data.get('scores', {})
        if scores:
            content.append("## 内容评分")
            content.append("")
            content.append(f"**总分**: {scores.get('total_score', 0):.1f}/10")
            content.append("")
            
            dimension_scores = scores.get('scores', {})
            if dimension_scores:
                content.append("### 各维度评分")
                content.append("")
                for dimension, score in dimension_scores.items():
                    content.append(f"- **{dimension}**: {score:.1f}/10")
                content.append("")
        
        # 逻辑检查
        logic_check = report_data.get('logic_check', {})
        if logic_check:
            content.append("## 逻辑检查")
            content.append("")
            content.append(f"**状态**: {logic_check.get('status', '未知')}")
            content.append("")
            
            analysis = logic_check.get('analysis', '')
            if analysis:
                content.append("### 检查结果")
                content.append("")
                content.append(analysis)
                content.append("")
        
        # 反思报告
        report = report_data.get('report', {})
        if report:
            content.append("## 反思报告")
            content.append("")
            
            report_content = report.get('content', '')
            if report_content:
                content.append(report_content)
                content.append("")
        
        return "\n".join(content)
    
    def _format_techniques(self, techniques: list) -> str:
        """格式化功法列表"""
        if not techniques:
            return "暂无功法设定"
        
        content = ""
        for tech in techniques:
            content += f"### {tech.get('name', '未命名功法')}\n"
            content += f"- **等级要求**: {tech.get('level_requirement', '未知')}\n"
            content += f"- **属性要求**: {tech.get('element_type', '未知')}\n"
            content += f"- **难度**: {tech.get('difficulty', '未知')}/10\n"
            content += f"- **威力**: {tech.get('power_level', '未知')}/10\n"
            content += f"- **描述**: {tech.get('description', '无描述')}\n"
            content += "\n"
        
        return content
    
    def _format_analysis_report(self, report_data: Dict[str, Any]) -> str:
        """格式化分析报告为Markdown"""
        content = []
        
        # 标题
        content.append("# 小说生成分析报告")
        content.append("")
        
        # 生成信息
        generation_info = report_data.get('generation_info', {})
        if generation_info:
            content.append("## 生成信息")
            content.append("")
            content.append(f"- **核心概念**: {generation_info.get('core_concept', '未知')}")
            content.append(f"- **世界观名称**: {generation_info.get('world_name', '未知')}")
            content.append(f"- **剧情标题**: {generation_info.get('plot_title', '未知')}")
            content.append(f"- **角色数量**: {generation_info.get('total_characters', 0)}")
            content.append(f"- **生成时间**: {generation_info.get('generation_time', '未知')}")
            content.append("")
        
        # 评分信息
        scores = report_data.get('scores', {})
        if scores:
            content.append("## 内容评分")
            content.append("")
            content.append(f"**总分**: {scores.get('total_score', 0):.1f}/10")
            content.append("")
            
            dimension_scores = scores.get('scores', {})
            if dimension_scores:
                content.append("### 各维度评分")
                content.append("")
                for dimension, score in dimension_scores.items():
                    content.append(f"- **{dimension}**: {score:.1f}/10")
                content.append("")
        
        # 逻辑检查
        logic_check = report_data.get('logic_check', {})
        if logic_check:
            content.append("## 逻辑检查")
            content.append("")
            content.append(f"**状态**: {logic_check.get('status', '未知')}")
            content.append("")
            
            analysis = logic_check.get('analysis', '')
            if analysis:
                content.append("### 检查结果")
                content.append("")
                content.append(analysis)
                content.append("")
        
        # 反思报告
        report = report_data.get('report', {})
        if report:
            content.append("## 反思报告")
            content.append("")
            
            report_content = report.get('content', '')
            if report_content:
                content.append(report_content)
                content.append("")
        
        return "\n".join(content)
    
    def _format_artifacts(self, artifacts: list) -> str:
        """格式化法宝列表"""
        if not artifacts:
            return "暂无法宝设定"
        
        content = ""
        for artifact in artifacts:
            content += f"### {artifact.get('name', '未命名法宝')}\n"
            content += f"- **类型**: {artifact.get('artifact_type', '未知')}\n"
            content += f"- **品级**: {artifact.get('grade', '未知')}/10\n"
            content += f"- **威力**: {artifact.get('power_level', '未知')}/10\n"
            content += f"- **描述**: {artifact.get('description', '无描述')}\n"
            content += "\n"
        
        return content
    
    def _format_analysis_report(self, report_data: Dict[str, Any]) -> str:
        """格式化分析报告为Markdown"""
        content = []
        
        # 标题
        content.append("# 小说生成分析报告")
        content.append("")
        
        # 生成信息
        generation_info = report_data.get('generation_info', {})
        if generation_info:
            content.append("## 生成信息")
            content.append("")
            content.append(f"- **核心概念**: {generation_info.get('core_concept', '未知')}")
            content.append(f"- **世界观名称**: {generation_info.get('world_name', '未知')}")
            content.append(f"- **剧情标题**: {generation_info.get('plot_title', '未知')}")
            content.append(f"- **角色数量**: {generation_info.get('total_characters', 0)}")
            content.append(f"- **生成时间**: {generation_info.get('generation_time', '未知')}")
            content.append("")
        
        # 评分信息
        scores = report_data.get('scores', {})
        if scores:
            content.append("## 内容评分")
            content.append("")
            content.append(f"**总分**: {scores.get('total_score', 0):.1f}/10")
            content.append("")
            
            dimension_scores = scores.get('scores', {})
            if dimension_scores:
                content.append("### 各维度评分")
                content.append("")
                for dimension, score in dimension_scores.items():
                    content.append(f"- **{dimension}**: {score:.1f}/10")
                content.append("")
        
        # 逻辑检查
        logic_check = report_data.get('logic_check', {})
        if logic_check:
            content.append("## 逻辑检查")
            content.append("")
            content.append(f"**状态**: {logic_check.get('status', '未知')}")
            content.append("")
            
            analysis = logic_check.get('analysis', '')
            if analysis:
                content.append("### 检查结果")
                content.append("")
                content.append(analysis)
                content.append("")
        
        # 反思报告
        report = report_data.get('report', {})
        if report:
            content.append("## 反思报告")
            content.append("")
            
            report_content = report.get('content', '')
            if report_content:
                content.append(report_content)
                content.append("")
        
        return "\n".join(content)
    
    def _format_personality_traits(self, traits: list) -> str:
        """格式化性格特质"""
        if not traits:
            return "暂无性格设定"
        
        return ", ".join(traits)
    
    def _format_goals(self, goals: list) -> str:
        """格式化目标列表"""
        if not goals:
            return "暂无目标设定"
        
        content = ""
        for goal in goals:
            content += f"- **{goal.get('type', '未知类型')}**: {goal.get('description', '无描述')}\n"
        
        return content
    
    def _format_analysis_report(self, report_data: Dict[str, Any]) -> str:
        """格式化分析报告为Markdown"""
        content = []
        
        # 标题
        content.append("# 小说生成分析报告")
        content.append("")
        
        # 生成信息
        generation_info = report_data.get('generation_info', {})
        if generation_info:
            content.append("## 生成信息")
            content.append("")
            content.append(f"- **核心概念**: {generation_info.get('core_concept', '未知')}")
            content.append(f"- **世界观名称**: {generation_info.get('world_name', '未知')}")
            content.append(f"- **剧情标题**: {generation_info.get('plot_title', '未知')}")
            content.append(f"- **角色数量**: {generation_info.get('total_characters', 0)}")
            content.append(f"- **生成时间**: {generation_info.get('generation_time', '未知')}")
            content.append("")
        
        # 评分信息
        scores = report_data.get('scores', {})
        if scores:
            content.append("## 内容评分")
            content.append("")
            content.append(f"**总分**: {scores.get('total_score', 0):.1f}/10")
            content.append("")
            
            dimension_scores = scores.get('scores', {})
            if dimension_scores:
                content.append("### 各维度评分")
                content.append("")
                for dimension, score in dimension_scores.items():
                    content.append(f"- **{dimension}**: {score:.1f}/10")
                content.append("")
        
        # 逻辑检查
        logic_check = report_data.get('logic_check', {})
        if logic_check:
            content.append("## 逻辑检查")
            content.append("")
            content.append(f"**状态**: {logic_check.get('status', '未知')}")
            content.append("")
            
            analysis = logic_check.get('analysis', '')
            if analysis:
                content.append("### 检查结果")
                content.append("")
                content.append(analysis)
                content.append("")
        
        # 反思报告
        report = report_data.get('report', {})
        if report:
            content.append("## 反思报告")
            content.append("")
            
            report_content = report.get('content', '')
            if report_content:
                content.append(report_content)
                content.append("")
        
        return "\n".join(content)
    
    def _format_relationships(self, relationships: dict) -> str:
        """格式化人际关系"""
        if not relationships:
            return "暂无关系设定"
        
        content = ""
        for char_id, rel_type in relationships.items():
            content += f"- **{char_id}**: {rel_type}\n"
        
        return content
    
    def _format_analysis_report(self, report_data: Dict[str, Any]) -> str:
        """格式化分析报告为Markdown"""
        content = []
        
        # 标题
        content.append("# 小说生成分析报告")
        content.append("")
        
        # 生成信息
        generation_info = report_data.get('generation_info', {})
        if generation_info:
            content.append("## 生成信息")
            content.append("")
            content.append(f"- **核心概念**: {generation_info.get('core_concept', '未知')}")
            content.append(f"- **世界观名称**: {generation_info.get('world_name', '未知')}")
            content.append(f"- **剧情标题**: {generation_info.get('plot_title', '未知')}")
            content.append(f"- **角色数量**: {generation_info.get('total_characters', 0)}")
            content.append(f"- **生成时间**: {generation_info.get('generation_time', '未知')}")
            content.append("")
        
        # 评分信息
        scores = report_data.get('scores', {})
        if scores:
            content.append("## 内容评分")
            content.append("")
            content.append(f"**总分**: {scores.get('total_score', 0):.1f}/10")
            content.append("")
            
            dimension_scores = scores.get('scores', {})
            if dimension_scores:
                content.append("### 各维度评分")
                content.append("")
                for dimension, score in dimension_scores.items():
                    content.append(f"- **{dimension}**: {score:.1f}/10")
                content.append("")
        
        # 逻辑检查
        logic_check = report_data.get('logic_check', {})
        if logic_check:
            content.append("## 逻辑检查")
            content.append("")
            content.append(f"**状态**: {logic_check.get('status', '未知')}")
            content.append("")
            
            analysis = logic_check.get('analysis', '')
            if analysis:
                content.append("### 检查结果")
                content.append("")
                content.append(analysis)
                content.append("")
        
        # 反思报告
        report = report_data.get('report', {})
        if report:
            content.append("## 反思报告")
            content.append("")
            
            report_content = report.get('content', '')
            if report_content:
                content.append(report_content)
                content.append("")
        
        return "\n".join(content)
    
    def _format_resources(self, resources: dict) -> str:
        """格式化资源状况"""
        if not resources:
            return "暂无资源设定"
        
        content = ""
        for resource, amount in resources.items():
            content += f"- **{resource}**: {amount}\n"
        
        return content
    
    def _format_analysis_report(self, report_data: Dict[str, Any]) -> str:
        """格式化分析报告为Markdown"""
        content = []
        
        # 标题
        content.append("# 小说生成分析报告")
        content.append("")
        
        # 生成信息
        generation_info = report_data.get('generation_info', {})
        if generation_info:
            content.append("## 生成信息")
            content.append("")
            content.append(f"- **核心概念**: {generation_info.get('core_concept', '未知')}")
            content.append(f"- **世界观名称**: {generation_info.get('world_name', '未知')}")
            content.append(f"- **剧情标题**: {generation_info.get('plot_title', '未知')}")
            content.append(f"- **角色数量**: {generation_info.get('total_characters', 0)}")
            content.append(f"- **生成时间**: {generation_info.get('generation_time', '未知')}")
            content.append("")
        
        # 评分信息
        scores = report_data.get('scores', {})
        if scores:
            content.append("## 内容评分")
            content.append("")
            content.append(f"**总分**: {scores.get('total_score', 0):.1f}/10")
            content.append("")
            
            dimension_scores = scores.get('scores', {})
            if dimension_scores:
                content.append("### 各维度评分")
                content.append("")
                for dimension, score in dimension_scores.items():
                    content.append(f"- **{dimension}**: {score:.1f}/10")
                content.append("")
        
        # 逻辑检查
        logic_check = report_data.get('logic_check', {})
        if logic_check:
            content.append("## 逻辑检查")
            content.append("")
            content.append(f"**状态**: {logic_check.get('status', '未知')}")
            content.append("")
            
            analysis = logic_check.get('analysis', '')
            if analysis:
                content.append("### 检查结果")
                content.append("")
                content.append(analysis)
                content.append("")
        
        # 反思报告
        report = report_data.get('report', {})
        if report:
            content.append("## 反思报告")
            content.append("")
            
            report_content = report.get('content', '')
            if report_content:
                content.append(report_content)
                content.append("")
        
        return "\n".join(content)
    
    def _format_stats(self, stats: dict) -> str:
        """格式化属性数值"""
        if not stats:
            return "暂无属性设定"
        
        content = ""
        for stat, value in stats.items():
            content += f"- **{stat}**: {value}\n"
        
        return content
    
    def _format_analysis_report(self, report_data: Dict[str, Any]) -> str:
        """格式化分析报告为Markdown"""
        content = []
        
        # 标题
        content.append("# 小说生成分析报告")
        content.append("")
        
        # 生成信息
        generation_info = report_data.get('generation_info', {})
        if generation_info:
            content.append("## 生成信息")
            content.append("")
            content.append(f"- **核心概念**: {generation_info.get('core_concept', '未知')}")
            content.append(f"- **世界观名称**: {generation_info.get('world_name', '未知')}")
            content.append(f"- **剧情标题**: {generation_info.get('plot_title', '未知')}")
            content.append(f"- **角色数量**: {generation_info.get('total_characters', 0)}")
            content.append(f"- **生成时间**: {generation_info.get('generation_time', '未知')}")
            content.append("")
        
        # 评分信息
        scores = report_data.get('scores', {})
        if scores:
            content.append("## 内容评分")
            content.append("")
            content.append(f"**总分**: {scores.get('total_score', 0):.1f}/10")
            content.append("")
            
            dimension_scores = scores.get('scores', {})
            if dimension_scores:
                content.append("### 各维度评分")
                content.append("")
                for dimension, score in dimension_scores.items():
                    content.append(f"- **{dimension}**: {score:.1f}/10")
                content.append("")
        
        # 逻辑检查
        logic_check = report_data.get('logic_check', {})
        if logic_check:
            content.append("## 逻辑检查")
            content.append("")
            content.append(f"**状态**: {logic_check.get('status', '未知')}")
            content.append("")
            
            analysis = logic_check.get('analysis', '')
            if analysis:
                content.append("### 检查结果")
                content.append("")
                content.append(analysis)
                content.append("")
        
        # 反思报告
        report = report_data.get('report', {})
        if report:
            content.append("## 反思报告")
            content.append("")
            
            report_content = report.get('content', '')
            if report_content:
                content.append(report_content)
                content.append("")
        
        return "\n".join(content)
    
    def _format_growth_trajectory(self, trajectory: list) -> str:
        """格式化成长轨迹"""
        if not trajectory:
            return "暂无成长轨迹"
        
        content = ""
        for node in trajectory:
            content += f"- **{node.get('level', '未知境界')}**: {node.get('description', '无描述')}\n"
        
        return content
    
    def _format_analysis_report(self, report_data: Dict[str, Any]) -> str:
        """格式化分析报告为Markdown"""
        content = []
        
        # 标题
        content.append("# 小说生成分析报告")
        content.append("")
        
        # 生成信息
        generation_info = report_data.get('generation_info', {})
        if generation_info:
            content.append("## 生成信息")
            content.append("")
            content.append(f"- **核心概念**: {generation_info.get('core_concept', '未知')}")
            content.append(f"- **世界观名称**: {generation_info.get('world_name', '未知')}")
            content.append(f"- **剧情标题**: {generation_info.get('plot_title', '未知')}")
            content.append(f"- **角色数量**: {generation_info.get('total_characters', 0)}")
            content.append(f"- **生成时间**: {generation_info.get('generation_time', '未知')}")
            content.append("")
        
        # 评分信息
        scores = report_data.get('scores', {})
        if scores:
            content.append("## 内容评分")
            content.append("")
            content.append(f"**总分**: {scores.get('total_score', 0):.1f}/10")
            content.append("")
            
            dimension_scores = scores.get('scores', {})
            if dimension_scores:
                content.append("### 各维度评分")
                content.append("")
                for dimension, score in dimension_scores.items():
                    content.append(f"- **{dimension}**: {score:.1f}/10")
                content.append("")
        
        # 逻辑检查
        logic_check = report_data.get('logic_check', {})
        if logic_check:
            content.append("## 逻辑检查")
            content.append("")
            content.append(f"**状态**: {logic_check.get('status', '未知')}")
            content.append("")
            
            analysis = logic_check.get('analysis', '')
            if analysis:
                content.append("### 检查结果")
                content.append("")
                content.append(analysis)
                content.append("")
        
        # 反思报告
        report = report_data.get('report', {})
        if report:
            content.append("## 反思报告")
            content.append("")
            
            report_content = report.get('content', '')
            if report_content:
                content.append(report_content)
                content.append("")
        
        return "\n".join(content)
    
    def _format_plot_arcs(self, arcs: list) -> str:
        """格式化剧情弧线"""
        if not arcs:
            return "暂无剧情弧线"
        
        content = ""
        for arc in arcs:
            content += f"### {arc.get('title', '未命名弧线')}\n"
            content += f"- **结构**: {arc.get('plot_structure', '未知')}\n"
            content += f"- **描述**: {arc.get('description', '无描述')}\n"
            content += f"- **目标长度**: {arc.get('target_length', '未知')}章节\n"
            content += "\n"
        
        return content
    
    def _format_analysis_report(self, report_data: Dict[str, Any]) -> str:
        """格式化分析报告为Markdown"""
        content = []
        
        # 标题
        content.append("# 小说生成分析报告")
        content.append("")
        
        # 生成信息
        generation_info = report_data.get('generation_info', {})
        if generation_info:
            content.append("## 生成信息")
            content.append("")
            content.append(f"- **核心概念**: {generation_info.get('core_concept', '未知')}")
            content.append(f"- **世界观名称**: {generation_info.get('world_name', '未知')}")
            content.append(f"- **剧情标题**: {generation_info.get('plot_title', '未知')}")
            content.append(f"- **角色数量**: {generation_info.get('total_characters', 0)}")
            content.append(f"- **生成时间**: {generation_info.get('generation_time', '未知')}")
            content.append("")
        
        # 评分信息
        scores = report_data.get('scores', {})
        if scores:
            content.append("## 内容评分")
            content.append("")
            content.append(f"**总分**: {scores.get('total_score', 0):.1f}/10")
            content.append("")
            
            dimension_scores = scores.get('scores', {})
            if dimension_scores:
                content.append("### 各维度评分")
                content.append("")
                for dimension, score in dimension_scores.items():
                    content.append(f"- **{dimension}**: {score:.1f}/10")
                content.append("")
        
        # 逻辑检查
        logic_check = report_data.get('logic_check', {})
        if logic_check:
            content.append("## 逻辑检查")
            content.append("")
            content.append(f"**状态**: {logic_check.get('status', '未知')}")
            content.append("")
            
            analysis = logic_check.get('analysis', '')
            if analysis:
                content.append("### 检查结果")
                content.append("")
                content.append(analysis)
                content.append("")
        
        # 反思报告
        report = report_data.get('report', {})
        if report:
            content.append("## 反思报告")
            content.append("")
            
            report_content = report.get('content', '')
            if report_content:
                content.append(report_content)
                content.append("")
        
        return "\n".join(content)
    
    def _format_foreshadowing(self, foreshadowing: list) -> str:
        """格式化伏笔设计"""
        if not foreshadowing:
            return "暂无伏笔设定"
        
        content = ""
        for foreshadow in foreshadowing:
            content += f"### {foreshadow.get('title', '未命名伏笔')}\n"
            content += f"- **描述**: {foreshadow.get('description', '无描述')}\n"
            content += f"- **重要性**: {foreshadow.get('importance', '未知')}/10\n"
            content += f"- **隐蔽性**: {foreshadow.get('subtlety', '未知')}/10\n"
            content += "\n"
        
        return content
    
    def _format_analysis_report(self, report_data: Dict[str, Any]) -> str:
        """格式化分析报告为Markdown"""
        content = []
        
        # 标题
        content.append("# 小说生成分析报告")
        content.append("")
        
        # 生成信息
        generation_info = report_data.get('generation_info', {})
        if generation_info:
            content.append("## 生成信息")
            content.append("")
            content.append(f"- **核心概念**: {generation_info.get('core_concept', '未知')}")
            content.append(f"- **世界观名称**: {generation_info.get('world_name', '未知')}")
            content.append(f"- **剧情标题**: {generation_info.get('plot_title', '未知')}")
            content.append(f"- **角色数量**: {generation_info.get('total_characters', 0)}")
            content.append(f"- **生成时间**: {generation_info.get('generation_time', '未知')}")
            content.append("")
        
        # 评分信息
        scores = report_data.get('scores', {})
        if scores:
            content.append("## 内容评分")
            content.append("")
            content.append(f"**总分**: {scores.get('total_score', 0):.1f}/10")
            content.append("")
            
            dimension_scores = scores.get('scores', {})
            if dimension_scores:
                content.append("### 各维度评分")
                content.append("")
                for dimension, score in dimension_scores.items():
                    content.append(f"- **{dimension}**: {score:.1f}/10")
                content.append("")
        
        # 逻辑检查
        logic_check = report_data.get('logic_check', {})
        if logic_check:
            content.append("## 逻辑检查")
            content.append("")
            content.append(f"**状态**: {logic_check.get('status', '未知')}")
            content.append("")
            
            analysis = logic_check.get('analysis', '')
            if analysis:
                content.append("### 检查结果")
                content.append("")
                content.append(analysis)
                content.append("")
        
        # 反思报告
        report = report_data.get('report', {})
        if report:
            content.append("## 反思报告")
            content.append("")
            
            report_content = report.get('content', '')
            if report_content:
                content.append(report_content)
                content.append("")
        
        return "\n".join(content)
    
    def _format_scores(self, scores: dict) -> str:
        """格式化评分详情"""
        if not scores:
            return "暂无评分数据"
        
        content = ""
        for dimension, score in scores.items():
            content += f"- **{dimension}**: {score}/10\n"
        
        return content
    
    def _format_analysis_report(self, report_data: Dict[str, Any]) -> str:
        """格式化分析报告为Markdown"""
        content = []
        
        # 标题
        content.append("# 小说生成分析报告")
        content.append("")
        
        # 生成信息
        generation_info = report_data.get('generation_info', {})
        if generation_info:
            content.append("## 生成信息")
            content.append("")
            content.append(f"- **核心概念**: {generation_info.get('core_concept', '未知')}")
            content.append(f"- **世界观名称**: {generation_info.get('world_name', '未知')}")
            content.append(f"- **剧情标题**: {generation_info.get('plot_title', '未知')}")
            content.append(f"- **角色数量**: {generation_info.get('total_characters', 0)}")
            content.append(f"- **生成时间**: {generation_info.get('generation_time', '未知')}")
            content.append("")
        
        # 评分信息
        scores = report_data.get('scores', {})
        if scores:
            content.append("## 内容评分")
            content.append("")
            content.append(f"**总分**: {scores.get('total_score', 0):.1f}/10")
            content.append("")
            
            dimension_scores = scores.get('scores', {})
            if dimension_scores:
                content.append("### 各维度评分")
                content.append("")
                for dimension, score in dimension_scores.items():
                    content.append(f"- **{dimension}**: {score:.1f}/10")
                content.append("")
        
        # 逻辑检查
        logic_check = report_data.get('logic_check', {})
        if logic_check:
            content.append("## 逻辑检查")
            content.append("")
            content.append(f"**状态**: {logic_check.get('status', '未知')}")
            content.append("")
            
            analysis = logic_check.get('analysis', '')
            if analysis:
                content.append("### 检查结果")
                content.append("")
                content.append(analysis)
                content.append("")
        
        # 反思报告
        report = report_data.get('report', {})
        if report:
            content.append("## 反思报告")
            content.append("")
            
            report_content = report.get('content', '')
            if report_content:
                content.append(report_content)
                content.append("")
        
        return "\n".join(content)
    
    def _format_list(self, items: list) -> str:
        """格式化简单列表"""
        if not items:
            return "暂无"
        
        return "\n".join([f"- {item}" for item in items])
    
    def write_antagonist_info(self, antagonists: List[Dict[str, Any]], 
                            antagonist_networks: List[Dict[str, Any]] = None,
                            antagonist_arcs: List[Dict[str, Any]] = None) -> str:
        """写入反派信息"""
        filename = f"反派设定_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        filepath = self.novel_dir / filename
        
        content = "# 反派角色设定\n\n"
        
        # 反派角色信息
        for i, antagonist in enumerate(antagonists, 1):
            content += f"""## 反派{i}: {antagonist.get('name', '未命名反派')}

### 基本信息
- **年龄**: {antagonist.get('age', '未知')}岁
- **性别**: {antagonist.get('gender', '未知')}
- **修炼境界**: {antagonist.get('cultivation_level', '未知')}
- **灵根属性**: {antagonist.get('element_type', '未知')}
- **反派类型**: {antagonist.get('antagonist_type', '未知')}
- **威胁等级**: {antagonist.get('threat_level', '未知')}

### 外貌描述
{antagonist.get('appearance', '暂无描述')}

### 性格特质
{', '.join(antagonist.get('personality', []))}

### 背景故事
{antagonist.get('background', '暂无描述')}

### 动机和目标
- **主要动机**: {antagonist.get('primary_motivation', '未知')}
- **次要动机**: {', '.join(antagonist.get('secondary_motivations', []))}

### 能力和资源
- **特殊能力**: {', '.join(antagonist.get('special_abilities', []))}
- **掌握功法**: {', '.join(antagonist.get('techniques', []))}
- **拥有法宝**: {', '.join(antagonist.get('artifacts', []))}

### 关系和影响
- **影响范围**: {antagonist.get('influence_scope', '未知')}
- **追随者**: {', '.join(antagonist.get('followers', []))}
- **敌人**: {', '.join(antagonist.get('enemies', []))}

### 剧情相关
- **主要冲突**: {', '.join(antagonist.get('major_conflicts', []))}
- **失败条件**: {', '.join(antagonist.get('defeat_conditions', []))}
- **救赎可能**: {'是' if antagonist.get('redemption_potential', False) else '否'}
- **秘密**: {', '.join(antagonist.get('secrets', []))}
- **弱点**: {', '.join(antagonist.get('weaknesses', []))}

---
"""
        
        # 反派网络信息
        if antagonist_networks:
            content += "\n## 反派网络\n\n"
            for network in antagonist_networks:
                content += f"""### {network.get('name', '未命名网络')}
- **描述**: {network.get('description', '暂无描述')}
- **领导者**: {network.get('leader', '未知')}
- **威胁等级**: {network.get('threat_level', '未知')}
- **影响区域**: {', '.join(network.get('influence_areas', []))}

"""
        
        # 反派剧情弧线
        if antagonist_arcs:
            content += "\n## 反派剧情弧线\n\n"
            for arc in antagonist_arcs:
                content += f"""### {arc.get('arc_name', '未命名弧线')}
- **描述**: {arc.get('description', '暂无描述')}
- **重要程度**: {arc.get('importance', '未知')}

#### 引入阶段
{arc.get('introduction', {}).get('first_appearance', '暂无描述')}

#### 发展阶段
{arc.get('development', {}).get('relationship_evolution', '暂无描述')}

#### 对抗阶段
{arc.get('confrontation', {}).get('direct_conflict', '暂无描述')}

#### 解决阶段
{arc.get('resolution', {}).get('final_battle', '暂无描述')}

"""
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ 反派设定已保存: {filepath}")
        return str(filepath)
    
    def _format_events_sequence(self, events: List[Any]) -> str:
        """格式化事件序列为Markdown"""
        content = ["# 事件序列", ""]
        
        for i, event in enumerate(events, 1):
            # 处理Event对象或字典
            if hasattr(event, 'dict'):
                event_data = event.dict()
            else:
                event_data = event
            
            content.append(f"## 事件 {i}: {event_data.get('title', '未命名事件')}")
            content.append("")
            
            # 基本信息
            content.append("### 基本信息")
            content.append(f"- **类型**: {event_data.get('event_type', '未知')}")
            content.append(f"- **重要性**: {event_data.get('importance', '未知')}")
            content.append(f"- **地点**: {event_data.get('setting', '未知')}")
            content.append(f"- **持续时间**: {event_data.get('duration', '未知')}")
            content.append("")
            
            # 事件描述
            content.append("### 事件描述")
            content.append(event_data.get('description', '暂无描述'))
            content.append("")
            
            # 参与角色
            participants = event_data.get('participants', [])
            if participants:
                content.append("### 参与角色")
                for participant in participants:
                    content.append(f"- {participant}")
                content.append("")
            
            # 事件结果
            outcome = event_data.get('outcome', '')
            if outcome:
                content.append("### 事件结果")
                content.append(outcome)
                content.append("")
            
            # 剧情影响
            plot_impact = event_data.get('plot_impact', '')
            if plot_impact:
                content.append("### 剧情影响")
                content.append(plot_impact)
                content.append("")
            
            # 伏笔元素
            foreshadowing = event_data.get('foreshadowing_elements', [])
            if foreshadowing:
                content.append("### 伏笔元素")
                for element in foreshadowing:
                    content.append(f"- {element}")
                content.append("")
            
            content.append("---")
            content.append("")
        
        content.append("*本文档由小说生成智能体框架自动生成*")
        return "\n".join(content)
    
    def write_chapter_outline(self, chapters: List[Dict[str, Any]]) -> str:
        """保存章节大纲到MD文件"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"章节大纲_{timestamp}.md"
        filepath = os.path.join(self.novel_dir, filename)
        
        content = self._format_chapter_outline(chapters)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return filepath
    
    def _format_chapter_outline(self, chapters: List[Dict[str, Any]]) -> str:
        """格式化章节大纲文档"""
        content = []
        content.append("# 章节大纲")
        content.append("")
        content.append(f"**总章节数**: {len(chapters)}")
        content.append("")
        
        for i, chapter in enumerate(chapters, 1):
            content.append(f"## 第{i}章: {chapter.get('title', f'第{i}章')}")
            content.append("")
            
            # 章节摘要
            summary = chapter.get('summary', '')
            if summary:
                content.append("### 章节摘要")
                content.append(summary)
                content.append("")
            
            # 主要事件
            main_events = chapter.get('main_events', [])
            if main_events:
                content.append("### 主要事件")
                for event_id in main_events:
                    content.append(f"- {event_id}")
                content.append("")
            
            # 场景
            scenes = chapter.get('scenes', [])
            if scenes:
                content.append("### 场景")
                for scene in scenes:
                    scene_title = scene.get('title', '未命名场景')
                    scene_summary = scene.get('summary', '')
                    content.append(f"- **{scene_title}**: {scene_summary}")
                content.append("")
            
            # 字数统计
            word_count = chapter.get('word_count', 0)
            if word_count > 0:
                content.append(f"**预计字数**: {word_count}字")
                content.append("")
            
            content.append("---")
            content.append("")
        
        content.append("*本文档由小说生成智能体框架自动生成*")
        return "\n".join(content)
    
    def write_foreshadowing_network(self, foreshadowing_network: Dict[str, Any]) -> str:
        """保存伏笔网络到MD文件"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"伏笔网络_{timestamp}.md"
        filepath = os.path.join(self.novel_dir, filename)
        
        content = self._format_foreshadowing_network(foreshadowing_network)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return filepath
    
    def _format_foreshadowing_network(self, foreshadowing_network: Dict[str, Any]) -> str:
        """格式化伏笔网络文档"""
        content = []
        content.append("# 伏笔网络")
        content.append("")
        
        # 伏笔设置
        setups = foreshadowing_network.get('setups', [])
        if setups:
            content.append("## 伏笔设置")
            content.append("")
            for i, setup in enumerate(setups, 1):
                content.append(f"### 伏笔{i}: {setup.get('title', f'伏笔{i}')}")
                content.append("")
                
                description = setup.get('description', '')
                if description:
                    content.append("**描述**:")
                    content.append(description)
                    content.append("")
                
                location = setup.get('location', '')
                if location:
                    content.append(f"**埋设位置**: {location}")
                    content.append("")
                
                trigger_condition = setup.get('trigger_condition', '')
                if trigger_condition:
                    content.append(f"**触发条件**: {trigger_condition}")
                    content.append("")
                
                content.append("---")
                content.append("")
        
        # 伏笔回收
        payoffs = foreshadowing_network.get('payoffs', [])
        if payoffs:
            content.append("## 伏笔回收")
            content.append("")
            for i, payoff in enumerate(payoffs, 1):
                content.append(f"### 回收{i}: {payoff.get('title', f'回收{i}')}")
                content.append("")
                
                description = payoff.get('description', '')
                if description:
                    content.append("**描述**:")
                    content.append(description)
                    content.append("")
                
                related_setup = payoff.get('related_setup', '')
                if related_setup:
                    content.append(f"**相关伏笔**: {related_setup}")
                    content.append("")
                
                content.append("---")
                content.append("")
        
        content.append("*本文档由小说生成智能体框架自动生成*")
        return "\n".join(content)
    
    def _format_power_system(self, power_system: Dict[str, Any]) -> str:
        """格式化力量体系"""
        if not power_system:
            return "暂无设定"
        
        content = []
        
        # 修炼境界
        cultivation_realms = power_system.get('cultivation_realms', [])
        if cultivation_realms:
            content.append("### 修炼境界")
            content.append("")
            for realm in cultivation_realms:
                content.append(f"**{realm.get('name', '未知境界')}** (等级: {realm.get('level', '未知')})")
                content.append(f"- 描述: {realm.get('description', '暂无描述')}")
                content.append(f"- 突破要求: {realm.get('requirements', '暂无要求')}")
                content.append("")
        
        # 能量类型
        energy_types = power_system.get('energy_types', [])
        if energy_types:
            content.append("### 能量类型")
            content.append("")
            for energy in energy_types:
                content.append(f"**{energy.get('name', '未知能量')}** ({energy.get('rarity', '未知')})")
                content.append(f"- 描述: {energy.get('description', '暂无描述')}")
                content.append("")
        
        # 功法类别
        technique_categories = power_system.get('technique_categories', [])
        if technique_categories:
            content.append("### 功法类别")
            content.append("")
            for category in technique_categories:
                content.append(f"**{category.get('name', '未知类别')}** (难度: {category.get('difficulty', '未知')})")
                content.append(f"- 描述: {category.get('description', '暂无描述')}")
                content.append("")
        
        return "\n".join(content) if content else "暂无设定"
    
    def _format_geography(self, geography: Dict[str, Any]) -> str:
        """格式化地理设定"""
        if not geography:
            return "暂无设定"
        
        content = []
        
        # 主要区域
        main_regions = geography.get('main_regions', [])
        if main_regions:
            content.append("### 主要区域")
            content.append("")
            for region in main_regions:
                content.append(f"**{region.get('name', '未知区域')}** ({region.get('type', '未知类型')})")
                content.append(f"- 描述: {region.get('description', '暂无描述')}")
                if region.get('resources'):
                    content.append(f"- 资源: {', '.join(region['resources'])}")
                if region.get('special_features'):
                    content.append(f"- 特色: {region['special_features']}")
                content.append("")
        
        # 特殊地点
        special_locations = geography.get('special_locations', [])
        if special_locations:
            content.append("### 特殊地点")
            content.append("")
            for location in special_locations:
                content.append(f"**{location.get('name', '未知地点')}** ({location.get('type', '未知类型')})")
                content.append(f"- 描述: {location.get('description', '暂无描述')}")
                if location.get('significance'):
                    content.append(f"- 重要性: {location['significance']}")
                if location.get('dangers'):
                    content.append(f"- 危险: {', '.join(location['dangers'])}")
                content.append("")
        
        return "\n".join(content) if content else "暂无设定"
    
    def _format_history_culture(self, history_culture: Dict[str, Any]) -> str:
        """格式化历史文化"""
        if not history_culture:
            return "暂无设定"
        
        content = []
        
        # 历史事件
        historical_events = history_culture.get('historical_events', [])
        if historical_events:
            content.append("### 历史事件")
            content.append("")
            for event in historical_events:
                content.append(f"**{event.get('name', '未知事件')}** ({event.get('time_period', '未知时间')})")
                content.append(f"- 描述: {event.get('description', '暂无描述')}")
                if event.get('impact'):
                    content.append(f"- 影响: {event['impact']}")
                content.append("")
        
        # 文化特色
        cultural_features = history_culture.get('cultural_features', [])
        if cultural_features:
            content.append("### 文化特色")
            content.append("")
            for feature in cultural_features:
                content.append(f"**{feature.get('region', '未知区域')}**")
                if feature.get('traditions'):
                    content.append(f"- 传统习俗: {feature['traditions']}")
                if feature.get('values'):
                    content.append(f"- 价值观念: {feature['values']}")
                if feature.get('lifestyle'):
                    content.append(f"- 生活方式: {feature['lifestyle']}")
                content.append("")
        
        # 当前冲突
        current_conflicts = history_culture.get('current_conflicts', [])
        if current_conflicts:
            content.append("### 当前冲突")
            content.append("")
            for conflict in current_conflicts:
                content.append(f"**{conflict.get('name', '未知冲突')}**")
                content.append(f"- 描述: {conflict.get('description', '暂无描述')}")
                if conflict.get('parties'):
                    content.append(f"- 参与方: {', '.join(conflict['parties'])}")
                if conflict.get('stakes'):
                    content.append(f"- 利害关系: {conflict['stakes']}")
                content.append("")
        
        return "\n".join(content) if content else "暂无设定"
    
    def _format_society(self, society: Dict[str, Any]) -> str:
        """格式化社会组织"""
        if not society:
            return "暂无设定"
        
        content = []
        
        # 组织
        organizations = society.get('organizations', [])
        if organizations:
            content.append("### 主要组织")
            content.append("")
            for org in organizations:
                content.append(f"**{org.get('name', '未知组织')}** ({org.get('type', '未知类型')})")
                content.append(f"- 描述: {org.get('description', '暂无描述')}")
                if org.get('power_level'):
                    content.append(f"- 实力等级: {org['power_level']}")
                if org.get('ideology'):
                    content.append(f"- 理念宗旨: {org['ideology']}")
                if org.get('structure'):
                    content.append(f"- 组织结构: {org['structure']}")
                content.append("")
        
        # 社会制度
        social_system = society.get('social_system', {})
        if social_system:
            content.append("### 社会制度")
            content.append("")
            if social_system.get('hierarchy'):
                content.append(f"- **等级制度**: {social_system['hierarchy']}")
            if social_system.get('economy'):
                content.append(f"- **经济体系**: {social_system['economy']}")
            if social_system.get('trading'):
                content.append(f"- **交易方式**: {social_system['trading']}")
            content.append("")
        
        return "\n".join(content) if content else "暂无设定"
