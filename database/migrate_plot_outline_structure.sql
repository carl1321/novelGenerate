-- 剧情大纲数据库结构迁移脚本
-- 从旧的结构迁移到新的简化版故事驱动模式

-- 执行前请备份数据库

-- 1. 备份现有数据
CREATE TABLE plot_outlines_backup AS SELECT * FROM plot_outlines;
CREATE TABLE acts_backup AS SELECT * FROM acts;

-- 2. 删除旧的列（如果存在）
ALTER TABLE plot_outlines DROP COLUMN IF EXISTS description;
ALTER TABLE plot_outlines DROP COLUMN IF EXISTS story_structure;
ALTER TABLE plot_outlines DROP COLUMN IF EXISTS story_framework;
ALTER TABLE plot_outlines DROP COLUMN IF EXISTS character_positions;
ALTER TABLE plot_outlines DROP COLUMN IF EXISTS plot_blocks;
ALTER TABLE plot_outlines DROP COLUMN IF EXISTS story_flow;

-- 3. 添加新的列
ALTER TABLE plot_outlines ADD COLUMN IF NOT EXISTS story_summary TEXT;
ALTER TABLE plot_outlines ADD COLUMN IF NOT EXISTS core_conflict TEXT;
ALTER TABLE plot_outlines ADD COLUMN IF NOT EXISTS theme TEXT;
ALTER TABLE plot_outlines ADD COLUMN IF NOT EXISTS protagonist_name VARCHAR(255);
ALTER TABLE plot_outlines ADD COLUMN IF NOT EXISTS protagonist_background TEXT;
ALTER TABLE plot_outlines ADD COLUMN IF NOT EXISTS protagonist_personality TEXT;
ALTER TABLE plot_outlines ADD COLUMN IF NOT EXISTS protagonist_goals TEXT;
ALTER TABLE plot_outlines ADD COLUMN IF NOT EXISTS core_concept TEXT;
ALTER TABLE plot_outlines ADD COLUMN IF NOT EXISTS world_description TEXT;
ALTER TABLE plot_outlines ADD COLUMN IF NOT EXISTS geography_setting TEXT;

-- 4. 更新acts表结构
-- 删除旧的列
ALTER TABLE acts DROP COLUMN IF EXISTS start_position;
ALTER TABLE acts DROP COLUMN IF EXISTS end_position;
ALTER TABLE acts DROP COLUMN IF EXISTS purpose;
ALTER TABLE acts DROP COLUMN IF EXISTS key_events;
ALTER TABLE acts DROP COLUMN IF EXISTS emotional_tone;
ALTER TABLE acts DROP COLUMN IF EXISTS character_focus;
ALTER TABLE acts DROP COLUMN IF EXISTS worldview_elements;
ALTER TABLE acts DROP COLUMN IF EXISTS estimated_chapters;
ALTER TABLE acts DROP COLUMN IF EXISTS estimated_words;

-- 添加新的6要素列
ALTER TABLE acts ADD COLUMN IF NOT EXISTS core_mission TEXT;
ALTER TABLE acts ADD COLUMN IF NOT EXISTS daily_events TEXT;
ALTER TABLE acts ADD COLUMN IF NOT EXISTS conflict_events TEXT;
ALTER TABLE acts ADD COLUMN IF NOT EXISTS special_events TEXT;
ALTER TABLE acts ADD COLUMN IF NOT EXISTS major_events TEXT;
ALTER TABLE acts ADD COLUMN IF NOT EXISTS stage_result TEXT;

-- 5. 迁移现有数据（如果有的话）
-- 将description迁移到story_summary
UPDATE plot_outlines SET story_summary = description WHERE story_summary IS NULL AND description IS NOT NULL;

-- 设置默认值
UPDATE plot_outlines SET 
    story_summary = COALESCE(story_summary, '暂无故事简介'),
    core_conflict = COALESCE(core_conflict, '暂无核心冲突'),
    theme = COALESCE(theme, '暂无主题思想'),
    protagonist_name = COALESCE(protagonist_name, '主角'),
    protagonist_background = COALESCE(protagonist_background, '暂无背景'),
    protagonist_personality = COALESCE(protagonist_personality, '暂无性格描述'),
    protagonist_goals = COALESCE(protagonist_goals, '暂无目标'),
    core_concept = COALESCE(core_concept, '暂无核心概念'),
    world_description = COALESCE(world_description, '暂无世界观描述'),
    geography_setting = COALESCE(geography_setting, '暂无地理设定');

