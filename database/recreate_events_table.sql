-- 重新创建事件表结构
-- 删除原有表并创建新的简化事件表

-- 1. 删除原有的事件相关表和视图
DROP VIEW IF EXISTS simple_events CASCADE;
DROP TABLE IF EXISTS event_chapter_mappings CASCADE;
DROP TABLE IF EXISTS events CASCADE;

-- 2. 删除相关函数
DROP FUNCTION IF EXISTS get_simple_events_by_plot(VARCHAR(50)) CASCADE;
DROP FUNCTION IF EXISTS get_simple_events_stats(VARCHAR(50)) CASCADE;
DROP FUNCTION IF EXISTS insert_simple_event CASCADE;
DROP FUNCTION IF EXISTS update_simple_event CASCADE;
DROP FUNCTION IF EXISTS delete_simple_event CASCADE;
DROP FUNCTION IF EXISTS get_simple_events_paginated CASCADE;
DROP FUNCTION IF EXISTS search_simple_events CASCADE;
DROP FUNCTION IF EXISTS export_simple_events CASCADE;
DROP FUNCTION IF EXISTS update_events_updated_at() CASCADE;

-- 3. 创建新的简化事件表
CREATE TABLE events (
    id VARCHAR(50) PRIMARY KEY,
    plot_outline_id VARCHAR(50) NOT NULL,
    chapter_number INTEGER,
    sequence_order INTEGER DEFAULT 0,
    
    -- 核心字段（与SimpleEvent模型一致）
    title VARCHAR(200) NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    outcome TEXT NOT NULL,
    
    -- 时间信息
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- 外键约束
    CONSTRAINT fk_events_plot_outline 
        FOREIGN KEY (plot_outline_id) 
        REFERENCES plot_outlines(id) 
        ON DELETE CASCADE
);

-- 4. 创建索引
CREATE INDEX idx_events_plot_outline_id ON events(plot_outline_id);
CREATE INDEX idx_events_chapter_number ON events(chapter_number);
CREATE INDEX idx_events_event_type ON events(event_type);
CREATE INDEX idx_events_sequence_order ON events(plot_outline_id, sequence_order);
CREATE INDEX idx_events_created_at ON events(created_at);

-- 5. 添加注释
COMMENT ON TABLE events IS '事件表，仅包含核心字段';
COMMENT ON COLUMN events.id IS '事件ID';
COMMENT ON COLUMN events.plot_outline_id IS '关联的剧情大纲ID';
COMMENT ON COLUMN events.chapter_number IS '所属章节号';
COMMENT ON COLUMN events.sequence_order IS '事件顺序';
COMMENT ON COLUMN events.title IS '事件标题';
COMMENT ON COLUMN events.event_type IS '事件类型';
COMMENT ON COLUMN events.description IS '事件描述';
COMMENT ON COLUMN events.outcome IS '事件结果';
COMMENT ON COLUMN events.created_at IS '创建时间';
COMMENT ON COLUMN events.updated_at IS '更新时间';

-- 6. 创建触发器：自动更新updated_at字段
CREATE OR REPLACE FUNCTION update_events_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_events_updated_at
    BEFORE UPDATE ON events
    FOR EACH ROW
    EXECUTE FUNCTION update_events_updated_at();

-- 7. 创建事件CRUD函数

-- 插入事件
CREATE OR REPLACE FUNCTION insert_event(
    p_id VARCHAR(50),
    p_plot_outline_id VARCHAR(50),
    p_title VARCHAR(200),
    p_event_type VARCHAR(50),
    p_description TEXT,
    p_outcome TEXT,
    p_chapter_number INTEGER DEFAULT NULL,
    p_sequence_order INTEGER DEFAULT 0
)
RETURNS BOOLEAN AS $$
BEGIN
    INSERT INTO events (
        id, plot_outline_id, chapter_number, sequence_order,
        title, event_type, description, outcome, created_at
    ) VALUES (
        p_id, p_plot_outline_id, p_chapter_number, p_sequence_order,
        p_title, p_event_type, p_description, p_outcome, CURRENT_TIMESTAMP
    );
    RETURN TRUE;
EXCEPTION
    WHEN OTHERS THEN
        RETURN FALSE;
END;
$$ LANGUAGE plpgsql;

-- 更新事件
CREATE OR REPLACE FUNCTION update_event(
    p_id VARCHAR(50),
    p_title VARCHAR(200) DEFAULT NULL,
    p_event_type VARCHAR(50) DEFAULT NULL,
    p_description TEXT DEFAULT NULL,
    p_outcome TEXT DEFAULT NULL,
    p_chapter_number INTEGER DEFAULT NULL,
    p_sequence_order INTEGER DEFAULT NULL
)
RETURNS BOOLEAN AS $$
DECLARE
    update_fields TEXT[] := ARRAY[]::TEXT[];
    update_values TEXT[] := ARRAY[]::TEXT[];
    sql_query TEXT;
