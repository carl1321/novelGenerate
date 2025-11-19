-- 创建事件进化历史表
-- 用于存储事件的所有版本，避免主键冲突

-- 1. 创建事件进化历史表
CREATE TABLE IF NOT EXISTS event_evolution_history (
    id VARCHAR(50) PRIMARY KEY DEFAULT 'evo_' || substr(md5(random()::text), 1, 8),
    original_event_id VARCHAR(50) NOT NULL,  -- 原始事件ID
    version INTEGER NOT NULL DEFAULT 1,     -- 版本号
    is_current_version BOOLEAN DEFAULT TRUE, -- 是否为当前版本
    
    -- 事件内容
    title VARCHAR(200) NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    description TEXT,
    outcome TEXT,
    
    -- 关联信息
    plot_outline_id VARCHAR(50),
    chapter_number INTEGER,
    sequence_order INTEGER,
    
    -- 进化信息
    evolution_reason TEXT,  -- 进化原因
    score_id INTEGER,       -- 关联的评分ID
    parent_version_id VARCHAR(50), -- 父版本ID
    
    -- 时间戳
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- 索引
    CONSTRAINT fk_original_event FOREIGN KEY (original_event_id) REFERENCES events(id) ON DELETE CASCADE,
    CONSTRAINT fk_parent_version FOREIGN KEY (parent_version_id) REFERENCES event_evolution_history(id) ON DELETE SET NULL
);

-- 2. 创建索引
CREATE INDEX IF NOT EXISTS idx_event_evolution_original_id ON event_evolution_history(original_event_id);
CREATE INDEX IF NOT EXISTS idx_event_evolution_version ON event_evolution_history(original_event_id, version);
CREATE INDEX IF NOT EXISTS idx_event_evolution_current ON event_evolution_history(original_event_id, is_current_version);
CREATE INDEX IF NOT EXISTS idx_event_evolution_plot ON event_evolution_history(plot_outline_id);

