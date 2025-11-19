-- 章节大纲数据库表设计 - 简化版（基于事件驱动）
-- 创建时间: 2025-10-02

-- 1. 章节大纲主表（简化版）
CREATE TABLE IF NOT EXISTS chapter_outlines (
    id VARCHAR(50) PRIMARY KEY,
    plot_outline_id VARCHAR(50) NOT NULL REFERENCES plot_outlines(id) ON DELETE CASCADE,
    chapter_number INTEGER NOT NULL,
    title VARCHAR(200) NOT NULL,
    
    -- 章节定位
    story_position DECIMAL(3,2) NOT NULL,  -- 在故事中的位置比例 (0.0-1.0)
    act_belonging VARCHAR(50),             -- 所属幕次
    
    -- 章节内容
    chapter_summary TEXT NOT NULL,
    character_appearances JSONB DEFAULT '[]'::jsonb,  -- 出场角色
    
    -- 剧情功能
    plot_function VARCHAR(50) NOT NULL,     -- 剧情功能
    conflict_development TEXT,             -- 冲突发展
    character_development JSONB DEFAULT '[]'::jsonb,  -- 角色发展
    
    -- 写作指导
    writing_notes TEXT,                    -- 写作指导
    
    -- 情感和氛围
    emotional_tone VARCHAR(50) NOT NULL,   -- 情感基调
    atmosphere TEXT,                       -- 氛围描述
    tension_level INTEGER DEFAULT 5,       -- 紧张程度 (1-10)
    
    -- 世界观元素
    worldview_elements JSONB DEFAULT '[]'::jsonb,  -- 涉及的世界观元素
    
    -- 元数据
    estimated_word_count INTEGER DEFAULT 5000,
    status VARCHAR(20) DEFAULT '大纲',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- 唯一约束
    UNIQUE(plot_outline_id, chapter_number)
);

-- 2. 场景表（简化版）
CREATE TABLE IF NOT EXISTS scenes (
    id VARCHAR(50) PRIMARY KEY,
    chapter_outline_id VARCHAR(50) NOT NULL REFERENCES chapter_outlines(id) ON DELETE CASCADE,
    scene_number INTEGER NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    location VARCHAR(200),                 -- 场景地点
    characters_present JSONB DEFAULT '[]'::jsonb,  -- 在场角色
    purpose TEXT,                          -- 场景目的
    related_events JSONB DEFAULT '[]'::jsonb,     -- 关联事件ID列表
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- 唯一约束
    UNIQUE(chapter_outline_id, scene_number)
);