BEGIN
    -- 构建动态更新字段
    IF p_title IS NOT NULL THEN
        update_fields := array_append(update_fields, 'title = $' || (array_length(update_values, 1) + 2)::TEXT);
        update_values := array_append(update_values, p_title);
    END IF;
    
    IF p_event_type IS NOT NULL THEN
        update_fields := array_append(update_fields, 'event_type = $' || (array_length(update_values, 1) + 2)::TEXT);
        update_values := array_append(update_values, p_event_type);
    END IF;
    
    IF p_description IS NOT NULL THEN
        update_fields := array_append(update_fields, 'description = $' || (array_length(update_values, 1) + 2)::TEXT);
        update_values := array_append(update_values, p_description);
    END IF;
    
    IF p_outcome IS NOT NULL THEN
        update_fields := array_append(update_fields, 'outcome = $' || (array_length(update_values, 1) + 2)::TEXT);
        update_values := array_append(update_values, p_outcome);
    END IF;
    
    IF p_chapter_number IS NOT NULL THEN
        update_fields := array_append(update_fields, 'chapter_number = $' || (array_length(update_values, 1) + 2)::TEXT);
        update_values := array_append(update_values, p_chapter_number::TEXT);
    END IF;
    
    IF p_sequence_order IS NOT NULL THEN
        update_fields := array_append(update_fields, 'sequence_order = $' || (array_length(update_values, 1) + 2)::TEXT);
        update_values := array_append(update_values, p_sequence_order::TEXT);
    END IF;
    
    -- 如果没有要更新的字段，返回false
    IF array_length(update_fields, 1) IS NULL THEN
        RETURN FALSE;
    END IF;
    
    -- 添加updated_at字段
    update_fields := array_append(update_fields, 'updated_at = CURRENT_TIMESTAMP');
    
    -- 构建SQL查询
    sql_query := 'UPDATE events SET ' || array_to_string(update_fields, ', ') || ' WHERE id = $1';
    
    -- 执行更新
    EXECUTE sql_query USING p_id, update_values[1], update_values[2], update_values[3], update_values[4], update_values[5], update_values[6];
    
    RETURN TRUE;
EXCEPTION
    WHEN OTHERS THEN
        RETURN FALSE;
END;
$$ LANGUAGE plpgsql;

-- 删除事件
CREATE OR REPLACE FUNCTION delete_event(p_id VARCHAR(50))
RETURNS BOOLEAN AS $$
BEGIN
    DELETE FROM events WHERE id = p_id;
    RETURN FOUND;
EXCEPTION
    WHEN OTHERS THEN
        RETURN FALSE;
END;
$$ LANGUAGE plpgsql;

