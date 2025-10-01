-- 角色数据库表结构初始化脚本（简化版）
-- PostgreSQL 17 兼容

-- 连接到数据库
-- \c novel_generate;

-- 创建角色类型枚举
CREATE TYPE character_role_type AS ENUM ('主角', '配角', '反派', '导师', '盟友', '路人');

-- 创建角色主表（简化版，使用JSONB存储非结构化数据）
CREATE TABLE IF NOT EXISTS characters (
    id SERIAL PRIMARY KEY,
    character_id VARCHAR(255) UNIQUE NOT NULL,
    worldview_id VARCHAR(255) NOT NULL REFERENCES worldviews(worldview_id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    age INTEGER NOT NULL CHECK (age >= 0),
    gender VARCHAR(10) NOT NULL CHECK (gender IN ('男', '女', '其他')),
    role_type character_role_type NOT NULL DEFAULT '配角',
    cultivation_level VARCHAR(50),
    element_type VARCHAR(50),
    background TEXT,
    current_location VARCHAR(255),
    organization_id VARCHAR(255),
    
    -- 使用JSONB存储非结构化数据
    personality_traits JSONB DEFAULT '[]'::jsonb,  -- 性格特质
    goals JSONB DEFAULT '[]'::jsonb,              -- 目标列表
    relationships JSONB DEFAULT '{}'::jsonb,      -- 人际关系
    techniques JSONB DEFAULT '[]'::jsonb,         -- 技能列表
    artifacts JSONB DEFAULT '[]'::jsonb,          -- 法宝列表
    resources JSONB DEFAULT '{}'::jsonb,          -- 资源
    stats JSONB DEFAULT '{}'::jsonb,              -- 属性数值
    metadata JSONB DEFAULT '{}'::jsonb,           -- 扩展元数据
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    status VARCHAR(50) DEFAULT 'active' -- active, archived, deleted
);

-- 创建角色组表（简化版）
CREATE TABLE IF NOT EXISTS character_groups (
    id SERIAL PRIMARY KEY,
    group_id VARCHAR(255) UNIQUE NOT NULL,
    group_name VARCHAR(200) NOT NULL,
    group_description TEXT,
    group_type VARCHAR(50) DEFAULT 'custom',
    worldview_id VARCHAR(255) NOT NULL REFERENCES worldviews(worldview_id) ON DELETE CASCADE,
    character_ids JSONB DEFAULT '[]'::jsonb,  -- 角色ID列表
    common_goals JSONB DEFAULT '[]'::jsonb,   -- 共同目标
    internal_conflicts JSONB DEFAULT '[]'::jsonb,  -- 内部冲突
    external_enemies JSONB DEFAULT '[]'::jsonb,    -- 外部敌人
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255)
);