-- 6. 设置非空约束
ALTER TABLE plot_outlines ALTER COLUMN story_summary SET NOT NULL;
ALTER TABLE plot_outlines ALTER COLUMN core_conflict SET NOT NULL;
ALTER TABLE plot_outlines ALTER COLUMN theme SET NOT NULL;
ALTER TABLE plot_outlines ALTER COLUMN protagonist_name SET NOT NULL;
ALTER TABLE plot_outlines ALTER COLUMN protagonist_background SET NOT NULL;
ALTER TABLE plot_outlines ALTER COLUMN protagonist_personality SET NOT NULL;
ALTER TABLE plot_outlines ALTER COLUMN protagonist_goals SET NOT NULL;
ALTER TABLE plot_outlines ALTER COLUMN core_concept SET NOT NULL;
ALTER TABLE plot_outlines ALTER COLUMN world_description SET NOT NULL;
ALTER TABLE plot_outlines ALTER COLUMN geography_setting SET NOT NULL;

ALTER TABLE acts ALTER COLUMN core_mission SET NOT NULL;
ALTER TABLE acts ALTER COLUMN daily_events SET NOT NULL;
ALTER TABLE acts ALTER COLUMN conflict_events SET NOT NULL;
ALTER TABLE acts ALTER COLUMN special_events SET NOT NULL;
ALTER TABLE acts ALTER COLUMN major_events SET NOT NULL;
ALTER TABLE acts ALTER COLUMN stage_result SET NOT NULL;

-- 7. 删除不再需要的turning_points表（如果存在）
DROP TABLE IF EXISTS turning_points;

-- 8. 添加索引优化查询性能
CREATE INDEX IF NOT EXISTS idx_plot_outlines_worldview_id ON plot_outlines(worldview_id);
CREATE INDEX IF NOT EXISTS idx_plot_outlines_status ON plot_outlines(status);
CREATE INDEX IF NOT EXISTS idx_plot_outlines_created_at ON plot_outlines(created_at);
CREATE INDEX IF NOT EXISTS idx_acts_plot_outline_id ON acts(plot_outline_id);
CREATE INDEX IF NOT EXISTS idx_acts_act_number ON acts(act_number);

-- 9. 添加注释
COMMENT ON TABLE plot_outlines IS '剧情大纲表 - 简化版故事驱动模式';
COMMENT ON COLUMN plot_outlines.story_summary IS '故事简介';
COMMENT ON COLUMN plot_outlines.core_conflict IS '核心冲突';
COMMENT ON COLUMN plot_outlines.theme IS '主题思想';
COMMENT ON COLUMN plot_outlines.protagonist_name IS '主角姓名';
COMMENT ON COLUMN plot_outlines.protagonist_background IS '主角背景';
COMMENT ON COLUMN plot_outlines.protagonist_personality IS '主角性格特质';
COMMENT ON COLUMN plot_outlines.protagonist_goals IS '主角目标';
COMMENT ON COLUMN plot_outlines.core_concept IS '世界观核心概念';
COMMENT ON COLUMN plot_outlines.world_description IS '世界观描述';
COMMENT ON COLUMN plot_outlines.geography_setting IS '地理设定';

COMMENT ON TABLE acts IS '幕次表 - 6要素结构';
COMMENT ON COLUMN acts.core_mission IS '核心任务：主角在这一幕的主要目标';
COMMENT ON COLUMN acts.daily_events IS '日常事件：主角日常行动，会获得什么';
COMMENT ON COLUMN acts.conflict_events IS '冲突事件：主角服务于目标的关键行动，会有什么阻碍';
COMMENT ON COLUMN acts.special_events IS '特殊事件：主角的转折事件或奇遇，获得什么关键提升';
COMMENT ON COLUMN acts.major_events IS '重大事件：非主角发起的环境变化事件，如何推动剧情发展';
COMMENT ON COLUMN acts.stage_result IS '阶段结果：主角获得了哪些成果，状态如何，拥有哪些资源，新目标是什么';

-- 迁移完成
SELECT '剧情大纲数据库结构迁移完成！' as message;