-- 3. 创建函数：获取事件的最新版本
CREATE OR REPLACE FUNCTION get_event_latest_version(p_original_event_id VARCHAR(50))
RETURNS TABLE (
    id VARCHAR(50),
    original_event_id VARCHAR(50),
    version INTEGER,
    is_current_version BOOLEAN,
    title VARCHAR(200),
    event_type VARCHAR(50),
    description TEXT,
    outcome TEXT,
    plot_outline_id VARCHAR(50),
    chapter_number INTEGER,
    sequence_order INTEGER,
    evolution_reason TEXT,
    score_id INTEGER,
    parent_version_id VARCHAR(50),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        eeh.id, eeh.original_event_id, eeh.version, eeh.is_current_version,
        eeh.title, eeh.event_type, eeh.description, eeh.outcome,
        eeh.plot_outline_id, eeh.chapter_number, eeh.sequence_order,
        eeh.evolution_reason, eeh.score_id, eeh.parent_version_id,
        eeh.created_at, eeh.updated_at
    FROM event_evolution_history eeh
    WHERE eeh.original_event_id = p_original_event_id 
      AND eeh.is_current_version = TRUE
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;

-- 4. 创建函数：获取事件的所有版本
CREATE OR REPLACE FUNCTION get_event_all_evolution_versions(p_original_event_id VARCHAR(50))
RETURNS TABLE (
    id VARCHAR(50),
    original_event_id VARCHAR(50),
    version INTEGER,
    is_current_version BOOLEAN,
    title VARCHAR(200),
    event_type VARCHAR(50),
    description TEXT,
    outcome TEXT,
    plot_outline_id VARCHAR(50),
    chapter_number INTEGER,
    sequence_order INTEGER,
    evolution_reason TEXT,
    score_id INTEGER,
    parent_version_id VARCHAR(50),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        eeh.id, eeh.original_event_id, eeh.version, eeh.is_current_version,
        eeh.title, eeh.event_type, eeh.description, eeh.outcome,
        eeh.plot_outline_id, eeh.chapter_number, eeh.sequence_order,
        eeh.evolution_reason, eeh.score_id, eeh.parent_version_id,
        eeh.created_at, eeh.updated_at
    FROM event_evolution_history eeh
    WHERE eeh.original_event_id = p_original_event_id
    ORDER BY eeh.version ASC;
END;
$$ LANGUAGE plpgsql;

-- 5. 创建函数：创建事件新版本（进化）
CREATE OR REPLACE FUNCTION create_event_evolution_version(
    p_original_event_id VARCHAR(50),
    p_new_title VARCHAR(200),
    p_new_event_type VARCHAR(50),
    p_new_description TEXT,
    p_new_outcome TEXT,
    p_evolution_reason TEXT DEFAULT '',
    p_score_id INTEGER DEFAULT NULL
)
RETURNS VARCHAR(50) AS $$
DECLARE
    v_new_evolution_id VARCHAR(50);
    v_next_version INTEGER;
    v_plot_outline_id VARCHAR(50);
    v_chapter_number INTEGER;
    v_sequence_order INTEGER;
    v_current_version_id VARCHAR(50);
BEGIN
    -- 获取原始事件信息
    SELECT plot_outline_id, chapter_number, sequence_order
    INTO v_plot_outline_id, v_chapter_number, v_sequence_order
    FROM events 
    WHERE id = p_original_event_id
    LIMIT 1;
    
    -- 获取当前版本ID
    SELECT id INTO v_current_version_id
    FROM event_evolution_history 
    WHERE original_event_id = p_original_event_id 
      AND is_current_version = TRUE
    LIMIT 1;
    
    -- 获取下一个版本号
    SELECT COALESCE(MAX(version), 0) + 1
    INTO v_next_version
    FROM event_evolution_history 
    WHERE original_event_id = p_original_event_id;
    
    -- 生成新的进化ID
    v_new_evolution_id := 'evo_' || substr(md5(random()::text), 1, 8);
    
    -- 将当前版本标记为非当前版本
    UPDATE event_evolution_history 
    SET is_current_version = FALSE 
    WHERE original_event_id = p_original_event_id 
      AND is_current_version = TRUE;
    
    -- 插入新版本到进化历史表
    INSERT INTO event_evolution_history (
        id, original_event_id, version, is_current_version,
        title, event_type, description, outcome,
        plot_outline_id, chapter_number, sequence_order,
        evolution_reason, score_id, parent_version_id,
        created_at, updated_at
    ) VALUES (
        v_new_evolution_id, p_original_event_id, v_next_version, TRUE,
        p_new_title, p_new_event_type, p_new_description, p_new_outcome,
        v_plot_outline_id, v_chapter_number, v_sequence_order,
        p_evolution_reason, p_score_id, v_current_version_id,
        CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
    );
    
    RETURN v_new_evolution_id;
END;
$$ LANGUAGE plpgsql;

-- 6. 创建函数：回滚到指定版本
CREATE OR REPLACE FUNCTION rollback_event_evolution_version(
    p_original_event_id VARCHAR(50),
    p_target_version INTEGER
)
RETURNS BOOLEAN AS $$
BEGIN
    -- 将当前版本标记为非当前版本
    UPDATE event_evolution_history 
    SET is_current_version = FALSE 
    WHERE original_event_id = p_original_event_id 
      AND is_current_version = TRUE;
    
    -- 将目标版本标记为当前版本
    UPDATE event_evolution_history 
    SET is_current_version = TRUE 
    WHERE original_event_id = p_original_event_id 
      AND version = p_target_version;
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- 7. 创建函数：删除事件进化版本
CREATE OR REPLACE FUNCTION delete_event_evolution_version(
    p_original_event_id VARCHAR(50),
    p_version INTEGER DEFAULT NULL
)
RETURNS BOOLEAN AS $$
BEGIN
    IF p_version IS NULL THEN
        -- 删除所有版本
        DELETE FROM event_evolution_history 
        WHERE original_event_id = p_original_event_id;
    ELSE
        -- 删除指定版本
        DELETE FROM event_evolution_history 
        WHERE original_event_id = p_original_event_id 
          AND version = p_version;
    END IF;
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- 8. 创建视图：事件与最新进化版本的关联视图
CREATE OR REPLACE VIEW events_with_latest_evolution AS
SELECT 
    e.id as original_event_id,
    e.title as original_title,
    e.event_type as original_event_type,
    e.description as original_description,
    e.outcome as original_outcome,
    e.plot_outline_id,
    e.chapter_number,
    e.sequence_order,
    e.created_at as original_created_at,
    e.updated_at as original_updated_at,
    
    -- 最新进化版本信息
    eeh.id as current_evolution_id,
    eeh.version as current_version,
    eeh.title as current_title,
    eeh.event_type as current_event_type,
    eeh.description as current_description,
    eeh.outcome as current_outcome,
    eeh.evolution_reason,
    eeh.score_id,
    eeh.parent_version_id,
    eeh.created_at as evolution_created_at,
    eeh.updated_at as evolution_updated_at,
    
    -- 判断是否有进化版本
    CASE 
        WHEN eeh.id IS NOT NULL THEN TRUE 
        ELSE FALSE 
    END as has_evolution
    
FROM events e
LEFT JOIN event_evolution_history eeh ON (
    e.id = eeh.original_event_id 
    AND eeh.is_current_version = TRUE
);

-- 9. 添加注释
COMMENT ON TABLE event_evolution_history IS '事件进化历史表，存储事件的所有版本';
COMMENT ON COLUMN event_evolution_history.original_event_id IS '原始事件ID，关联events表';
COMMENT ON COLUMN event_evolution_history.version IS '版本号，从1开始递增';
COMMENT ON COLUMN event_evolution_history.is_current_version IS '是否为当前版本';
COMMENT ON COLUMN event_evolution_history.evolution_reason IS '进化原因描述';
COMMENT ON COLUMN event_evolution_history.score_id IS '关联的评分ID';
COMMENT ON COLUMN event_evolution_history.parent_version_id IS '父版本ID，用于版本链追踪';

COMMENT ON VIEW events_with_latest_evolution IS '事件与最新进化版本的关联视图，用于查询时只显示最新版本';