-- 创建角色对话表（保留，因为对话数据量大）
CREATE TABLE IF NOT EXISTS character_dialogues (
    id SERIAL PRIMARY KEY,
    character_id VARCHAR(255) NOT NULL REFERENCES characters(character_id) ON DELETE CASCADE,
    situation VARCHAR(200) NOT NULL,
    dialogue_content TEXT NOT NULL,
    dialogue_type VARCHAR(50) DEFAULT 'normal', -- normal, internal_monologue, action
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引以提高查询性能
CREATE INDEX IF NOT EXISTS idx_characters_character_id ON characters(character_id);
CREATE INDEX IF NOT EXISTS idx_characters_worldview_id ON characters(worldview_id);
CREATE INDEX IF NOT EXISTS idx_characters_name ON characters(name);
CREATE INDEX IF NOT EXISTS idx_characters_role_type ON characters(role_type);
CREATE INDEX IF NOT EXISTS idx_characters_created_at ON characters(created_at);
CREATE INDEX IF NOT EXISTS idx_characters_status ON characters(status);

CREATE INDEX IF NOT EXISTS idx_character_groups_group_id ON character_groups(group_id);
CREATE INDEX IF NOT EXISTS idx_character_groups_worldview_id ON character_groups(worldview_id);
CREATE INDEX IF NOT EXISTS idx_character_dialogues_character_id ON character_dialogues(character_id);

-- 创建JSONB字段的GIN索引以提高JSON查询性能
CREATE INDEX IF NOT EXISTS idx_characters_personality_traits ON characters USING GIN (personality_traits);
CREATE INDEX IF NOT EXISTS idx_characters_goals ON characters USING GIN (goals);
CREATE INDEX IF NOT EXISTS idx_characters_relationships ON characters USING GIN (relationships);
CREATE INDEX IF NOT EXISTS idx_characters_techniques ON characters USING GIN (techniques);
CREATE INDEX IF NOT EXISTS idx_characters_artifacts ON characters USING GIN (artifacts);
CREATE INDEX IF NOT EXISTS idx_characters_resources ON characters USING GIN (resources);
CREATE INDEX IF NOT EXISTS idx_characters_stats ON characters USING GIN (stats);
CREATE INDEX IF NOT EXISTS idx_characters_metadata ON characters USING GIN (metadata);

CREATE INDEX IF NOT EXISTS idx_character_groups_character_ids ON character_groups USING GIN (character_ids);
CREATE INDEX IF NOT EXISTS idx_character_groups_common_goals ON character_groups USING GIN (common_goals);

-- 为所有表添加更新时间触发器
CREATE TRIGGER update_characters_updated_at BEFORE UPDATE ON characters
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_character_groups_updated_at BEFORE UPDATE ON character_groups
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 创建视图：完整的角色信息（简化版）
CREATE OR REPLACE VIEW character_complete AS
SELECT 
    c.id,
    c.character_id,
    c.worldview_id,
    c.name,
    c.age,
    c.gender,
    c.role_type,
    c.cultivation_level,
    c.element_type,
    c.background,
    c.current_location,
    c.organization_id,
    c.personality_traits,
    c.goals,
    c.relationships,
    c.techniques,
    c.artifacts,
    c.resources,
    c.stats,
    c.metadata,
    c.created_at,
    c.updated_at,
    c.created_by,
    c.status
FROM characters c;

-- 创建存储过程：批量创建角色（简化版）
CREATE OR REPLACE FUNCTION create_characters_batch_simple(
    p_worldview_id VARCHAR(255),
    p_characters_data JSONB,
    p_created_by VARCHAR(255) DEFAULT 'system'
) RETURNS JSONB AS $$
DECLARE
    char_data JSONB;
    char_id VARCHAR(255);
    result JSONB := '[]'::jsonb;
    char_record RECORD;
BEGIN
    -- 遍历角色数据数组
    FOR char_data IN SELECT * FROM jsonb_array_elements(p_characters_data)
    LOOP
        -- 生成角色ID
        char_id := 'char_' || extract(epoch from now())::bigint || '_' || floor(random() * 10000)::int;
        
        -- 插入角色记录
        INSERT INTO characters (
            character_id, worldview_id, name, age, gender, role_type,
            cultivation_level, element_type, background, current_location,
            organization_id, personality_traits, goals, relationships,
            techniques, artifacts, resources, stats, metadata, created_by
        ) VALUES (
            char_id,
            p_worldview_id,
            char_data->>'name',
            (char_data->>'age')::integer,
            char_data->>'gender',
            COALESCE(char_data->>'role_type', '配角')::character_role_type,
            char_data->>'cultivation_level',
            char_data->>'element_type',
            char_data->>'background',
            char_data->>'current_location',
            char_data->>'organization_id',
            COALESCE(char_data->'personality_traits', '[]'::jsonb),
            COALESCE(char_data->'goals', '[]'::jsonb),
            COALESCE(char_data->'relationships', '{}'::jsonb),
            COALESCE(char_data->'techniques', '[]'::jsonb),
            COALESCE(char_data->'artifacts', '[]'::jsonb),
            COALESCE(char_data->'resources', '{}'::jsonb),
            COALESCE(char_data->'stats', '{}'::jsonb),
            COALESCE(char_data->'metadata', '{}'::jsonb),
            p_created_by
        ) RETURNING character_id, name INTO char_record;
        
        -- 添加角色ID到结果
        result := result || jsonb_build_object('character_id', char_record.character_id, 'name', char_record.name);
    END LOOP;
    
    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- 创建存储过程：根据角色类型统计（简化版）
CREATE OR REPLACE FUNCTION get_character_stats_by_type_simple(
    p_worldview_id VARCHAR(255)
) RETURNS JSONB AS $$
DECLARE
    result JSONB;
BEGIN
    SELECT jsonb_object_agg(role_type, count) INTO result
    FROM (
        SELECT role_type, COUNT(*) as count
        FROM characters 
        WHERE worldview_id = p_worldview_id AND status = 'active'
        GROUP BY role_type
    ) as stats;
    
    RETURN COALESCE(result, '{}'::jsonb);
END;
$$ LANGUAGE plpgsql;

-- 创建存储过程：搜索角色（简化版）
CREATE OR REPLACE FUNCTION search_characters_simple(
    p_worldview_id VARCHAR(255),
    p_keyword VARCHAR(255) DEFAULT NULL,
    p_role_type VARCHAR(20) DEFAULT NULL,
    p_limit INTEGER DEFAULT 50
) RETURNS JSONB AS $$
DECLARE
    result JSONB;
    where_clause TEXT := 'WHERE worldview_id = $1 AND status = ''active''';
    query_params TEXT[] := ARRAY[p_worldview_id];
    param_count INTEGER := 1;
BEGIN
    -- 构建动态WHERE子句
    IF p_keyword IS NOT NULL THEN
        param_count := param_count + 1;
        where_clause := where_clause || ' AND (name ILIKE $' || param_count || ' OR background ILIKE $' || param_count || ')';
        query_params := array_append(query_params, '%' || p_keyword || '%');
    END IF;
    
    IF p_role_type IS NOT NULL THEN
        param_count := param_count + 1;
        where_clause := where_clause || ' AND role_type = $' || param_count;
        query_params := array_append(query_params, p_role_type);
    END IF;
    
    -- 执行查询
    EXECUTE 'SELECT jsonb_agg(
        jsonb_build_object(
            ''character_id'', character_id,
            ''name'', name,
            ''age'', age,
            ''gender'', gender,
            ''role_type'', role_type,
            ''cultivation_level'', cultivation_level,
            ''element_type'', element_type,
            ''background'', background,
            ''personality_traits'', personality_traits,
            ''goals'', goals,
            ''relationships'', relationships,
            ''techniques'', techniques,
            ''artifacts'', artifacts,
            ''resources'', resources,
            ''stats'', stats,
            ''metadata'', metadata,
            ''created_at'', created_at
        )
    ) FROM characters ' || where_clause || ' LIMIT ' || p_limit
    USING query_params
    INTO result;
    
    RETURN COALESCE(result, '[]'::jsonb);
END;
$$ LANGUAGE plpgsql;

-- 添加注释
COMMENT ON TABLE characters IS '角色主表，存储角色的完整信息（简化版）';
COMMENT ON TABLE character_groups IS '角色组表，存储角色分组信息';
COMMENT ON TABLE character_dialogues IS '角色对话表，存储角色的对话记录';

COMMENT ON FUNCTION create_characters_batch_simple IS '批量创建角色（简化版）';
COMMENT ON FUNCTION get_character_stats_by_type_simple IS '根据角色类型统计角色数量（简化版）';
COMMENT ON FUNCTION search_characters_simple IS '搜索角色（简化版）';
COMMENT ON VIEW character_complete IS '完整的角色信息视图（简化版）';

-- 显示创建结果
SELECT 'Character database tables created successfully (Simplified Version)!' as status;
