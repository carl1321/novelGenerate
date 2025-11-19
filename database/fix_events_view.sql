-- 修复事件视图，确保original_title字段正确
-- 重新创建events_with_latest_evolution视图

-- 1. 删除现有视图
DROP VIEW IF EXISTS events_with_latest_evolution CASCADE;

-- 2. 重新创建视图
CREATE VIEW events_with_latest_evolution AS
SELECT 
    e.id as original_event_id,
    e.title as original_title,
    e.event_type as original_event_type,
    e.description as original_description,
    e.outcome as original_outcome,
    e.plot_outline_id,
    e.chapter_number,
    e.sequence_order,
    e.created_at as original_created_at,
    e.updated_at as original_updated_at,
    
    -- 最新进化版本信息
    eeh.id as current_evolution_id,
    eeh.version as current_version,
    eeh.title as current_title,
    eeh.event_type as current_event_type,
    eeh.description as current_description,
    eeh.outcome as current_outcome,
    eeh.evolution_reason,
    eeh.score_id,
    eeh.parent_version_id,
    eeh.created_at as evolution_created_at,
    eeh.updated_at as evolution_updated_at,
    
    -- 判断是否有进化版本
    CASE 
        WHEN eeh.id IS NOT NULL THEN TRUE 
        ELSE FALSE 
    END as has_evolution
    
FROM events e
LEFT JOIN event_evolution_history eeh ON (
    e.id = eeh.original_event_id 
    AND eeh.is_current_version = TRUE
);

-- 3. 添加注释
COMMENT ON VIEW events_with_latest_evolution IS '事件与最新进化版本的关联视图，用于查询时只显示最新版本';