-- 获取事件列表
CREATE OR REPLACE FUNCTION get_events_by_plot(plot_id VARCHAR(50))
RETURNS TABLE (
    id VARCHAR(50),
    plot_outline_id VARCHAR(50),
    chapter_number INTEGER,
    sequence_order INTEGER,
    title VARCHAR(200),
    event_type VARCHAR(50),
    description TEXT,
    outcome TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        e.id, e.plot_outline_id, e.chapter_number, e.sequence_order,
        e.title, e.event_type, e.description, e.outcome,
        e.created_at, e.updated_at
    FROM events e
    WHERE e.plot_outline_id = plot_id
    ORDER BY e.sequence_order, e.created_at;
END;
$$ LANGUAGE plpgsql;

-- 获取单个事件
CREATE OR REPLACE FUNCTION get_event_by_id(event_id VARCHAR(50))
RETURNS TABLE (
    id VARCHAR(50),
    plot_outline_id VARCHAR(50),
    chapter_number INTEGER,
    sequence_order INTEGER,
    title VARCHAR(200),
    event_type VARCHAR(50),
    description TEXT,
    outcome TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        e.id, e.plot_outline_id, e.chapter_number, e.sequence_order,
        e.title, e.event_type, e.description, e.outcome,
        e.created_at, e.updated_at
    FROM events e
    WHERE e.id = event_id;
END;
$$ LANGUAGE plpgsql;

-- 分页获取事件
CREATE OR REPLACE FUNCTION get_events_paginated(
    p_plot_id VARCHAR(50),
    p_page INTEGER DEFAULT 1,
    p_page_size INTEGER DEFAULT 20
)
RETURNS TABLE (
    id VARCHAR(50),
    plot_outline_id VARCHAR(50),
    chapter_number INTEGER,
    sequence_order INTEGER,
    title VARCHAR(200),
    event_type VARCHAR(50),
    description TEXT,
    outcome TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    total_count BIGINT
) AS $$
DECLARE
    offset_value INTEGER;
BEGIN
    offset_value := (p_page - 1) * p_page_size;
    
    RETURN QUERY
    SELECT 
        e.id, e.plot_outline_id, e.chapter_number, e.sequence_order,
        e.title, e.event_type, e.description, e.outcome,
        e.created_at, e.updated_at,
        COUNT(*) OVER() as total_count
    FROM events e
    WHERE e.plot_outline_id = p_plot_id
    ORDER BY e.sequence_order, e.created_at
    LIMIT p_page_size OFFSET offset_value;
END;
$$ LANGUAGE plpgsql;

-- 搜索事件
CREATE OR REPLACE FUNCTION search_events(
    p_plot_id VARCHAR(50),
    p_search_term TEXT
)
RETURNS TABLE (
    id VARCHAR(50),
    plot_outline_id VARCHAR(50),
    chapter_number INTEGER,
    sequence_order INTEGER,
    title VARCHAR(200),
    event_type VARCHAR(50),
    description TEXT,
    outcome TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    relevance_score REAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        e.id, e.plot_outline_id, e.chapter_number, e.sequence_order,
        e.title, e.event_type, e.description, e.outcome,
        e.created_at, e.updated_at,
        (
            CASE 
                WHEN e.title ILIKE '%' || p_search_term || '%' THEN 3.0
                WHEN e.description ILIKE '%' || p_search_term || '%' THEN 2.0
                WHEN e.outcome ILIKE '%' || p_search_term || '%' THEN 1.0
                ELSE 0.0
            END
        ) as relevance_score
    FROM events e
    WHERE e.plot_outline_id = p_plot_id
    AND (
        e.title ILIKE '%' || p_search_term || '%' OR
        e.description ILIKE '%' || p_search_term || '%' OR
        e.outcome ILIKE '%' || p_search_term || '%'
    )
    ORDER BY relevance_score DESC, e.sequence_order, e.created_at;
END;
$$ LANGUAGE plpgsql;

-- 获取事件统计
CREATE OR REPLACE FUNCTION get_events_stats(plot_id VARCHAR(50))
RETURNS TABLE (
    total_events BIGINT,
    events_by_type JSONB,
    events_by_chapter JSONB
) AS $$
DECLARE
    type_stats JSONB;
    chapter_stats JSONB;
BEGIN
    -- 获取总数
    SELECT COUNT(*) INTO total_events FROM events WHERE plot_outline_id = plot_id;
    
    -- 按类型统计
    SELECT jsonb_object_agg(event_type, type_count) INTO type_stats
    FROM (
        SELECT event_type, COUNT(*) as type_count
        FROM events 
        WHERE plot_outline_id = plot_id
        GROUP BY event_type
    ) t;
    
    -- 按章节统计
    SELECT jsonb_object_agg(
        COALESCE(chapter_number::TEXT, '未分配'), 
        chapter_count
    ) INTO chapter_stats
    FROM (
        SELECT chapter_number, COUNT(*) as chapter_count
        FROM events 
        WHERE plot_outline_id = plot_id
        GROUP BY chapter_number
    ) c;
    
    RETURN QUERY SELECT total_events, type_stats, chapter_stats;
END;
$$ LANGUAGE plpgsql;

-- 8. 添加函数注释
COMMENT ON FUNCTION insert_event IS '插入事件到数据库';
COMMENT ON FUNCTION update_event IS '更新事件';
COMMENT ON FUNCTION delete_event IS '删除事件';
COMMENT ON FUNCTION get_events_by_plot IS '根据剧情大纲ID获取事件列表';
COMMENT ON FUNCTION get_event_by_id IS '根据ID获取事件';
COMMENT ON FUNCTION get_events_paginated IS '分页获取事件列表';
COMMENT ON FUNCTION search_events IS '搜索事件';
COMMENT ON FUNCTION get_events_stats IS '获取事件统计信息';

-- 9. 创建权限设置
DO $$
BEGIN
    -- 尝试设置权限，如果失败则忽略
    BEGIN
        GRANT SELECT, INSERT, UPDATE, DELETE ON events TO PUBLIC;
        GRANT EXECUTE ON FUNCTION insert_event TO PUBLIC;
        GRANT EXECUTE ON FUNCTION update_event TO PUBLIC;
        GRANT EXECUTE ON FUNCTION delete_event TO PUBLIC;
        GRANT EXECUTE ON FUNCTION get_events_by_plot TO PUBLIC;
        GRANT EXECUTE ON FUNCTION get_event_by_id TO PUBLIC;
        GRANT EXECUTE ON FUNCTION get_events_paginated TO PUBLIC;
        GRANT EXECUTE ON FUNCTION search_events TO PUBLIC;
        GRANT EXECUTE ON FUNCTION get_events_stats TO PUBLIC;
    EXCEPTION
        WHEN OTHERS THEN
            -- 忽略权限设置错误
            NULL;
    END;
END
$$;

-- 10. 完成重建
SELECT '事件表重建完成' as status;
