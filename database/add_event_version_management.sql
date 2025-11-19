-- 添加事件版本管理功能
-- 为events表添加版本控制字段

-- 1. 添加版本管理字段
ALTER TABLE events ADD COLUMN IF NOT EXISTS version INTEGER DEFAULT 1;
ALTER TABLE events ADD COLUMN IF NOT EXISTS is_current_version BOOLEAN DEFAULT TRUE;
ALTER TABLE events ADD COLUMN IF NOT EXISTS original_event_id VARCHAR(50);

-- 2. 为现有事件设置版本信息
UPDATE events SET 
    version = 1,
    is_current_version = TRUE,
    original_event_id = id
WHERE original_event_id IS NULL;

-- 3. 创建索引
CREATE INDEX IF NOT EXISTS idx_events_version ON events(original_event_id, version);
CREATE INDEX IF NOT EXISTS idx_events_current_version ON events(original_event_id, is_current_version);

-- 4. 添加约束
ALTER TABLE events ADD CONSTRAINT chk_version_positive CHECK (version > 0);
ALTER TABLE events ADD CONSTRAINT chk_current_version_unique 
    EXCLUDE (original_event_id WITH =) WHERE (is_current_version = TRUE);

-- 5. 创建函数：获取事件的最新版本
CREATE OR REPLACE FUNCTION get_latest_event_version(p_event_id VARCHAR(50))
RETURNS TABLE (
    id VARCHAR(50),
    title VARCHAR(200),
    event_type VARCHAR(50),
    description TEXT,
    outcome TEXT,
    version INTEGER,
    is_current_version BOOLEAN,
    original_event_id VARCHAR(50),
    plot_outline_id VARCHAR(50),
    chapter_number INTEGER,
    sequence_order INTEGER,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT e.id, e.title, e.event_type, e.description, e.outcome,
           e.version, e.is_current_version, e.original_event_id,
           e.plot_outline_id, e.chapter_number, e.sequence_order,
           e.created_at, e.updated_at
    FROM events e
    WHERE e.original_event_id = p_event_id 
      AND e.is_current_version = TRUE
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;

-- 6. 创建函数：获取事件的所有版本
CREATE OR REPLACE FUNCTION get_event_all_versions(p_event_id VARCHAR(50))
RETURNS TABLE (
    id VARCHAR(50),
    title VARCHAR(200),
    event_type VARCHAR(50),
    description TEXT,
    outcome TEXT,
    version INTEGER,
    is_current_version BOOLEAN,
    original_event_id VARCHAR(50),
    plot_outline_id VARCHAR(50),
    chapter_number INTEGER,
    sequence_order INTEGER,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT e.id, e.title, e.event_type, e.description, e.outcome,
           e.version, e.is_current_version, e.original_event_id,
           e.plot_outline_id, e.chapter_number, e.sequence_order,
           e.created_at, e.updated_at
    FROM events e
    WHERE e.original_event_id = p_event_id
    ORDER BY e.version ASC;
END;
$$ LANGUAGE plpgsql;

-- 7. 创建函数：创建事件的新版本
CREATE OR REPLACE FUNCTION create_event_version(
    p_original_event_id VARCHAR(50),
    p_new_title VARCHAR(200),
    p_new_event_type VARCHAR(50),
    p_new_description TEXT,
    p_new_outcome TEXT
)
RETURNS VARCHAR(50) AS $$
DECLARE
    v_new_event_id VARCHAR(50);
    v_next_version INTEGER;
    v_plot_outline_id VARCHAR(50);
    v_chapter_number INTEGER;
    v_sequence_order INTEGER;
BEGIN
    -- 获取原始事件信息
    SELECT plot_outline_id, chapter_number, sequence_order
    INTO v_plot_outline_id, v_chapter_number, v_sequence_order
    FROM events 
    WHERE original_event_id = p_original_event_id 
      AND is_current_version = TRUE
    LIMIT 1;
    
    -- 如果没有找到原始事件，尝试直接查找
    IF v_plot_outline_id IS NULL THEN
        SELECT plot_outline_id, chapter_number, sequence_order
        INTO v_plot_outline_id, v_chapter_number, v_sequence_order
        FROM events 
        WHERE id = p_original_event_id
        LIMIT 1;
    END IF;
    
    -- 获取下一个版本号
    SELECT COALESCE(MAX(version), 0) + 1
    INTO v_next_version
    FROM events 
    WHERE original_event_id = p_original_event_id;
    
    -- 生成新的事件ID（保持原始ID前缀，添加版本后缀）
    v_new_event_id := p_original_event_id || '_v' || v_next_version;
    
    -- 将当前版本标记为非当前版本
    UPDATE events 
    SET is_current_version = FALSE 
    WHERE original_event_id = p_original_event_id 
      AND is_current_version = TRUE;
    
    -- 插入新版本
    INSERT INTO events (
        id, original_event_id, version, is_current_version,
        title, event_type, description, outcome,
        plot_outline_id, chapter_number, sequence_order,
        created_at, updated_at
    ) VALUES (
        v_new_event_id, p_original_event_id, v_next_version, TRUE,
        p_new_title, p_new_event_type, p_new_description, p_new_outcome,
        v_plot_outline_id, v_chapter_number, v_sequence_order,
        CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
    );
    
    RETURN v_new_event_id;
END;
$$ LANGUAGE plpgsql;

-- 8. 创建函数：回滚到指定版本
CREATE OR REPLACE FUNCTION rollback_event_version(
    p_original_event_id VARCHAR(50),
    p_target_version INTEGER
)
RETURNS BOOLEAN AS $$
BEGIN
    -- 将当前版本标记为非当前版本
    UPDATE events 
    SET is_current_version = FALSE 
    WHERE original_event_id = p_original_event_id 
      AND is_current_version = TRUE;
    
    -- 将目标版本标记为当前版本
    UPDATE events 
    SET is_current_version = TRUE 
    WHERE original_event_id = p_original_event_id 
      AND version = p_target_version;
    
    RETURN TRUE;
EXCEPTION
    WHEN OTHERS THEN
        RETURN FALSE;
END;
$$ LANGUAGE plpgsql;

-- 9. 添加注释
COMMENT ON COLUMN events.version IS '事件版本号，从1开始递增';
COMMENT ON COLUMN events.is_current_version IS '是否为当前版本';
COMMENT ON COLUMN events.original_event_id IS '原始事件ID，用于版本关联';

COMMENT ON FUNCTION get_latest_event_version(VARCHAR(50)) IS '获取事件的最新版本';
COMMENT ON FUNCTION get_event_all_versions(VARCHAR(50)) IS '获取事件的所有版本';
COMMENT ON FUNCTION create_event_version(VARCHAR(50), VARCHAR(200), VARCHAR(50), TEXT, TEXT) IS '创建事件的新版本';
COMMENT ON FUNCTION rollback_event_version(VARCHAR(50), INTEGER) IS '回滚到指定版本';
