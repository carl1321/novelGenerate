-- 简化章节大纲数据库结构
-- 删除不需要的字段，适配精简的输出格式

-- 1. 删除scenes表中不需要的字段
ALTER TABLE scenes DROP COLUMN IF EXISTS event_relation;
ALTER TABLE scenes DROP COLUMN IF EXISTS location;
ALTER TABLE scenes DROP COLUMN IF EXISTS purpose;
ALTER TABLE scenes DROP COLUMN IF EXISTS characters_present;
ALTER TABLE scenes DROP COLUMN IF EXISTS related_events;

-- 2. 删除chapter_outlines表中不需要的字段
ALTER TABLE chapter_outlines DROP COLUMN IF EXISTS writing_notes;
ALTER TABLE chapter_outlines DROP COLUMN IF EXISTS plot_function;
ALTER TABLE chapter_outlines DROP COLUMN IF EXISTS estimated_word_count;
ALTER TABLE chapter_outlines DROP COLUMN IF EXISTS conflict_development;

-- 3. 保留核心字段
-- scenes表保留: id, chapter_outline_id, scene_number, title, description, scene_title, scene_description, created_at
-- chapter_outlines表保留: id, plot_outline_id, chapter_number, title, act_belonging, chapter_summary, core_event, status, created_at, updated_at

-- 4. 添加注释说明
COMMENT ON TABLE scenes IS '场景表 - 精简版，只包含核心字段';
COMMENT ON TABLE chapter_outlines IS '章节大纲表 - 精简版，只包含核心字段';

COMMENT ON COLUMN scenes.title IS '场景标题（旧字段，保持兼容）';
COMMENT ON COLUMN scenes.description IS '场景描述（旧字段，保持兼容）';
COMMENT ON COLUMN scenes.scene_title IS '场景标题（新字段）';
COMMENT ON COLUMN scenes.scene_description IS '场景描述（新字段）';

COMMENT ON COLUMN chapter_outlines.core_event IS '核心事件ID或标题';
COMMENT ON COLUMN chapter_outlines.chapter_summary IS '章节概要';
COMMENT ON COLUMN chapter_outlines.act_belonging IS '所属幕次';
