-- 清理数据库迁移后的遗留问题
-- 删除依赖的视图和旧列

-- 1. 删除依赖的视图
DROP VIEW IF EXISTS plot_outline_details CASCADE;
DROP VIEW IF EXISTS chapter_outline_unified CASCADE;

-- 2. 删除旧的列（现在应该可以删除了）
ALTER TABLE plot_outlines DROP COLUMN IF EXISTS description CASCADE;
ALTER TABLE plot_outlines DROP COLUMN IF EXISTS story_structure CASCADE;
ALTER TABLE plot_outlines DROP COLUMN IF EXISTS story_framework CASCADE;
ALTER TABLE plot_outlines DROP COLUMN IF EXISTS character_positions CASCADE;
ALTER TABLE plot_outlines DROP COLUMN IF EXISTS plot_blocks CASCADE;
ALTER TABLE plot_outlines DROP COLUMN IF EXISTS story_flow CASCADE;

-- 3. 删除不再需要的turning_points表
DROP TABLE IF EXISTS turning_points CASCADE;

-- 4. 为acts表的新字段设置默认值
UPDATE acts SET 
    core_mission = COALESCE(core_mission, '暂无核心任务'),
    daily_events = COALESCE(daily_events, '暂无日常事件'),
    conflict_events = COALESCE(conflict_events, '暂无冲突事件'),
    special_events = COALESCE(special_events, '暂无特殊事件'),
    major_events = COALESCE(major_events, '暂无重大事件'),
    stage_result = COALESCE(stage_result, '暂无阶段结果')
WHERE core_mission IS NULL OR daily_events IS NULL OR conflict_events IS NULL 
   OR special_events IS NULL OR major_events IS NULL OR stage_result IS NULL;

-- 5. 设置非空约束
ALTER TABLE acts ALTER COLUMN core_mission SET NOT NULL;
ALTER TABLE acts ALTER COLUMN daily_events SET NOT NULL;
ALTER TABLE acts ALTER COLUMN conflict_events SET NOT NULL;
ALTER TABLE acts ALTER COLUMN special_events SET NOT NULL;
ALTER TABLE acts ALTER COLUMN major_events SET NOT NULL;
ALTER TABLE acts ALTER COLUMN stage_result SET NOT NULL;

-- 6. 重新创建必要的视图（如果需要的话）
-- 这里可以根据需要重新创建视图

-- 清理完成
SELECT '数据库清理完成！' as message;
