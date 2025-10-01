-- 剧情大纲数据库表设计
-- 创建时间: 2025-10-01

-- 1. 剧情大纲主表
CREATE TABLE IF NOT EXISTS plot_outlines (
    id VARCHAR(50) PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    
    -- 关联信息
    worldview_id VARCHAR(50) NOT NULL,
    character_ids JSONB DEFAULT '[]'::jsonb,
    
    -- 剧情结构
    structure_type VARCHAR(20) DEFAULT '三幕式',
    total_chapters INTEGER DEFAULT 20,
    target_word_count INTEGER DEFAULT 100000,
    
    -- 剧情内容
    main_conflict TEXT NOT NULL,
    theme TEXT NOT NULL,
    tone VARCHAR(50) NOT NULL,
    
    -- 角色发展
    character_arcs JSONB DEFAULT '{}'::jsonb,
    
    -- 元数据
    status VARCHAR(20) DEFAULT '草稿',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50)
);

-- 2. 章节大纲表
CREATE TABLE IF NOT EXISTS chapter_outlines (
    id VARCHAR(50) PRIMARY KEY,
    plot_outline_id VARCHAR(50) NOT NULL REFERENCES plot_outlines(id) ON DELETE CASCADE,
    chapter_number INTEGER NOT NULL,
    title VARCHAR(200) NOT NULL,
    
    -- 章节内容
    summary TEXT NOT NULL,
    main_events JSONB DEFAULT '[]'::jsonb,
    key_scenes JSONB DEFAULT '[]'::jsonb,
    
    -- 角色参与
    participating_characters JSONB DEFAULT '[]'::jsonb,
    character_development JSONB DEFAULT '{}'::jsonb,
    
    -- 剧情推进
    conflict_escalation TEXT NOT NULL,
    plot_advancement TEXT NOT NULL,
    foreshadowing JSONB DEFAULT '[]'::jsonb,
    
    -- 元数据
    estimated_word_count INTEGER DEFAULT 5000,
    estimated_reading_time INTEGER DEFAULT 20,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- 唯一约束
    UNIQUE(plot_outline_id, chapter_number)
);

-- 3. 创建索引
CREATE INDEX IF NOT EXISTS idx_plot_outlines_worldview_id ON plot_outlines(worldview_id);
CREATE INDEX IF NOT EXISTS idx_plot_outlines_status ON plot_outlines(status);
CREATE INDEX IF NOT EXISTS idx_plot_outlines_created_at ON plot_outlines(created_at);
CREATE INDEX IF NOT EXISTS idx_chapter_outlines_plot_id ON chapter_outlines(plot_outline_id);
CREATE INDEX IF NOT EXISTS idx_chapter_outlines_number ON chapter_outlines(plot_outline_id, chapter_number);

-- 4. 创建更新时间触发器
CREATE OR REPLACE FUNCTION update_plot_outline_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_plot_outline_updated_at
    BEFORE UPDATE ON plot_outlines
    FOR EACH ROW
    EXECUTE FUNCTION update_plot_outline_updated_at();

-- 5. 插入示例数据
INSERT INTO plot_outlines (
    id, title, description, worldview_id, character_ids,
    structure_type, total_chapters, target_word_count,
    main_conflict, theme, tone, status, created_by
) VALUES (
    'plot_example_001',
    '修仙传奇',
    '一个关于修仙者成长的故事',
    'world_490231911657504838',
    '["char_001", "char_002"]'::jsonb,
    '三幕式',
    20,
    100000,
    '主角与邪恶势力的斗争',
    '正义与邪恶的较量',
    '热血',
    '草稿',
    'system'
) ON CONFLICT (id) DO NOTHING;

INSERT INTO chapter_outlines (
    id, plot_outline_id, chapter_number, title,
    summary, main_events, key_scenes,
    participating_characters, character_development,
    conflict_escalation, plot_advancement, foreshadowing,
    estimated_word_count
) VALUES (
    'chapter_example_001',
    'plot_example_001',
    1,
    '初入修仙界',
    '主角初次接触修仙世界，开始修炼之路',
    '["初遇师父", "开始修炼"]'::jsonb,
    '["修炼场景", "师父指导"]'::jsonb,
    '["主角", "师父"]'::jsonb,
    '{"主角": "开始修炼，了解修仙世界"}'::jsonb,
    '主角发现自己的修炼天赋',
    '建立世界观，介绍主要角色',
    '["神秘功法", "未来敌人"]'::jsonb,
    5000
) ON CONFLICT (id) DO NOTHING;

-- 6. 创建视图：剧情大纲详情
CREATE OR REPLACE VIEW plot_outline_details AS
SELECT 
    po.id,
    po.title,
    po.description,
    po.worldview_id,
    po.character_ids,
    po.structure_type,
    po.total_chapters,
    po.target_word_count,
    po.main_conflict,
    po.theme,
    po.tone,
    po.character_arcs,
    po.status,
    po.created_at,
    po.updated_at,
    po.created_by,
    COUNT(co.id) as actual_chapters,
    COALESCE(SUM(co.estimated_word_count), 0) as total_estimated_words
FROM plot_outlines po
LEFT JOIN chapter_outlines co ON po.id = co.plot_outline_id
GROUP BY po.id;

-- 7. 创建函数：获取剧情大纲的完整信息
CREATE OR REPLACE FUNCTION get_plot_outline_with_chapters(plot_id VARCHAR(50))
RETURNS JSONB AS $$
DECLARE
    result JSONB;
BEGIN
    SELECT jsonb_build_object(
        'plot_outline', row_to_json(po),
        'chapters', COALESCE(
            (SELECT jsonb_agg(row_to_json(co) ORDER BY co.chapter_number)
             FROM chapter_outlines co 
             WHERE co.plot_outline_id = plot_id),
            '[]'::jsonb
        )
    ) INTO result
    FROM plot_outlines po
    WHERE po.id = plot_id;
    
    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- 8. 创建函数：统计剧情大纲信息
CREATE OR REPLACE FUNCTION get_plot_outline_stats()
RETURNS JSONB AS $$
DECLARE
    result JSONB;
BEGIN
    SELECT jsonb_build_object(
        'total_plots', COUNT(*),
        'draft_plots', COUNT(*) FILTER (WHERE status = '草稿'),
        'planning_plots', COUNT(*) FILTER (WHERE status = '规划中'),
        'writing_plots', COUNT(*) FILTER (WHERE status = '写作中'),
        'completed_plots', COUNT(*) FILTER (WHERE status = '已完成'),
        'total_chapters', COALESCE(SUM(total_chapters), 0),
        'total_target_words', COALESCE(SUM(target_word_count), 0)
    ) INTO result
    FROM plot_outlines;
    
    RETURN result;
END;
$$ LANGUAGE plpgsql;
