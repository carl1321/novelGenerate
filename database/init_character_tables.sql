-- 角色数据库表结构初始化脚本
-- PostgreSQL 17 兼容

-- 连接到数据库
-- \c novel_generate;

-- 创建角色类型枚举
CREATE TYPE character_role_type AS ENUM ('主角', '配角', '反派', '导师', '盟友', '路人');

-- 创建角色主表
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
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    status VARCHAR(50) DEFAULT 'active' -- active, archived, deleted
);

-- 创建角色性格特质表
CREATE TABLE IF NOT EXISTS character_personality_traits (
    id SERIAL PRIMARY KEY,
    character_id VARCHAR(255) NOT NULL REFERENCES characters(character_id) ON DELETE CASCADE,
    trait_name VARCHAR(50) NOT NULL,
    trait_value VARCHAR(100),
    intensity INTEGER DEFAULT 5 CHECK (intensity >= 1 AND intensity <= 10),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(character_id, trait_name)
);

-- 创建角色目标表
CREATE TABLE IF NOT EXISTS character_goals (
    id SERIAL PRIMARY KEY,
    character_id VARCHAR(255) NOT NULL REFERENCES characters(character_id) ON DELETE CASCADE,
    goal_type VARCHAR(50) NOT NULL,
    goal_description TEXT NOT NULL,
    priority INTEGER DEFAULT 5 CHECK (priority >= 1 AND priority <= 10),
    is_achieved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 创建角色关系表
CREATE TABLE IF NOT EXISTS character_relationships (
    id SERIAL PRIMARY KEY,
    character1_id VARCHAR(255) NOT NULL REFERENCES characters(character_id) ON DELETE CASCADE,
    character2_id VARCHAR(255) NOT NULL REFERENCES characters(character_id) ON DELETE CASCADE,
    relationship_type VARCHAR(50) NOT NULL,
    intimacy_level INTEGER DEFAULT 5 CHECK (intimacy_level >= 1 AND intimacy_level <= 10),
    trust_level INTEGER DEFAULT 5 CHECK (trust_level >= 1 AND trust_level <= 10),
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CHECK (character1_id != character2_id)
);

-- 创建角色技能表
CREATE TABLE IF NOT EXISTS character_techniques (
    id SERIAL PRIMARY KEY,
    character_id VARCHAR(255) NOT NULL REFERENCES characters(character_id) ON DELETE CASCADE,
    technique_name VARCHAR(200) NOT NULL,
    technique_description TEXT,
    technique_level INTEGER DEFAULT 1 CHECK (technique_level >= 1 AND technique_level <= 10),
    technique_type VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 创建角色法宝表
CREATE TABLE IF NOT EXISTS character_artifacts (
    id SERIAL PRIMARY KEY,
    character_id VARCHAR(255) NOT NULL REFERENCES characters(character_id) ON DELETE CASCADE,
    artifact_name VARCHAR(200) NOT NULL,
    artifact_description TEXT,
    artifact_grade VARCHAR(50),
    artifact_type VARCHAR(50),
    is_equipped BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 创建角色资源表
CREATE TABLE IF NOT EXISTS character_resources (
    id SERIAL PRIMARY KEY,
    character_id VARCHAR(255) NOT NULL REFERENCES characters(character_id) ON DELETE CASCADE,
    resource_name VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    quantity INTEGER DEFAULT 0 CHECK (quantity >= 0),
    unit VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(character_id, resource_name)
);

-- 创建角色属性表
CREATE TABLE IF NOT EXISTS character_stats (
    id SERIAL PRIMARY KEY,
    character_id VARCHAR(255) NOT NULL REFERENCES characters(character_id) ON DELETE CASCADE,
    stat_name VARCHAR(50) NOT NULL,
    stat_value INTEGER NOT NULL DEFAULT 0,
    stat_type VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(character_id, stat_name)
);

-- 创建角色元数据表
CREATE TABLE IF NOT EXISTS character_metadata (
    id SERIAL PRIMARY KEY,
    character_id VARCHAR(255) NOT NULL REFERENCES characters(character_id) ON DELETE CASCADE,
    metadata_key VARCHAR(100) NOT NULL,
    metadata_value JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(character_id, metadata_key)
);

-- 创建角色组表
CREATE TABLE IF NOT EXISTS character_groups (
    id SERIAL PRIMARY KEY,
    group_id VARCHAR(255) UNIQUE NOT NULL,
    group_name VARCHAR(200) NOT NULL,
    group_description TEXT,
    group_type VARCHAR(50) DEFAULT 'custom',
    worldview_id VARCHAR(255) NOT NULL REFERENCES worldviews(worldview_id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255)
);

-- 创建角色组成员关系表
CREATE TABLE IF NOT EXISTS character_group_members (
    id SERIAL PRIMARY KEY,
    group_id VARCHAR(255) NOT NULL REFERENCES character_groups(group_id) ON DELETE CASCADE,
    character_id VARCHAR(255) NOT NULL REFERENCES characters(character_id) ON DELETE CASCADE,
    role_in_group VARCHAR(100),
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(group_id, character_id)
);

-- 创建角色成长轨迹表
CREATE TABLE IF NOT EXISTS character_growth_tracks (
    id SERIAL PRIMARY KEY,
    character_id VARCHAR(255) NOT NULL REFERENCES characters(character_id) ON DELETE CASCADE,
    growth_node_id VARCHAR(255) NOT NULL,
    target_level VARCHAR(50),
    estimated_time INTEGER, -- 预计时间（年）
    requirements JSONB, -- 达成条件
    key_events JSONB, -- 关键事件
    rewards JSONB, -- 奖励
    risks JSONB, -- 风险
    is_completed BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 创建角色对话表
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

CREATE INDEX IF NOT EXISTS idx_character_personality_traits_character_id ON character_personality_traits(character_id);
CREATE INDEX IF NOT EXISTS idx_character_goals_character_id ON character_goals(character_id);
CREATE INDEX IF NOT EXISTS idx_character_goals_goal_type ON character_goals(goal_type);
CREATE INDEX IF NOT EXISTS idx_character_goals_is_achieved ON character_goals(is_achieved);

CREATE INDEX IF NOT EXISTS idx_character_relationships_character1_id ON character_relationships(character1_id);
CREATE INDEX IF NOT EXISTS idx_character_relationships_character2_id ON character_relationships(character2_id);
CREATE INDEX IF NOT EXISTS idx_character_relationships_type ON character_relationships(relationship_type);

CREATE INDEX IF NOT EXISTS idx_character_techniques_character_id ON character_techniques(character_id);
CREATE INDEX IF NOT EXISTS idx_character_artifacts_character_id ON character_artifacts(character_id);
CREATE INDEX IF NOT EXISTS idx_character_resources_character_id ON character_resources(character_id);
CREATE INDEX IF NOT EXISTS idx_character_stats_character_id ON character_stats(character_id);
CREATE INDEX IF NOT EXISTS idx_character_metadata_character_id ON character_metadata(character_id);

CREATE INDEX IF NOT EXISTS idx_character_groups_group_id ON character_groups(group_id);
CREATE INDEX IF NOT EXISTS idx_character_groups_worldview_id ON character_groups(worldview_id);
CREATE INDEX IF NOT EXISTS idx_character_group_members_group_id ON character_group_members(group_id);
CREATE INDEX IF NOT EXISTS idx_character_group_members_character_id ON character_group_members(character_id);

CREATE INDEX IF NOT EXISTS idx_character_growth_tracks_character_id ON character_growth_tracks(character_id);
CREATE INDEX IF NOT EXISTS idx_character_dialogues_character_id ON character_dialogues(character_id);

-- 创建JSONB字段的GIN索引
CREATE INDEX IF NOT EXISTS idx_character_growth_tracks_requirements ON character_growth_tracks USING GIN (requirements);
CREATE INDEX IF NOT EXISTS idx_character_growth_tracks_key_events ON character_growth_tracks USING GIN (key_events);
CREATE INDEX IF NOT EXISTS idx_character_growth_tracks_rewards ON character_growth_tracks USING GIN (rewards);
CREATE INDEX IF NOT EXISTS idx_character_growth_tracks_risks ON character_growth_tracks USING GIN (risks);
CREATE INDEX IF NOT EXISTS idx_character_metadata_value ON character_metadata USING GIN (metadata_value);

-- 为所有表添加更新时间触发器
CREATE TRIGGER update_characters_updated_at BEFORE UPDATE ON characters
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_character_goals_updated_at BEFORE UPDATE ON character_goals
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_character_relationships_updated_at BEFORE UPDATE ON character_relationships
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_character_techniques_updated_at BEFORE UPDATE ON character_techniques
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_character_artifacts_updated_at BEFORE UPDATE ON character_artifacts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_character_resources_updated_at BEFORE UPDATE ON character_resources
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_character_stats_updated_at BEFORE UPDATE ON character_stats
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_character_metadata_updated_at BEFORE UPDATE ON character_metadata
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_character_groups_updated_at BEFORE UPDATE ON character_groups
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_character_growth_tracks_updated_at BEFORE UPDATE ON character_growth_tracks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 创建视图：完整的角色信息
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
    c.created_at,
    c.updated_at,
    c.created_by,
    c.status,
    -- 聚合性格特质
    COALESCE(
        json_agg(
            DISTINCT jsonb_build_object(
                'trait_name', pt.trait_name,
                'trait_value', pt.trait_value,
                'intensity', pt.intensity
            )
        ) FILTER (WHERE pt.trait_name IS NOT NULL),
        '[]'::json
    ) as personality_traits,
    -- 聚合目标
    COALESCE(
        json_agg(
            DISTINCT jsonb_build_object(
                'goal_type', g.goal_type,
                'goal_description', g.goal_description,
                'priority', g.priority,
                'is_achieved', g.is_achieved
            )
        ) FILTER (WHERE g.goal_type IS NOT NULL),
        '[]'::json
    ) as goals,
    -- 聚合技能
    COALESCE(
        json_agg(
            DISTINCT jsonb_build_object(
                'technique_name', t.technique_name,
                'technique_description', t.technique_description,
                'technique_level', t.technique_level,
                'technique_type', t.technique_type
            )
        ) FILTER (WHERE t.technique_name IS NOT NULL),
        '[]'::json
    ) as techniques,
    -- 聚合法宝
    COALESCE(
        json_agg(
            DISTINCT jsonb_build_object(
                'artifact_name', a.artifact_name,
                'artifact_description', a.artifact_description,
                'artifact_grade', a.artifact_grade,
                'artifact_type', a.artifact_type,
                'is_equipped', a.is_equipped
            )
        ) FILTER (WHERE a.artifact_name IS NOT NULL),
        '[]'::json
    ) as artifacts,
    -- 聚合资源
    COALESCE(
        json_agg(
            DISTINCT jsonb_build_object(
                'resource_name', r.resource_name,
                'resource_type', r.resource_type,
                'quantity', r.quantity,
                'unit', r.unit
            )
        ) FILTER (WHERE r.resource_name IS NOT NULL),
        '[]'::json
    ) as resources,
    -- 聚合属性
    COALESCE(
        json_agg(
            DISTINCT jsonb_build_object(
                'stat_name', s.stat_name,
                'stat_value', s.stat_value,
                'stat_type', s.stat_type
            )
        ) FILTER (WHERE s.stat_name IS NOT NULL),
        '{}'::json
    ) as stats
FROM characters c
LEFT JOIN character_personality_traits pt ON c.character_id = pt.character_id
LEFT JOIN character_goals g ON c.character_id = g.character_id
LEFT JOIN character_techniques t ON c.character_id = t.character_id
LEFT JOIN character_artifacts a ON c.character_id = a.character_id
LEFT JOIN character_resources r ON c.character_id = r.character_id
LEFT JOIN character_stats s ON c.character_id = s.character_id
GROUP BY c.id, c.character_id, c.worldview_id, c.name, c.age, c.gender, 
         c.role_type, c.cultivation_level, c.element_type, c.background, 
         c.current_location, c.organization_id, c.created_at, c.updated_at, 
         c.created_by, c.status;

-- 创建存储过程：批量创建角色
CREATE OR REPLACE FUNCTION create_characters_batch(
    p_worldview_id VARCHAR(255),
    p_character_descriptions JSONB,
    p_created_by VARCHAR(255) DEFAULT 'system'
) RETURNS JSONB AS $$
DECLARE
    char_desc JSONB;
    char_id VARCHAR(255);
    result JSONB := '[]'::jsonb;
    char_record RECORD;
BEGIN
    -- 遍历角色描述数组
    FOR char_desc IN SELECT * FROM jsonb_array_elements(p_character_descriptions)
    LOOP
        -- 生成角色ID
        char_id := 'char_' || extract(epoch from now())::bigint || '_' || floor(random() * 10000)::int;
        
        -- 插入角色主记录
        INSERT INTO characters (
            character_id, worldview_id, name, age, gender, role_type,
            cultivation_level, element_type, background, created_by
        ) VALUES (
            char_id,
            p_worldview_id,
            char_desc->>'name',
            (char_desc->>'age')::integer,
            char_desc->>'gender',
            COALESCE(char_desc->>'role_type', '配角')::character_role_type,
            char_desc->>'cultivation_level',
            char_desc->>'element_type',
            char_desc->>'background',
            p_created_by
        ) RETURNING * INTO char_record;
        
        -- 添加角色ID到结果
        result := result || jsonb_build_object('character_id', char_id, 'name', char_record.name);
        
        -- 插入性格特质
        IF char_desc ? 'personality_traits' THEN
            INSERT INTO character_personality_traits (character_id, trait_name, trait_value, intensity)
            SELECT 
                char_id,
                trait->>'trait_name',
                trait->>'trait_value',
                COALESCE((trait->>'intensity')::integer, 5)
            FROM jsonb_array_elements(char_desc->'personality_traits') as trait;
        END IF;
        
        -- 插入目标
        IF char_desc ? 'goals' THEN
            INSERT INTO character_goals (character_id, goal_type, goal_description, priority)
            SELECT 
                char_id,
                goal->>'goal_type',
                goal->>'goal_description',
                COALESCE((goal->>'priority')::integer, 5)
            FROM jsonb_array_elements(char_desc->'goals') as goal;
        END IF;
        
        -- 插入技能
        IF char_desc ? 'techniques' THEN
            INSERT INTO character_techniques (character_id, technique_name, technique_description, technique_level, technique_type)
            SELECT 
                char_id,
                tech->>'technique_name',
                tech->>'technique_description',
                COALESCE((tech->>'technique_level')::integer, 1),
                tech->>'technique_type'
            FROM jsonb_array_elements(char_desc->'techniques') as tech;
        END IF;
        
        -- 插入属性
        IF char_desc ? 'stats' THEN
            INSERT INTO character_stats (character_id, stat_name, stat_value, stat_type)
            SELECT 
                char_id,
                stat_key,
                (stat_value)::integer,
                'base'
            FROM jsonb_each_text(char_desc->'stats') as stat(stat_key, stat_value);
        END IF;
    END LOOP;
    
    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- 创建存储过程：根据角色类型统计
CREATE OR REPLACE FUNCTION get_character_stats_by_type(
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

-- 添加注释
COMMENT ON TABLE characters IS '角色主表，存储角色的基本信息';
COMMENT ON TABLE character_personality_traits IS '角色性格特质表，存储角色的性格特征';
COMMENT ON TABLE character_goals IS '角色目标表，存储角色的各种目标';
COMMENT ON TABLE character_relationships IS '角色关系表，存储角色之间的关系';
COMMENT ON TABLE character_techniques IS '角色技能表，存储角色掌握的技能';
COMMENT ON TABLE character_artifacts IS '角色法宝表，存储角色拥有的法宝';
COMMENT ON TABLE character_resources IS '角色资源表，存储角色的各种资源';
COMMENT ON TABLE character_stats IS '角色属性表，存储角色的数值属性';
COMMENT ON TABLE character_metadata IS '角色元数据表，存储角色的扩展信息';
COMMENT ON TABLE character_groups IS '角色组表，存储角色分组信息';
COMMENT ON TABLE character_group_members IS '角色组成员关系表';
COMMENT ON TABLE character_growth_tracks IS '角色成长轨迹表，存储角色的成长规划';
COMMENT ON TABLE character_dialogues IS '角色对话表，存储角色的对话记录';

COMMENT ON FUNCTION create_characters_batch IS '批量创建角色';
COMMENT ON FUNCTION get_character_stats_by_type IS '根据角色类型统计角色数量';
COMMENT ON VIEW character_complete IS '完整的角色信息视图';

-- 显示创建结果
SELECT 'Character database tables created successfully!' as status;
