-- 更新事件评分表结构，简化评分维度并添加文笔质量字段

-- 1. 添加新的文笔质量字段
ALTER TABLE event_scores ADD COLUMN IF NOT EXISTS writing_quality FLOAT DEFAULT 5.0;

-- 2. 将现有的emotional_impact数据迁移到writing_quality（如果writing_quality为空）
UPDATE event_scores 
SET writing_quality = emotional_impact 
WHERE writing_quality IS NULL OR writing_quality = 5.0;

-- 3. 删除不再需要的字段（可选，先注释掉以防数据丢失）
-- ALTER TABLE event_scores DROP COLUMN IF EXISTS character_development;
-- ALTER TABLE event_scores DROP COLUMN IF EXISTS world_consistency;
-- ALTER TABLE event_scores DROP COLUMN IF EXISTS emotional_impact;
-- ALTER TABLE event_scores DROP COLUMN IF EXISTS foreshadowing;

-- 4. 添加注释
COMMENT ON COLUMN event_scores.writing_quality IS '文笔质量评分 (0-10)';
COMMENT ON COLUMN event_scores.protagonist_involvement IS '主角参与度评分 (0-10)';
COMMENT ON COLUMN event_scores.plot_coherence IS '剧情逻辑性评分 (0-10)';
COMMENT ON COLUMN event_scores.dramatic_tension IS '戏剧张力评分 (0-10)';
COMMENT ON COLUMN event_scores.overall_quality IS '综合质量评分 (0-10)';
