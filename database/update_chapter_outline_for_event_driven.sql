-- 更新章节大纲表结构以支持事件驱动的章节生成
-- 创建时间: 2025-01-09

-- 1. 添加核心事件字段
ALTER TABLE chapter_outlines 
ADD COLUMN IF NOT EXISTS core_event VARCHAR(50);

-- 2. 更新场景表结构，简化字段
ALTER TABLE scenes 
ADD COLUMN IF NOT EXISTS scene_title VARCHAR(200),
ADD COLUMN IF NOT EXISTS scene_description TEXT,
ADD COLUMN IF NOT EXISTS event_relation TEXT;

-- 3. 创建事件-章节映射表（如果不存在）
CREATE TABLE IF NOT EXISTS event_chapter_mappings (
    id VARCHAR(50) PRIMARY KEY,
    event_id VARCHAR(50) NOT NULL,
    chapter_outline_id VARCHAR(50) NOT NULL REFERENCES chapter_outlines(id) ON DELETE CASCADE,
    mapping_type VARCHAR(50) DEFAULT 'core', -- 'core', 'supporting', 'reference'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(event_id, chapter_outline_id)
);

-- 4. 创建索引
CREATE INDEX IF NOT EXISTS idx_chapter_outlines_core_event ON chapter_outlines(core_event);
CREATE INDEX IF NOT EXISTS idx_event_chapter_mappings_event_id ON event_chapter_mappings(event_id);
CREATE INDEX IF NOT EXISTS idx_event_chapter_mappings_chapter_id ON event_chapter_mappings(chapter_outline_id);

-- 5. 更新现有数据（可选）
-- 将现有的related_events字段中的第一个事件设为core_event
UPDATE chapter_outlines 
SET core_event = (
    SELECT event_id 
    FROM event_chapter_mappings 
    WHERE chapter_outline_id = chapter_outlines.id 
    LIMIT 1
)
WHERE core_event IS NULL;

-- 6. 添加注释
COMMENT ON COLUMN chapter_outlines.core_event IS '核心事件ID，章节围绕此事件展开';
COMMENT ON COLUMN scenes.scene_title IS '场景标题';
COMMENT ON COLUMN scenes.scene_description IS '场景描述';
COMMENT ON COLUMN scenes.event_relation IS '与核心事件的关系';
COMMENT ON TABLE event_chapter_mappings IS '事件-章节映射表';
