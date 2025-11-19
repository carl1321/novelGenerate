-- 重新设计事件版本管理系统
-- 核心原则：同一事件的所有版本使用相同ID，通过版本号区分

-- 1. 备份现有数据（如果需要）
-- CREATE TABLE events_backup AS SELECT * FROM events;

-- 2. 删除现有的版本管理字段（如果存在）
ALTER TABLE events DROP COLUMN IF EXISTS original_event_id;
ALTER TABLE events DROP COLUMN IF EXISTS version;
ALTER TABLE events DROP COLUMN IF EXISTS is_current_version;

-- 3. 重新添加版本管理字段
ALTER TABLE events ADD COLUMN version INTEGER DEFAULT 1 NOT NULL;
ALTER TABLE events ADD COLUMN is_current_version BOOLEAN DEFAULT TRUE NOT NULL;

-- 4. 添加约束
-- 同一ID的版本号必须唯一
ALTER TABLE events ADD CONSTRAINT unique_event_version UNIQUE (id, version);

-- 同一ID只能有一个当前版本
CREATE UNIQUE INDEX unique_current_version ON events (id) WHERE is_current_version = TRUE;

-- 5. 删除旧的版本管理函数（如果存在）
DROP FUNCTION IF EXISTS get_latest_event_version(VARCHAR(50));
DROP FUNCTION IF EXISTS get_event_all_versions(VARCHAR(50));
DROP FUNCTION IF EXISTS create_event_version(VARCHAR(50), VARCHAR(200), VARCHAR(50), TEXT, TEXT);
DROP FUNCTION IF EXISTS rollback_event_version(VARCHAR(50), INTEGER);

-- 6. 创建新的版本管理函数

