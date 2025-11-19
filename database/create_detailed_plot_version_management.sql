-- 创建详细剧情版本管理表
-- 用于统一管理详细剧情的修正版本和进化版本
-- 版本优先级：修正版本 > 进化版本 > 原始版本

-- 1. 创建详细剧情版本管理表
CREATE TABLE IF NOT EXISTS detailed_plot_versions (
    id SERIAL PRIMARY KEY,  -- 自增主键
    detailed_plot_id VARCHAR(255) NOT NULL,  -- 详细剧情ID（与detailed_plots.id保持一致）
    version_type VARCHAR(50) NOT NULL,  -- 版本类型：'original', 'evolution', 'correction'
    version_number INTEGER NOT NULL DEFAULT 1,  -- 版本号
    is_current_version BOOLEAN DEFAULT FALSE,  -- 是否为当前版本
    
    -- 版本内容
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    word_count INTEGER DEFAULT 0,
    
    -- 版本来源信息
    source_table VARCHAR(50),  -- 来源表：'detailed_plots', 'evolution_history', 'correction_history'
    source_record_id VARCHAR(255),  -- 来源记录ID
    
    -- 版本元数据
    version_notes TEXT,  -- 版本说明
    created_by VARCHAR(50) DEFAULT 'system',  -- 创建者
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- 外键约束
    CONSTRAINT fk_detailed_plot_versions_detailed_plot_id 
        FOREIGN KEY (detailed_plot_id) REFERENCES detailed_plots(id) ON DELETE CASCADE
);

-- 2. 创建索引
CREATE INDEX IF NOT EXISTS idx_detailed_plot_versions_detailed_plot_id 
    ON detailed_plot_versions(detailed_plot_id);
CREATE INDEX IF NOT EXISTS idx_detailed_plot_versions_version_type 
    ON detailed_plot_versions(detailed_plot_id, version_type);
CREATE INDEX IF NOT EXISTS idx_detailed_plot_versions_current 
    ON detailed_plot_versions(detailed_plot_id, is_current_version);
CREATE INDEX IF NOT EXISTS idx_detailed_plot_versions_version_number 
    ON detailed_plot_versions(detailed_plot_id, version_number);

-- 3. 创建唯一约束：每个详细剧情只能有一个当前版本
CREATE UNIQUE INDEX IF NOT EXISTS idx_detailed_plot_versions_unique_current 
    ON detailed_plot_versions(detailed_plot_id) 
    WHERE is_current_version = TRUE;

-- 4. 添加注释
COMMENT ON TABLE detailed_plot_versions IS '详细剧情版本管理表';
COMMENT ON COLUMN detailed_plot_versions.id IS '版本记录ID（自增主键）';
COMMENT ON COLUMN detailed_plot_versions.detailed_plot_id IS '详细剧情ID（与detailed_plots.id保持一致）';
COMMENT ON COLUMN detailed_plot_versions.version_type IS '版本类型：original(原始), evolution(进化), correction(修正)';
COMMENT ON COLUMN detailed_plot_versions.version_number IS '版本号';
COMMENT ON COLUMN detailed_plot_versions.is_current_version IS '是否为当前版本';
COMMENT ON COLUMN detailed_plot_versions.title IS '版本标题';
COMMENT ON COLUMN detailed_plot_versions.content IS '版本内容';
COMMENT ON COLUMN detailed_plot_versions.word_count IS '字数统计';
COMMENT ON COLUMN detailed_plot_versions.source_table IS '来源表名';
COMMENT ON COLUMN detailed_plot_versions.source_record_id IS '来源记录ID';
COMMENT ON COLUMN detailed_plot_versions.version_notes IS '版本说明';
COMMENT ON COLUMN detailed_plot_versions.created_by IS '创建者';
COMMENT ON COLUMN detailed_plot_versions.created_at IS '创建时间';
COMMENT ON COLUMN detailed_plot_versions.updated_at IS '更新时间';

