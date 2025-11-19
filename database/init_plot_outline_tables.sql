-- 剧情大纲数据库表设计 - 完整的剧情大纲设计
-- 创建时间: 2025-10-02

-- 1. 剧情大纲主表 (完整设计)
CREATE TABLE IF NOT EXISTS plot_outlines (
    id VARCHAR(50) PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    
    -- 关联信息
    worldview_id VARCHAR(50) NOT NULL,
    
    -- 剧情大纲要求
    story_tone VARCHAR(50) NOT NULL,
    narrative_structure VARCHAR(50) NOT NULL,
    story_structure VARCHAR(50) NOT NULL,
    target_word_count INTEGER DEFAULT 100000,
    estimated_chapters INTEGER DEFAULT 20,
    
    -- 简化的剧情大纲结构
    story_framework JSONB NOT NULL,
    character_positions JSONB DEFAULT '{}'::jsonb,
    plot_blocks JSONB DEFAULT '[]'::jsonb,
    story_flow JSONB NOT NULL,
    
    -- 元数据
    status VARCHAR(20) DEFAULT '草稿',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50)
);

-- 2. 关键情节点表
CREATE TABLE IF NOT EXISTS plot_points (
    id VARCHAR(50) PRIMARY KEY,
    plot_outline_id VARCHAR(50) NOT NULL REFERENCES plot_outlines(id) ON DELETE CASCADE,
    point_type VARCHAR(50) NOT NULL,  -- 'inciting_incident', 'first_turning_point', 'midpoint', 'second_turning_point', 'climax', 'resolution'
    position DECIMAL(3,2) NOT NULL,   -- 在故事中的位置比例 (0.0-1.0)
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    emotional_impact VARCHAR(50),    -- 'tension', 'relief', 'shock', 'satisfaction'
    character_involvement JSONB DEFAULT '[]'::jsonb,
    plot_function VARCHAR(50),       -- 剧情功能
    foreshadowing JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. 幕次表
CREATE TABLE IF NOT EXISTS acts (
    id VARCHAR(50) PRIMARY KEY,
    plot_outline_id VARCHAR(50) NOT NULL REFERENCES plot_outlines(id) ON DELETE CASCADE,
    act_number INTEGER NOT NULL,
    act_name VARCHAR(100) NOT NULL,
    start_position DECIMAL(3,2) NOT NULL,
    end_position DECIMAL(3,2) NOT NULL,
    purpose TEXT NOT NULL,
    key_events JSONB DEFAULT '[]'::jsonb,
    emotional_tone VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- 唯一约束
    UNIQUE(plot_outline_id, act_number)
);

-- 4. 转折点表
CREATE TABLE IF NOT EXISTS turning_points (
    id VARCHAR(50) PRIMARY KEY,
    plot_outline_id VARCHAR(50) NOT NULL REFERENCES plot_outlines(id) ON DELETE CASCADE,
    point_type VARCHAR(50) NOT NULL,
    position DECIMAL(3,2) NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    impact TEXT NOT NULL,
    character_involvement JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. 故事弧线节点表
CREATE TABLE IF NOT EXISTS story_arc_points (
    id VARCHAR(50) PRIMARY KEY,
    plot_outline_id VARCHAR(50) NOT NULL REFERENCES plot_outlines(id) ON DELETE CASCADE,
    arc_type VARCHAR(50) NOT NULL,  -- 'beginning', 'development', 'climax', 'falling_action', 'resolution'
    position DECIMAL(3,2) NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    emotional_state VARCHAR(50) NOT NULL,
    character_growth TEXT,
    plot_advancement TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. 创建索引
CREATE INDEX IF NOT EXISTS idx_plot_outlines_worldview_id ON plot_outlines(worldview_id);
CREATE INDEX IF NOT EXISTS idx_plot_outlines_status ON plot_outlines(status);
CREATE INDEX IF NOT EXISTS idx_plot_outlines_created_at ON plot_outlines(created_at);
CREATE INDEX IF NOT EXISTS idx_plot_points_plot_id ON plot_points(plot_outline_id);
CREATE INDEX IF NOT EXISTS idx_plot_points_position ON plot_points(plot_outline_id, position);
CREATE INDEX IF NOT EXISTS idx_acts_plot_id ON acts(plot_outline_id);
CREATE INDEX IF NOT EXISTS idx_turning_points_plot_id ON turning_points(plot_outline_id);
CREATE INDEX IF NOT EXISTS idx_story_arc_points_plot_id ON story_arc_points(plot_outline_id);

-- 7. 创建更新时间触发器
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

-- 8. 插入示例数据
INSERT INTO plot_outlines (
    id, title, description, worldview_id, story_tone, narrative_structure, story_structure,
    story_framework, character_positions, plot_blocks, story_flow,
    target_word_count, estimated_chapters, status, created_by
) VALUES (
    'plot_example_001',
    '修仙传奇：灵枢觉醒',
    '一个关于修仙者成长的故事，主角在灵枢世界中觉醒，面对正邪之争',
    'world_490231911657504838',
    '热血',
    '线性叙事',
    '三幕式',
    '{"structure_type": "三幕式", "acts": [], "turning_points": [], "climax_position": 0.8, "resolution_position": 0.9, "narrative_style": "线性叙事"}'::jsonb,
    '{"主角": {"position": "故事中心", "function": "推动剧情发展", "development_arc": "从普通人到修仙者", "worldview_connection": "灵枢修炼体系", "key_moments": ["觉醒", "修炼", "成长"]}}'::jsonb,
    '[{"plot_name": "觉醒篇", "description": "主角觉醒灵枢能力", "participating_characters": ["主角"], "worldview_elements": ["灵枢"], "emotional_tone": "震惊", "plot_function": "故事开端", "estimated_chapters": 5, "estimated_words": 25000, "key_events": ["觉醒", "初遇导师"], "foreshadowing": ["神秘力量"]}]'::jsonb,
    '{"overall_direction": "从普通人到修仙者的成长历程", "thematic_progression": "正义与邪恶的较量", "character_arcs": {"主角": "从普通人到修仙者的成长历程"}, "worldview_evolution": "灵枢世界的逐步展现", "conflict_progression": "从个人成长到正邪之争", "emotional_journey": "震惊→困惑→决心→挫折→成长→胜利→满足"}'::jsonb,
    100000,
    20,
    '草稿',
    'system'
) ON CONFLICT (id) DO NOTHING;

-- 9. 创建视图：剧情大纲详情
CREATE OR REPLACE VIEW plot_outline_details AS
SELECT 
    po.id,
    po.title,
    po.description,
    po.worldview_id,
    po.story_tone,
    po.narrative_structure,
    po.story_structure,
    po.story_framework,
    po.character_positions,
    po.plot_blocks,
    po.story_flow,
    po.target_word_count,
    po.estimated_chapters,
    po.status,
    po.created_at,
    po.updated_at,
    po.created_by,
    COUNT(pp.id) as plot_points_count,
    COUNT(a.id) as acts_count,
    COUNT(tp.id) as turning_points_count
FROM plot_outlines po
LEFT JOIN plot_points pp ON po.id = pp.plot_outline_id
LEFT JOIN acts a ON po.id = a.plot_outline_id
LEFT JOIN turning_points tp ON po.id = tp.plot_outline_id
GROUP BY po.id;

-- 10. 创建函数：获取剧情大纲的完整信息
CREATE OR REPLACE FUNCTION get_plot_outline_with_details(plot_id VARCHAR(50))
RETURNS JSONB AS $$
DECLARE
    result JSONB;
BEGIN
    SELECT jsonb_build_object(
        'plot_outline', row_to_json(po),
        'plot_points', COALESCE(
            (SELECT jsonb_agg(row_to_json(pp) ORDER BY pp.position)
             FROM plot_points pp 
             WHERE pp.plot_outline_id = plot_id),
            '[]'::jsonb
        ),
        'acts', COALESCE(
            (SELECT jsonb_agg(row_to_json(a) ORDER BY a.act_number)
             FROM acts a 
             WHERE a.plot_outline_id = plot_id),
            '[]'::jsonb
        ),
        'turning_points', COALESCE(
            (SELECT jsonb_agg(row_to_json(tp) ORDER BY tp.position)
             FROM turning_points tp 
             WHERE tp.plot_outline_id = plot_id),
            '[]'::jsonb
        ),
        'story_arc_points', COALESCE(
            (SELECT jsonb_agg(row_to_json(sap) ORDER BY sap.position)
             FROM story_arc_points sap 
             WHERE sap.plot_outline_id = plot_id),
            '[]'::jsonb
        )
    ) INTO result
    FROM plot_outlines po
    WHERE po.id = plot_id;
    
    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- 11. 创建函数：统计剧情大纲信息
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
        'total_estimated_chapters', COALESCE(SUM(estimated_chapters), 0),
        'total_target_words', COALESCE(SUM(target_word_count), 0),
        'avg_word_count', COALESCE(AVG(target_word_count), 0),
        'avg_chapters', COALESCE(AVG(estimated_chapters), 0)
    ) INTO result
    FROM plot_outlines;
    
    RETURN result;
END;
$$ LANGUAGE plpgsql;
