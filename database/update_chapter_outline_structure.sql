-- 更新章节大纲表结构以匹配简化的模型
-- 创建时间: 2025-01-08

-- 1. 删除依赖的视图和函数
DROP VIEW IF EXISTS chapter_outline_details CASCADE;
DROP FUNCTION IF EXISTS get_chapter_outline_with_details(VARCHAR(50)) CASCADE;
DROP FUNCTION IF EXISTS get_plot_outline_chapters(VARCHAR(50)) CASCADE;
DROP FUNCTION IF EXISTS get_chapter_outline_stats(VARCHAR(50)) CASCADE;

-- 2. 删除不需要的列
ALTER TABLE chapter_outlines DROP COLUMN IF EXISTS story_tone;
ALTER TABLE chapter_outlines DROP COLUMN IF EXISTS narrative_structure;
ALTER TABLE chapter_outlines DROP COLUMN IF EXISTS story_structure;
ALTER TABLE chapter_outlines DROP COLUMN IF EXISTS foreshadowing;
ALTER TABLE chapter_outlines DROP COLUMN IF EXISTS callbacks;
ALTER TABLE chapter_outlines DROP COLUMN IF EXISTS estimated_reading_time;
ALTER TABLE chapter_outlines DROP COLUMN IF EXISTS main_events;
ALTER TABLE chapter_outlines DROP COLUMN IF EXISTS event_development;
ALTER TABLE chapter_outlines DROP COLUMN IF EXISTS driving_events;
ALTER TABLE chapter_outlines DROP COLUMN IF EXISTS conflict_sources;
ALTER TABLE chapter_outlines DROP COLUMN IF EXISTS emotional_triggers;
ALTER TABLE chapter_outlines DROP COLUMN IF EXISTS event_mappings;

-- 3. 更新场景表结构
ALTER TABLE scenes DROP COLUMN IF EXISTS scene_type;
ALTER TABLE scenes DROP COLUMN IF EXISTS time_period;
ALTER TABLE scenes DROP COLUMN IF EXISTS key_dialogue;
ALTER TABLE scenes DROP COLUMN IF EXISTS emotional_tone;
ALTER TABLE scenes DROP COLUMN IF EXISTS estimated_word_count;

-- 4. 重新创建视图
CREATE OR REPLACE VIEW chapter_outline_details AS
SELECT 
    co.id,
    co.plot_outline_id,
    co.chapter_number,
    co.title,
    co.story_position,
    co.act_belonging,
    co.chapter_summary,
    co.character_appearances,
    co.plot_function,
    co.conflict_development,
    co.character_development,
    co.writing_notes,
    co.emotional_tone,
    co.atmosphere,
    co.tension_level,
    co.worldview_elements,
    co.estimated_word_count,
    co.status,
    co.created_at,
    co.updated_at,
    COUNT(s.id) as scenes_count,
    COUNT(cd.id) as character_developments_count,
    COUNT(ei.id) as event_integrations_count
FROM chapter_outlines co
LEFT JOIN scenes s ON co.id = s.chapter_outline_id
LEFT JOIN character_developments cd ON co.id = cd.chapter_outline_id
LEFT JOIN event_integrations ei ON co.id = ei.chapter_outline_id
GROUP BY co.id;

-- 5. 重新创建函数
CREATE OR REPLACE FUNCTION get_chapter_outline_with_details(chapter_id VARCHAR(50))
RETURNS JSONB AS $$
DECLARE
    result JSONB;
BEGIN
    SELECT jsonb_build_object(
        'chapter_outline', row_to_json(co),
        'scenes', COALESCE(
            (SELECT jsonb_agg(row_to_json(s) ORDER BY s.scene_number)
             FROM scenes s 
             WHERE s.chapter_outline_id = chapter_id),
            '[]'::jsonb
        ),
        'character_developments', COALESCE(
            (SELECT jsonb_agg(row_to_json(cd))
             FROM character_developments cd 
             WHERE cd.chapter_outline_id = chapter_id),
            '[]'::jsonb
        ),
        'event_integrations', COALESCE(
            (SELECT jsonb_agg(row_to_json(ei))
             FROM event_integrations ei 
             WHERE ei.chapter_outline_id = chapter_id),
            '[]'::jsonb
        )
    ) INTO result
    FROM chapter_outlines co
    WHERE co.id = chapter_id;
    
    RETURN result;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_plot_outline_chapters(plot_id VARCHAR(50))
RETURNS JSONB AS $$
DECLARE
    result JSONB;
BEGIN
    SELECT jsonb_agg(
        jsonb_build_object(
            'chapter_outline', row_to_json(co),
            'scenes', COALESCE(
                (SELECT jsonb_agg(row_to_json(s) ORDER BY s.scene_number)
                 FROM scenes s 
                 WHERE s.chapter_outline_id = co.id),
                '[]'::jsonb
            ),
            'character_developments', COALESCE(
                (SELECT jsonb_agg(row_to_json(cd))
                 FROM character_developments cd 
                 WHERE cd.chapter_outline_id = co.id),
                '[]'::jsonb
            ),
            'event_integrations', COALESCE(
                (SELECT jsonb_agg(row_to_json(ei))
                 FROM event_integrations ei 
                 WHERE ei.chapter_outline_id = co.id),
                '[]'::jsonb
            )
        ) ORDER BY co.chapter_number
    ) INTO result
    FROM chapter_outlines co
    WHERE co.plot_outline_id = plot_id;
    
    RETURN COALESCE(result, '[]'::jsonb);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_chapter_outline_stats(plot_id VARCHAR(50))
RETURNS JSONB AS $$
DECLARE
    result JSONB;
BEGIN
    SELECT jsonb_build_object(
        'total_chapters', COUNT(*),
        'outline_chapters', COUNT(*) FILTER (WHERE status = '大纲'),
        'draft_chapters', COUNT(*) FILTER (WHERE status = '草稿'),
        'completed_chapters', COUNT(*) FILTER (WHERE status = '已完成'),
        'total_estimated_words', COALESCE(SUM(estimated_word_count), 0),
        'avg_words_per_chapter', COALESCE(AVG(estimated_word_count), 0),
        'total_scenes', COALESCE(
            (SELECT COUNT(*) FROM scenes s 
             JOIN chapter_outlines co ON s.chapter_outline_id = co.id 
             WHERE co.plot_outline_id = plot_id), 0
        ),
        'total_event_integrations', COALESCE(
            (SELECT COUNT(*) FROM event_integrations ei 
             JOIN chapter_outlines co ON ei.chapter_outline_id = co.id 
             WHERE co.plot_outline_id = plot_id), 0
        )
    ) INTO result
    FROM chapter_outlines
    WHERE plot_outline_id = plot_id;
    
    RETURN result;
END;
$$ LANGUAGE plpgsql;
