-- 事件-章节大纲集成增强脚本
-- 为现有事件表添加新字段，创建事件-章节映射表

-- 1. 为events表添加新字段
ALTER TABLE events ADD COLUMN IF NOT EXISTS story_position DECIMAL(3,2);
ALTER TABLE events ADD COLUMN IF NOT EXISTS conflict_core TEXT;
ALTER TABLE events ADD COLUMN IF NOT EXISTS dramatic_tension INTEGER;
ALTER TABLE events ADD COLUMN IF NOT EXISTS emotional_impact INTEGER;
ALTER TABLE events ADD COLUMN IF NOT EXISTS chapter_integration_points JSONB DEFAULT '[]'::jsonb;
ALTER TABLE events ADD COLUMN IF NOT EXISTS storyline_requirements JSONB DEFAULT '[]'::jsonb;

-- 2. 创建事件-章节映射表
CREATE TABLE IF NOT EXISTS event_chapter_mappings (
    id VARCHAR(36) PRIMARY KEY,
    event_id VARCHAR(50) NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    chapter_outline_id VARCHAR(50) NOT NULL REFERENCES chapter_outlines(id) ON DELETE CASCADE,
    integration_type VARCHAR(20) NOT NULL, -- 'driving', 'conflict', 'emotional', 'background'
    sequence_order INTEGER DEFAULT 0,
    integration_notes TEXT, -- 融入说明
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- 唯一约束：同一事件在同一章节中只能有一种融入类型
    UNIQUE(event_id, chapter_outline_id, integration_type)
);

-- 3. 创建索引
CREATE INDEX IF NOT EXISTS idx_event_chapter_mappings_event_id ON event_chapter_mappings(event_id);
CREATE INDEX IF NOT EXISTS idx_event_chapter_mappings_chapter_id ON event_chapter_mappings(chapter_outline_id);
CREATE INDEX IF NOT EXISTS idx_event_chapter_mappings_type ON event_chapter_mappings(integration_type);
CREATE INDEX IF NOT EXISTS idx_events_story_position ON events(story_position);
CREATE INDEX IF NOT EXISTS idx_events_conflict_core ON events(conflict_core);
CREATE INDEX IF NOT EXISTS idx_events_dramatic_tension ON events(dramatic_tension);
CREATE INDEX IF NOT EXISTS idx_events_emotional_impact ON events(emotional_impact);

-- 4. 添加注释
COMMENT ON TABLE event_chapter_mappings IS '事件-章节大纲映射表';
COMMENT ON COLUMN event_chapter_mappings.integration_type IS '融入类型：driving(推动)、conflict(冲突)、emotional(情感)、background(背景)';
COMMENT ON COLUMN event_chapter_mappings.sequence_order IS '在同一章节中的顺序';
COMMENT ON COLUMN event_chapter_mappings.integration_notes IS '融入说明';

COMMENT ON COLUMN events.story_position IS '在整体故事中的位置比例 (0-1)';
COMMENT ON COLUMN events.conflict_core IS '核心矛盾描述';
COMMENT ON COLUMN events.dramatic_tension IS '戏剧张力 (1-10)';
COMMENT ON COLUMN events.emotional_impact IS '情感冲击 (1-10)';
COMMENT ON COLUMN events.chapter_integration_points IS '章节融入点列表';
COMMENT ON COLUMN events.storyline_requirements IS '章节要求列表';

-- 5. 创建视图：事件与章节关联详情
CREATE OR REPLACE VIEW event_chapter_details AS
SELECT 
    e.id as event_id,
    e.title as event_title,
    e.description as event_description,
    e.event_type,
    e.importance,
    e.category,
    e.story_position,
    e.conflict_core,
    e.dramatic_tension,
    e.emotional_impact,
    e.plot_outline_id,
    co.id as chapter_outline_id,
    co.chapter_number,
    co.title as chapter_title,
    co.story_position as chapter_story_position,
    co.act_belonging,
    ecm.integration_type,
    ecm.sequence_order,
    ecm.integration_notes
