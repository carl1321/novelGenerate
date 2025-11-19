-- 简化的章节大纲字段同步脚本
-- 创建时间: 2025-01-02
-- 目的: 将现有剧情大纲的字段同步到章节大纲

-- 1. 同步基础字段
UPDATE chapter_outlines 
SET 
    story_tone = po.story_tone,
    narrative_structure = po.narrative_structure,
    story_structure = po.story_structure,
    updated_at = CURRENT_TIMESTAMP
FROM plot_outlines po
WHERE chapter_outlines.plot_outline_id = po.id
AND (
    chapter_outlines.story_tone IS NULL 
    OR chapter_outlines.narrative_structure IS NULL 
    OR chapter_outlines.story_structure IS NULL
    OR chapter_outlines.story_tone != po.story_tone
    OR chapter_outlines.narrative_structure != po.narrative_structure
    OR chapter_outlines.story_structure != po.story_structure
);

-- 2. 显示同步结果
SELECT 
    po.id as plot_id,
    po.title as plot_title,
    COUNT(co.id) as total_chapters,
    COUNT(CASE 
        WHEN co.story_tone = po.story_tone 
        AND co.narrative_structure = po.narrative_structure 
        AND co.story_structure = po.story_structure 
        THEN 1 
    END) as synced_chapters,
    COUNT(CASE 
        WHEN co.story_tone != po.story_tone 
        OR co.narrative_structure != po.narrative_structure 
        OR co.story_structure != po.story_structure 
        THEN 1 
    END) as unsynced_chapters
FROM plot_outlines po
LEFT JOIN chapter_outlines co ON po.id = co.plot_outline_id
GROUP BY po.id, po.title, po.story_tone, po.narrative_structure, po.story_structure
ORDER BY po.title;

-- 3. 显示最终统计
SELECT 
    COUNT(*) as total_plots,
    (SELECT COUNT(*) FROM chapter_outlines) as total_chapters,
    COUNT(CASE 
        WHEN co.story_tone = po.story_tone 
        AND co.narrative_structure = po.narrative_structure 
        AND co.story_structure = po.story_structure 
        THEN 1 
    END) as synced_chapters
FROM plot_outlines po
LEFT JOIN chapter_outlines co ON po.id = co.plot_outline_id;