-- 3. 角色发展表（简化版）
CREATE TABLE IF NOT EXISTS character_developments (
    id VARCHAR(50) PRIMARY KEY,
    chapter_outline_id VARCHAR(50) NOT NULL REFERENCES chapter_outlines(id) ON DELETE CASCADE,
    character_id VARCHAR(50) NOT NULL,
    development_type VARCHAR(50) NOT NULL, -- 发展类型
    description TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. 事件整合表（新增）
CREATE TABLE IF NOT EXISTS event_integrations (
    id VARCHAR(50) PRIMARY KEY,
    chapter_outline_id VARCHAR(50) NOT NULL REFERENCES chapter_outlines(id) ON DELETE CASCADE,
    event_id VARCHAR(50) NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    event_title VARCHAR(200) NOT NULL,
    integration_type VARCHAR(50) NOT NULL,  -- 主要事件/次要事件
    chapter_position DECIMAL(3,2) NOT NULL,  -- 在章节中的位置比例 (0.0-1.0)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- 唯一约束
    UNIQUE(chapter_outline_id, event_id)
);

-- 5. 章节模板表
CREATE TABLE IF NOT EXISTS chapter_templates (
    template_id VARCHAR(50) PRIMARY KEY,
    template_name VARCHAR(100) NOT NULL,
    plot_function VARCHAR(50) NOT NULL,    -- 适用剧情功能
    structure JSONB DEFAULT '[]'::jsonb,   -- 结构要点
    scene_types JSONB DEFAULT '[]'::jsonb, -- 推荐场景类型
    emotional_tone VARCHAR(50) NOT NULL,   -- 推荐情感基调
    writing_tips JSONB DEFAULT '[]'::jsonb, -- 写作建议
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. 创建索引
CREATE INDEX IF NOT EXISTS idx_chapter_outlines_plot_id ON chapter_outlines(plot_outline_id);
CREATE INDEX IF NOT EXISTS idx_chapter_outlines_number ON chapter_outlines(plot_outline_id, chapter_number);
CREATE INDEX IF NOT EXISTS idx_chapter_outlines_position ON chapter_outlines(plot_outline_id, story_position);
CREATE INDEX IF NOT EXISTS idx_chapter_outlines_status ON chapter_outlines(status);
CREATE INDEX IF NOT EXISTS idx_scenes_chapter_id ON scenes(chapter_outline_id);
CREATE INDEX IF NOT EXISTS idx_scenes_number ON scenes(chapter_outline_id, scene_number);
CREATE INDEX IF NOT EXISTS idx_character_developments_chapter_id ON character_developments(chapter_outline_id);
CREATE INDEX IF NOT EXISTS idx_character_developments_character_id ON character_developments(character_id);
CREATE INDEX IF NOT EXISTS idx_event_integrations_chapter ON event_integrations(chapter_outline_id);
CREATE INDEX IF NOT EXISTS idx_event_integrations_event ON event_integrations(event_id);
CREATE INDEX IF NOT EXISTS idx_chapter_templates_function ON chapter_templates(plot_function);

-- 7. 创建更新时间触发器
CREATE OR REPLACE FUNCTION update_chapter_outline_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_chapter_outline_updated_at
    BEFORE UPDATE ON chapter_outlines
    FOR EACH ROW
    EXECUTE FUNCTION update_chapter_outline_updated_at();

-- 8. 插入章节模板数据
INSERT INTO chapter_templates (template_id, template_name, plot_function, structure, scene_types, emotional_tone, writing_tips) VALUES
('exposition', '背景介绍章节', '背景介绍', 
 '["介绍故事背景", "介绍主要角色", "建立世界观", "设置初始状态"]'::jsonb,
 '["氛围场景", "对话场景"]'::jsonb,
 '轻松',
 '["避免信息过载", "通过角色视角展示世界", "保持读者兴趣", "设置悬念"]'::jsonb),

('inciting_incident', '引发事件章节', '引发事件',
 '["正常生活被打破", "主角面临选择", "冲突开始显现", "故事目标确立"]'::jsonb,
 '["动作场景", "对话场景"]'::jsonb,
 '紧张',
 '["制造戏剧性转折", "让主角主动选择", "建立紧迫感", "为后续冲突埋下伏笔"]'::jsonb),

('rising_action', '上升行动章节', '上升行动',
 '["主角开始行动", "遇到障碍和挑战", "角色关系发展", "冲突逐步升级"]'::jsonb,
 '["动作场景", "对话场景", "战斗场景"]'::jsonb,
 '戏剧性',
 '["逐步增加紧张感", "发展角色关系", "引入新角色或元素", "为高潮做准备"]'::jsonb),

('climax', '高潮章节', '高潮',
 '["冲突达到顶点", "主角面临最大挑战", "关键决策时刻", "冲突解决或转变"]'::jsonb,
 '["战斗场景", "动作场景", "对话场景"]'::jsonb,
 '紧张',
 '["制造最大紧张感", "让主角面临终极选择", "解决主要冲突", "为结局做准备"]'::jsonb),

('falling_action', '回落行动章节', '回落行动',
 '["冲突后果显现", "角色处理结果", "关系重新调整", "为结局做准备"]'::jsonb,
 '["对话场景", "氛围场景"]'::jsonb,
 '轻松',
 '["处理高潮的后果", "发展角色关系", "为结局做铺垫", "保持读者兴趣"]'::jsonb),

('resolution', '结局章节', '结局',
 '["解决剩余问题", "角色获得成长", "关系得到确认", "故事圆满结束"]'::jsonb,
 '["对话场景", "氛围场景"]'::jsonb,
 '欢快',
 '["给读者满足感", "展示角色成长", "解决所有悬念", "留下余韵"]'::jsonb)
ON CONFLICT (template_id) DO NOTHING;

-- 9. 创建视图：章节大纲详情
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

-- 10. 创建函数：获取章节大纲的完整信息
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
        )
    ) INTO result
    FROM chapter_outlines co
    WHERE co.id = chapter_id;
    
    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- 11. 创建函数：获取剧情大纲的所有章节
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
            )
        ) ORDER BY co.chapter_number
    ) INTO result
    FROM chapter_outlines co
    WHERE co.plot_outline_id = plot_id;
    
    RETURN COALESCE(result, '[]'::jsonb);
END;
$$ LANGUAGE plpgsql;

-- 12. 创建函数：统计章节大纲信息
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