FROM events e
LEFT JOIN event_chapter_mappings ecm ON e.id = ecm.event_id
LEFT JOIN chapter_outlines co ON ecm.chapter_outline_id = co.id
ORDER BY e.story_position, ecm.sequence_order;

-- 6. 创建函数：获取章节的相关事件
CREATE OR REPLACE FUNCTION get_chapter_events(chapter_id VARCHAR(50))
RETURNS JSONB AS $$
DECLARE
    result JSONB;
BEGIN
    SELECT jsonb_agg(
        jsonb_build_object(
            'event_id', e.id,
            'event_title', e.title,
            'event_description', e.description,
            'event_type', e.event_type,
            'importance', e.importance,
            'category', e.category,
            'story_position', e.story_position,
            'conflict_core', e.conflict_core,
            'dramatic_tension', e.dramatic_tension,
            'emotional_impact', e.emotional_impact,
            'integration_type', ecm.integration_type,
            'sequence_order', ecm.sequence_order,
            'integration_notes', ecm.integration_notes
        ) ORDER BY ecm.sequence_order
    ) INTO result
    FROM events e
    JOIN event_chapter_mappings ecm ON e.id = ecm.event_id
    WHERE ecm.chapter_outline_id = chapter_id;
    
    RETURN COALESCE(result, '[]'::jsonb);
END;
$$ LANGUAGE plpgsql;

-- 7. 创建函数：获取剧情大纲的所有事件（按重要性分组）
CREATE OR REPLACE FUNCTION get_plot_events_by_importance(plot_id VARCHAR(50))
RETURNS JSONB AS $$
DECLARE
    result JSONB;
BEGIN
    SELECT jsonb_build_object(
        'major_events', COALESCE(
            (SELECT jsonb_agg(row_to_json(e) ORDER BY e.story_position)
             FROM events e 
             WHERE e.plot_outline_id = plot_id AND e.importance = '重大事件'),
            '[]'::jsonb
        ),
        'important_events', COALESCE(
            (SELECT jsonb_agg(row_to_json(e) ORDER BY e.story_position)
             FROM events e 
             WHERE e.plot_outline_id = plot_id AND e.importance = '重要事件'),
            '[]'::jsonb
        ),
        'normal_events', COALESCE(
            (SELECT jsonb_agg(row_to_json(e) ORDER BY e.story_position)
             FROM events e 
             WHERE e.plot_outline_id = plot_id AND e.importance = '普通事件'),
            '[]'::jsonb
        ),
        'special_events', COALESCE(
            (SELECT jsonb_agg(row_to_json(e) ORDER BY e.story_position)
             FROM events e 
             WHERE e.plot_outline_id = plot_id AND e.importance = '特殊事件'),
            '[]'::jsonb
        )
    ) INTO result;
    
    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- 8. 创建函数：统计事件信息
CREATE OR REPLACE FUNCTION get_event_stats(plot_id VARCHAR(50))
RETURNS JSONB AS $$
DECLARE
    result JSONB;
BEGIN
    SELECT jsonb_build_object(
        'total_events', COUNT(*),
        'major_events_count', COUNT(*) FILTER (WHERE importance = '重大事件'),
        'important_events_count', COUNT(*) FILTER (WHERE importance = '重要事件'),
        'normal_events_count', COUNT(*) FILTER (WHERE importance = '普通事件'),
        'special_events_count', COUNT(*) FILTER (WHERE importance = '特殊事件'),
        'avg_dramatic_tension', COALESCE(AVG(dramatic_tension), 0),
        'avg_emotional_impact', COALESCE(AVG(emotional_impact), 0),
        'events_with_chapters', COUNT(*) FILTER (WHERE chapter_number IS NOT NULL),
        'events_without_chapters', COUNT(*) FILTER (WHERE chapter_number IS NULL)
    ) INTO result
    FROM events
    WHERE plot_outline_id = plot_id;
    
    RETURN result;
END;
$$ LANGUAGE plpgsql;