-- 获取事件的最新版本
CREATE OR REPLACE FUNCTION get_latest_event_version(p_event_id VARCHAR(50))
RETURNS TABLE (
    id VARCHAR(50),
    version INTEGER,
    is_current_version BOOLEAN,
    title VARCHAR(200),
    event_type VARCHAR(50),
    description TEXT,
    outcome TEXT,
    plot_outline_id VARCHAR(50),
    chapter_number INTEGER,
    sequence_order INTEGER,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        e.id, e.version, e.is_current_version,
        e.title, e.event_type, e.description, e.outcome,
        e.plot_outline_id, e.chapter_number, e.sequence_order,
        e.created_at, e.updated_at
    FROM events e
    WHERE e.id = p_event_id 
      AND e.is_current_version = TRUE;
END;
$$ LANGUAGE plpgsql;

-- 获取事件的所有版本
CREATE OR REPLACE FUNCTION get_event_all_versions(p_event_id VARCHAR(50))
RETURNS TABLE (
    id VARCHAR(50),
    version INTEGER,
    is_current_version BOOLEAN,
    title VARCHAR(200),
    event_type VARCHAR(50),
    description TEXT,
    outcome TEXT,
    plot_outline_id VARCHAR(50),
    chapter_number INTEGER,
    sequence_order INTEGER,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        e.id, e.version, e.is_current_version,
        e.title, e.event_type, e.description, e.outcome,
        e.plot_outline_id, e.chapter_number, e.sequence_order,
        e.created_at, e.updated_at
    FROM events e
    WHERE e.id = p_event_id
    ORDER BY e.version ASC;
END;
$$ LANGUAGE plpgsql;

-- 创建事件新版本
CREATE OR REPLACE FUNCTION create_event_version(
    p_event_id VARCHAR(50),
    p_new_title VARCHAR(200),
    p_new_event_type VARCHAR(50),
    p_new_description TEXT,
    p_new_outcome TEXT
)
RETURNS VARCHAR(50) AS $$
DECLARE
    v_next_version INTEGER;
    v_plot_outline_id VARCHAR(50);
    v_chapter_number INTEGER;
    v_sequence_order INTEGER;
BEGIN
    -- 获取原始事件信息
    SELECT plot_outline_id, chapter_number, sequence_order
    INTO v_plot_outline_id, v_chapter_number, v_sequence_order
    FROM events 
    WHERE id = p_event_id 
      AND is_current_version = TRUE
    LIMIT 1;
    
    -- 获取下一个版本号
    SELECT COALESCE(MAX(version), 0) + 1
    INTO v_next_version
    FROM events 
    WHERE id = p_event_id;
    
    -- 将当前版本标记为非当前版本
    UPDATE events 
    SET is_current_version = FALSE 
    WHERE id = p_event_id 
      AND is_current_version = TRUE;
    
    -- 插入新版本（使用相同的ID）
    INSERT INTO events (
        id, version, is_current_version,
        title, event_type, description, outcome,
        plot_outline_id, chapter_number, sequence_order,
        created_at, updated_at
    ) VALUES (
        p_event_id, v_next_version, TRUE,
        p_new_title, p_new_event_type, p_new_description, p_new_outcome,
        v_plot_outline_id, v_chapter_number, v_sequence_order,
        CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
    );
    
    RETURN p_event_id;
END;
$$ LANGUAGE plpgsql;

-- 删除事件版本
CREATE OR REPLACE FUNCTION delete_event_version(
    p_event_id VARCHAR(50),
    p_version INTEGER DEFAULT NULL
)
RETURNS BOOLEAN AS $$
DECLARE
    v_deleted_count INTEGER;
BEGIN
    IF p_version IS NULL THEN
        -- 删除整个事件的所有版本
        DELETE FROM events WHERE id = p_event_id;
        GET DIAGNOSTICS v_deleted_count = ROW_COUNT;
    ELSE
        -- 只删除指定版本
        DELETE FROM events WHERE id = p_event_id AND version = p_version;
        GET DIAGNOSTICS v_deleted_count = ROW_COUNT;
        
        -- 如果删除的是当前版本，需要将其他版本设为当前版本
        IF v_deleted_count > 0 THEN
            UPDATE events 
            SET is_current_version = TRUE 
            WHERE id = p_event_id 
              AND version = (
                  SELECT MAX(version) 
                  FROM events 
                  WHERE id = p_event_id
              );
        END IF;
    END IF;
    
    RETURN v_deleted_count > 0;
END;
$$ LANGUAGE plpgsql;

-- 获取剧情大纲下所有事件的最新版本
CREATE OR REPLACE FUNCTION get_latest_versions_by_plot(p_plot_outline_id VARCHAR(50))
RETURNS TABLE (
    id VARCHAR(50),
    version INTEGER,
    is_current_version BOOLEAN,
    title VARCHAR(200),
    event_type VARCHAR(50),
    description TEXT,
    outcome TEXT,
    plot_outline_id VARCHAR(50),
    chapter_number INTEGER,
    sequence_order INTEGER,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        e.id, e.version, e.is_current_version,
        e.title, e.event_type, e.description, e.outcome,
        e.plot_outline_id, e.chapter_number, e.sequence_order,
        e.created_at, e.updated_at
    FROM events e
    WHERE e.plot_outline_id = p_plot_outline_id 
      AND e.is_current_version = TRUE
    ORDER BY e.chapter_number ASC, e.sequence_order ASC;
END;
$$ LANGUAGE plpgsql;

-- 7. 更新现有数据（为现有事件设置版本号）
UPDATE events SET version = 1, is_current_version = TRUE WHERE version IS NULL;

-- 8. 添加注释
COMMENT ON COLUMN events.version IS '事件版本号，同一ID的版本号递增';
COMMENT ON COLUMN events.is_current_version IS '是否为当前版本，同一ID只能有一个当前版本';
COMMENT ON FUNCTION get_latest_event_version(VARCHAR(50)) IS '获取事件的最新版本';
COMMENT ON FUNCTION get_event_all_versions(VARCHAR(50)) IS '获取事件的所有版本';
COMMENT ON FUNCTION create_event_version(VARCHAR(50), VARCHAR(200), VARCHAR(50), TEXT, TEXT) IS '创建事件新版本';
COMMENT ON FUNCTION delete_event_version(VARCHAR(50), INTEGER) IS '删除事件版本，未指定版本号则删除整个事件';
COMMENT ON FUNCTION get_latest_versions_by_plot(VARCHAR(50)) IS '获取剧情大纲下所有事件的最新版本';
