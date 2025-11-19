-- 章节大纲字段同步脚本
-- 创建时间: 2025-01-02
-- 目的: 将现有剧情大纲的字段同步到章节大纲

-- 1. 创建函数：从剧情大纲同步字段到章节大纲
CREATE OR REPLACE FUNCTION sync_chapter_outline_fields_from_plot()
RETURNS INTEGER AS $$
DECLARE
    updated_count INTEGER := 0;
    plot_record RECORD;
    chapter_record RECORD;
BEGIN
    -- 遍历所有剧情大纲
    FOR plot_record IN 
        SELECT id, story_tone, narrative_structure, story_structure 
        FROM plot_outlines 
        WHERE story_tone IS NOT NULL 
        AND narrative_structure IS NOT NULL 
        AND story_structure IS NOT NULL
    LOOP
        -- 更新该剧情大纲下的所有章节大纲
        UPDATE chapter_outlines 
        SET 
            story_tone = plot_record.story_tone,
            narrative_structure = plot_record.narrative_structure,
            story_structure = plot_record.story_structure,
            updated_at = CURRENT_TIMESTAMP
        WHERE plot_outline_id = plot_record.id
        AND (
            story_tone IS NULL 
            OR narrative_structure IS NULL 
            OR story_structure IS NULL
            OR story_tone != plot_record.story_tone
            OR narrative_structure != plot_record.narrative_structure
            OR story_structure != plot_record.story_structure
        );
        
        GET DIAGNOSTICS updated_count = ROW_COUNT;
        
        RAISE NOTICE '剧情大纲 % 同步了 % 个章节大纲', plot_record.id, updated_count;
    END LOOP;
    
    RETURN updated_count;
END;
$$ LANGUAGE plpgsql;

-- 2. 创建函数：从剧情大纲的幕次信息提取世界观元素
CREATE OR REPLACE FUNCTION extract_worldview_elements_from_acts()
RETURNS INTEGER AS $$
DECLARE
    updated_count INTEGER := 0;
    plot_record RECORD;
    act_data JSONB;
    worldview_elements JSONB;
    chapter_record RECORD;
BEGIN
    -- 遍历所有剧情大纲
    FOR plot_record IN 
        SELECT id, story_framework 
        FROM plot_outlines 
        WHERE story_framework IS NOT NULL
    LOOP
        -- 提取世界观元素
        worldview_elements := '[]'::jsonb;
        
        -- 从幕次中提取世界观元素
        FOR act_data IN 
            SELECT jsonb_array_elements(plot_record.story_framework->'acts')
        LOOP
            IF act_data ? 'worldview_elements' THEN
                worldview_elements := worldview_elements || (act_data->'worldview_elements');
            END IF;
        END LOOP;
        
        -- 去重
        SELECT jsonb_agg(DISTINCT value) 
        INTO worldview_elements
        FROM jsonb_array_elements(worldview_elements);
        
        -- 更新该剧情大纲下的所有章节大纲
        UPDATE chapter_outlines 
        SET 
            worldview_elements = worldview_elements,
            updated_at = CURRENT_TIMESTAMP
        WHERE plot_outline_id = plot_record.id
        AND (
            chapter_outlines.worldview_elements IS NULL 
            OR chapter_outlines.worldview_elements = '[]'::jsonb
        );
        
        GET DIAGNOSTICS updated_count = ROW_COUNT;
        
        RAISE NOTICE '剧情大纲 % 提取了世界观元素，更新了 % 个章节大纲', plot_record.id, updated_count;
    END LOOP;
    
    RETURN updated_count;
END;
$$ LANGUAGE plpgsql;

-- 3. 创建函数：验证字段同步结果
CREATE OR REPLACE FUNCTION validate_chapter_outline_sync()
RETURNS TABLE(
    plot_id VARCHAR(50),
    plot_title VARCHAR(200),
    total_chapters INTEGER,
    synced_chapters INTEGER,
    unsynced_chapters INTEGER,
    sync_status TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        po.id as plot_id,
        po.title as plot_title,
        COUNT(co.id)::INTEGER as total_chapters,
        COUNT(CASE 
            WHEN co.story_tone = po.story_tone 
            AND co.narrative_structure = po.narrative_structure 
            AND co.story_structure = po.story_structure 
            THEN 1 
        END)::INTEGER as synced_chapters,
        COUNT(CASE 
            WHEN co.story_tone != po.story_tone 
            OR co.narrative_structure != po.narrative_structure 
            OR co.story_structure != po.story_structure 
            THEN 1 
        END)::INTEGER as unsynced_chapters,
        CASE 
            WHEN COUNT(co.id) = 0 THEN '无章节大纲'
            WHEN COUNT(CASE 
                WHEN co.story_tone != po.story_tone 
                OR co.narrative_structure != po.narrative_structure 
                OR co.story_structure != po.story_structure 
                THEN 1 
            END) = 0 THEN '完全同步'
            ELSE '部分同步'
        END as sync_status
    FROM plot_outlines po
    LEFT JOIN chapter_outlines co ON po.id = co.plot_outline_id
    GROUP BY po.id, po.title, po.story_tone, po.narrative_structure, po.story_structure
    ORDER BY po.title;
END;
$$ LANGUAGE plpgsql;

-- 4. 执行字段同步
DO $$
DECLARE
    sync_result INTEGER;
    worldview_result INTEGER;
BEGIN
    RAISE NOTICE '开始同步章节大纲字段...';
    
    -- 同步基础字段
    SELECT sync_chapter_outline_fields_from_plot() INTO sync_result;
    RAISE NOTICE '基础字段同步完成，更新了 % 个章节大纲', sync_result;
    
    -- 提取世界观元素
    SELECT extract_worldview_elements_from_acts() INTO worldview_result;
    RAISE NOTICE '世界观元素提取完成，更新了 % 个章节大纲', worldview_result;
    
    RAISE NOTICE '字段同步完成！';
END $$;

-- 5. 显示同步结果
SELECT * FROM validate_chapter_outline_sync();

-- 6. 创建清理函数（可选）
CREATE OR REPLACE FUNCTION cleanup_sync_functions()
RETURNS VOID AS $$
BEGIN
    DROP FUNCTION IF EXISTS sync_chapter_outline_fields_from_plot();
    DROP FUNCTION IF EXISTS extract_worldview_elements_from_acts();
    DROP FUNCTION IF EXISTS validate_chapter_outline_sync();
    RAISE NOTICE '同步函数已清理';
END;
$$ LANGUAGE plpgsql;

-- 7. 显示最终统计
DO $$
DECLARE
    total_plots INTEGER;
    total_chapters INTEGER;
    synced_chapters INTEGER;
BEGIN
    SELECT COUNT(*) INTO total_plots FROM plot_outlines;
    SELECT COUNT(*) INTO total_chapters FROM chapter_outlines;
    SELECT COUNT(*) INTO synced_chapters 
    FROM chapter_outlines co
    JOIN plot_outlines po ON co.plot_outline_id = po.id
    WHERE co.story_tone = po.story_tone 
    AND co.narrative_structure = po.narrative_structure 
    AND co.story_structure = po.story_structure;
    
    RAISE NOTICE '=== 同步完成统计 ===';
    RAISE NOTICE '剧情大纲总数: %', total_plots;
    RAISE NOTICE '章节大纲总数: %', total_chapters;
    RAISE NOTICE '已同步章节: %', synced_chapters;
    RAISE NOTICE '同步率: %', CASE WHEN total_chapters > 0 THEN ROUND(synced_chapters::DECIMAL / total_chapters * 100, 2) ELSE 0 END || '%';
END $$;
