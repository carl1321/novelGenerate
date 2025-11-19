-- 章节大纲字段统一化迁移脚本
-- 创建时间: 2025-01-02
-- 目的: 添加与剧情大纲一致的字段，实现字段统一化

-- 1. 添加与剧情大纲一致的字段
ALTER TABLE chapter_outlines 
ADD COLUMN IF NOT EXISTS story_tone VARCHAR(50),
ADD COLUMN IF NOT EXISTS narrative_structure VARCHAR(50),
ADD COLUMN IF NOT EXISTS story_structure VARCHAR(50),
ADD COLUMN IF NOT EXISTS worldview_elements JSONB DEFAULT '[]'::jsonb;

-- 2. 添加注释说明字段用途
COMMENT ON COLUMN chapter_outlines.story_tone IS '故事基调 - 与剧情大纲一致';
COMMENT ON COLUMN chapter_outlines.narrative_structure IS '叙事结构 - 与剧情大纲一致';
COMMENT ON COLUMN chapter_outlines.story_structure IS '故事结构 - 与剧情大纲一致';
COMMENT ON COLUMN chapter_outlines.worldview_elements IS '世界观元素 - 与剧情大纲一致';

-- 3. 创建索引以提高查询性能
CREATE INDEX IF NOT EXISTS idx_chapter_outlines_story_tone ON chapter_outlines(story_tone);
CREATE INDEX IF NOT EXISTS idx_chapter_outlines_narrative_structure ON chapter_outlines(narrative_structure);
CREATE INDEX IF NOT EXISTS idx_chapter_outlines_story_structure ON chapter_outlines(story_structure);

-- 4. 创建GIN索引用于JSONB字段查询
CREATE INDEX IF NOT EXISTS idx_chapter_outlines_worldview_elements ON chapter_outlines USING GIN (worldview_elements);

-- 5. 更新现有数据的字段值（从关联的剧情大纲获取）
-- 注意：这里需要根据实际的剧情大纲数据来更新
-- 暂时设置为默认值，后续通过应用程序逻辑来填充

UPDATE chapter_outlines 
SET 
    story_tone = COALESCE(story_tone, '热血'),
    narrative_structure = COALESCE(narrative_structure, '线性叙事'),
    story_structure = COALESCE(story_structure, '三幕式'),
    worldview_elements = COALESCE(worldview_elements, '[]'::jsonb)
WHERE 
    story_tone IS NULL 
    OR narrative_structure IS NULL 
    OR story_structure IS NULL 
    OR worldview_elements IS NULL;

-- 6. 添加约束确保字段不为空
ALTER TABLE chapter_outlines 
ALTER COLUMN story_tone SET NOT NULL,
ALTER COLUMN narrative_structure SET NOT NULL,
ALTER COLUMN story_structure SET NOT NULL;

-- 7. 创建视图用于查询章节大纲的完整信息
CREATE OR REPLACE VIEW chapter_outline_unified AS
SELECT 
    co.id,
    co.plot_outline_id,
    co.chapter_number,
    co.title,
    
    -- 与剧情大纲一致的字段
    co.story_tone,
    co.narrative_structure,
    co.story_structure,
    co.worldview_elements,
    
    -- 章节定位
    co.story_position,
    co.act_belonging,
    
    -- 章节内容
    co.chapter_summary,
    co.character_appearances,
    
    -- 剧情功能
    co.plot_function,
    co.conflict_development,
    co.character_development,
    
    -- 写作指导
    co.writing_notes,
    co.foreshadowing,
    co.callbacks,
    
    -- 情感和氛围
    co.emotional_tone,
    co.atmosphere,
    co.tension_level,
    
    -- 元数据
    co.estimated_word_count,
    co.estimated_reading_time,
    co.status,
    co.created_at,
    co.updated_at,
    
    -- 关联的剧情大纲信息
    po.title as plot_title,
    po.description as plot_description,
    po.worldview_id,
    po.target_word_count as plot_target_word_count,
    po.estimated_chapters as plot_estimated_chapters
    
FROM chapter_outlines co
LEFT JOIN plot_outlines po ON co.plot_outline_id = po.id;

-- 8. 创建函数用于从剧情大纲同步字段到章节大纲
CREATE OR REPLACE FUNCTION sync_chapter_outline_fields()
RETURNS TRIGGER AS $$
BEGIN
    -- 当剧情大纲更新时，同步更新相关章节大纲的字段
    UPDATE chapter_outlines 
    SET 
        story_tone = NEW.story_tone,
        narrative_structure = NEW.narrative_structure,
        story_structure = NEW.story_structure,
        updated_at = CURRENT_TIMESTAMP
    WHERE plot_outline_id = NEW.id;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 9. 创建触发器自动同步字段
DROP TRIGGER IF EXISTS trigger_sync_chapter_outline_fields ON plot_outlines;
CREATE TRIGGER trigger_sync_chapter_outline_fields
    AFTER UPDATE ON plot_outlines
    FOR EACH ROW
    EXECUTE FUNCTION sync_chapter_outline_fields();

-- 10. 验证迁移结果
DO $$
BEGIN
    -- 检查新字段是否添加成功
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'chapter_outlines' 
        AND column_name = 'story_tone'
    ) THEN
        RAISE EXCEPTION '字段 story_tone 添加失败';
    END IF;
    
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'chapter_outlines' 
        AND column_name = 'narrative_structure'
    ) THEN
        RAISE EXCEPTION '字段 narrative_structure 添加失败';
    END IF;
    
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'chapter_outlines' 
        AND column_name = 'story_structure'
    ) THEN
        RAISE EXCEPTION '字段 story_structure 添加失败';
    END IF;
    
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'chapter_outlines' 
        AND column_name = 'worldview_elements'
    ) THEN
        RAISE EXCEPTION '字段 worldview_elements 添加失败';
    END IF;
    
    RAISE NOTICE '章节大纲字段统一化迁移完成！';
END $$;