-- 5. 创建函数：获取详细剧情的最新版本
CREATE OR REPLACE FUNCTION get_detailed_plot_latest_version(p_detailed_plot_id VARCHAR(255))
RETURNS TABLE (
    id INTEGER,
    detailed_plot_id VARCHAR(255),
    version_type VARCHAR(50),
    version_number INTEGER,
    is_current_version BOOLEAN,
    title VARCHAR(500),
    content TEXT,
    word_count INTEGER,
    source_table VARCHAR(50),
    source_record_id VARCHAR(255),
    version_notes TEXT,
    created_by VARCHAR(50),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT dpv.id, dpv.detailed_plot_id, dpv.version_type, dpv.version_number,
           dpv.is_current_version, dpv.title, dpv.content, dpv.word_count,
           dpv.source_table, dpv.source_record_id, dpv.version_notes,
           dpv.created_by, dpv.created_at, dpv.updated_at
    FROM detailed_plot_versions dpv
    WHERE dpv.detailed_plot_id = p_detailed_plot_id 
      AND dpv.is_current_version = TRUE
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;

-- 6. 创建函数：获取详细剧情的所有版本
CREATE OR REPLACE FUNCTION get_detailed_plot_all_versions(p_detailed_plot_id VARCHAR(255))
RETURNS TABLE (
    id INTEGER,
    detailed_plot_id VARCHAR(255),
    version_type VARCHAR(50),
    version_number INTEGER,
    is_current_version BOOLEAN,
    title VARCHAR(500),
    content TEXT,
    word_count INTEGER,
    source_table VARCHAR(50),
    source_record_id VARCHAR(255),
    version_notes TEXT,
    created_by VARCHAR(50),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT dpv.id, dpv.detailed_plot_id, dpv.version_type, dpv.version_number,
           dpv.is_current_version, dpv.title, dpv.content, dpv.word_count,
           dpv.source_table, dpv.source_record_id, dpv.version_notes,
           dpv.created_by, dpv.created_at, dpv.updated_at
    FROM detailed_plot_versions dpv
    WHERE dpv.detailed_plot_id = p_detailed_plot_id
    ORDER BY 
        CASE dpv.version_type 
            WHEN 'correction' THEN 1
            WHEN 'evolution' THEN 2
            WHEN 'original' THEN 3
            ELSE 4
        END,
        dpv.version_number DESC,
        dpv.created_at DESC;
END;
$$ LANGUAGE plpgsql;

-- 7. 创建函数：设置详细剧情的当前版本
CREATE OR REPLACE FUNCTION set_detailed_plot_current_version(
    p_detailed_plot_id VARCHAR(255),
    p_version_record_id INTEGER
) RETURNS BOOLEAN AS $$
DECLARE
    version_exists BOOLEAN;
BEGIN
    -- 检查版本记录是否存在
    SELECT EXISTS(
        SELECT 1 FROM detailed_plot_versions 
        WHERE id = p_version_record_id 
          AND detailed_plot_id = p_detailed_plot_id
    ) INTO version_exists;
    
    IF NOT version_exists THEN
        RETURN FALSE;
    END IF;
    
    -- 先将该详细剧情的所有版本设为非当前版本
    UPDATE detailed_plot_versions 
    SET is_current_version = FALSE, updated_at = CURRENT_TIMESTAMP
    WHERE detailed_plot_id = p_detailed_plot_id;
    
    -- 设置指定版本为当前版本
    UPDATE detailed_plot_versions 
    SET is_current_version = TRUE, updated_at = CURRENT_TIMESTAMP
    WHERE id = p_version_record_id;
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- 8. 创建触发器：自动更新版本号
CREATE OR REPLACE FUNCTION update_version_number()
RETURNS TRIGGER AS $$
BEGIN
    -- 如果是新插入的记录，自动设置版本号
    IF TG_OP = 'INSERT' THEN
        SELECT COALESCE(MAX(version_number), 0) + 1
        INTO NEW.version_number
        FROM detailed_plot_versions
        WHERE detailed_plot_id = NEW.detailed_plot_id
          AND version_type = NEW.version_type;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_version_number
    BEFORE INSERT ON detailed_plot_versions
    FOR EACH ROW
    EXECUTE FUNCTION update_version_number();

-- 9. 创建视图：详细剧情与最新版本
CREATE OR REPLACE VIEW detailed_plots_with_latest_version AS
SELECT 
    dp.id as original_id,
    dp.chapter_outline_id,
    dp.plot_outline_id,
    dp.status,
    dp.logic_status,
    dp.logic_check_result,
    dp.scoring_status,
    dp.total_score,
    dp.scoring_result,
    dp.scoring_feedback,
    dp.scored_at,
    dp.scored_by,
    dp.created_at as original_created_at,
    dp.updated_at as original_updated_at,
    
    -- 最新版本信息
    dpv.id as current_version_id,
    dpv.version_type as current_version_type,
    dpv.version_number as current_version_number,
    dpv.title as current_title,
    dpv.content as current_content,
    dpv.word_count as current_word_count,
    dpv.source_table as current_source_table,
    dpv.source_record_id as current_source_record_id,
    dpv.version_notes as current_version_notes,
    dpv.created_by as current_created_by,
    dpv.created_at as current_created_at,
    dpv.updated_at as current_updated_at,
    
    -- 判断是否有版本记录
    CASE 
        WHEN dpv.id IS NOT NULL THEN TRUE 
        ELSE FALSE 
    END as has_version_record

FROM detailed_plots dp
LEFT JOIN detailed_plot_versions dpv ON (
    dp.id = dpv.detailed_plot_id 
    AND dpv.is_current_version = TRUE
);

-- 10. 添加注释
COMMENT ON VIEW detailed_plots_with_latest_version IS '详细剧情与最新版本视图';
COMMENT ON COLUMN detailed_plots_with_latest_version.original_id IS '原始详细剧情ID';
COMMENT ON COLUMN detailed_plots_with_latest_version.current_version_id IS '当前版本记录ID';
COMMENT ON COLUMN detailed_plots_with_latest_version.current_version_type IS '当前版本类型';
COMMENT ON COLUMN detailed_plots_with_latest_version.current_title IS '当前版本标题';
COMMENT ON COLUMN detailed_plots_with_latest_version.current_content IS '当前版本内容';
COMMENT ON COLUMN detailed_plots_with_latest_version.has_version_record IS '是否有版本记录';
