-- 事件数据表初始化脚本
-- 创建事件表

CREATE TABLE IF NOT EXISTS events (
    id VARCHAR(50) PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    event_type VARCHAR(50) NOT NULL,
    importance VARCHAR(20) NOT NULL,
    category VARCHAR(50) NOT NULL,
    
    -- 事件内容
    setting VARCHAR(200),
    participants JSONB DEFAULT '[]'::jsonb,
    duration VARCHAR(100),
    outcome TEXT,
    
    -- 剧情相关
    plot_impact TEXT,
    character_impact JSONB DEFAULT '{}'::jsonb,
    foreshadowing_elements JSONB DEFAULT '[]'::jsonb,
    
    -- 元数据
    prerequisites JSONB DEFAULT '[]'::jsonb,
    consequences JSONB DEFAULT '[]'::jsonb,
    tags JSONB DEFAULT '[]'::jsonb,
    
    -- 关联信息
    plot_outline_id VARCHAR(50),
    chapter_number INTEGER,
    sequence_order INTEGER DEFAULT 0,
    
    -- 时间信息
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_events_plot_outline_id ON events(plot_outline_id);
CREATE INDEX IF NOT EXISTS idx_events_chapter_number ON events(chapter_number);
CREATE INDEX IF NOT EXISTS idx_events_event_type ON events(event_type);
CREATE INDEX IF NOT EXISTS idx_events_importance ON events(importance);
CREATE INDEX IF NOT EXISTS idx_events_sequence_order ON events(sequence_order);

-- 添加注释
COMMENT ON TABLE events IS '事件表';
COMMENT ON COLUMN events.id IS '事件ID';
COMMENT ON COLUMN events.title IS '事件标题';
COMMENT ON COLUMN events.description IS '事件描述';
COMMENT ON COLUMN events.event_type IS '事件类型（日常事件、冲突事件等）';
COMMENT ON COLUMN events.importance IS '事件重要性（低、中、高、关键）';
COMMENT ON COLUMN events.category IS '事件分类（剧情推动、角色发展等）';
COMMENT ON COLUMN events.setting IS '事件发生地点';
COMMENT ON COLUMN events.participants IS '参与角色列表（JSON数组）';
COMMENT ON COLUMN events.duration IS '事件持续时间';
COMMENT ON COLUMN events.outcome IS '事件结果';
COMMENT ON COLUMN events.plot_impact IS '对剧情的影响';
COMMENT ON COLUMN events.character_impact IS '对角色的影响（JSON对象）';
COMMENT ON COLUMN events.foreshadowing_elements IS '伏笔元素列表（JSON数组）';
COMMENT ON COLUMN events.prerequisites IS '前置条件列表（JSON数组）';
COMMENT ON COLUMN events.consequences IS '后续影响列表（JSON数组）';
COMMENT ON COLUMN events.tags IS '标签列表（JSON数组）';
COMMENT ON COLUMN events.plot_outline_id IS '关联的剧情大纲ID';
COMMENT ON COLUMN events.chapter_number IS '所属章节号';
COMMENT ON COLUMN events.sequence_order IS '事件顺序';
COMMENT ON COLUMN events.created_at IS '创建时间';
COMMENT ON COLUMN events.updated_at IS '更新时间';
