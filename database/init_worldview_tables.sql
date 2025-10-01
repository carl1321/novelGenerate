-- 世界观数据库表结构初始化脚本
-- PostgreSQL 17 兼容

-- 创建数据库（如果不存在）
-- CREATE DATABASE novel_generate;

-- 连接到数据库
-- \c novel_generate;

-- 创建世界观主表
CREATE TABLE IF NOT EXISTS worldviews (
    id SERIAL PRIMARY KEY,
    worldview_id VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(500) NOT NULL,
    description TEXT,
    core_concept TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    version INTEGER DEFAULT 1,
    status VARCHAR(50) DEFAULT 'active' -- active, archived, deleted
);

-- 创建力量体系表
CREATE TABLE IF NOT EXISTS power_systems (
    id SERIAL PRIMARY KEY,
    worldview_id VARCHAR(255) NOT NULL REFERENCES worldviews(worldview_id) ON DELETE CASCADE,
    cultivation_realms JSONB, -- 修炼境界数组
    energy_types JSONB, -- 能量类型数组
    technique_categories JSONB, -- 功法类别数组
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(worldview_id)
);

-- 创建地理设定表
CREATE TABLE IF NOT EXISTS geographies (
    id SERIAL PRIMARY KEY,
    worldview_id VARCHAR(255) NOT NULL REFERENCES worldviews(worldview_id) ON DELETE CASCADE,
    main_regions JSONB, -- 主要区域数组
    special_locations JSONB, -- 特殊地点数组
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(worldview_id)
);

-- 创建社会组织表
CREATE TABLE IF NOT EXISTS societies (
    id SERIAL PRIMARY KEY,
    worldview_id VARCHAR(255) NOT NULL REFERENCES worldviews(worldview_id) ON DELETE CASCADE,
    organizations JSONB, -- 组织数组
    social_system JSONB, -- 社会系统对象
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(worldview_id)
);

-- 创建历史文化表
CREATE TABLE IF NOT EXISTS history_cultures (
    id SERIAL PRIMARY KEY,
    worldview_id VARCHAR(255) NOT NULL REFERENCES worldviews(worldview_id) ON DELETE CASCADE,
    historical_events JSONB, -- 历史事件数组
    cultural_features JSONB, -- 文化特色数组
    current_conflicts JSONB, -- 当前冲突数组
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(worldview_id)
);

-- 创建世界观元数据表（用于存储额外的元信息）
CREATE TABLE IF NOT EXISTS worldview_metadata (
    id SERIAL PRIMARY KEY,
    worldview_id VARCHAR(255) NOT NULL REFERENCES worldviews(worldview_id) ON DELETE CASCADE,
    metadata_key VARCHAR(255) NOT NULL,
    metadata_value JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(worldview_id, metadata_key)
);

-- 创建索引以提高查询性能
CREATE INDEX IF NOT EXISTS idx_worldviews_worldview_id ON worldviews(worldview_id);
CREATE INDEX IF NOT EXISTS idx_worldviews_name ON worldviews(name);
CREATE INDEX IF NOT EXISTS idx_worldviews_created_at ON worldviews(created_at);
CREATE INDEX IF NOT EXISTS idx_worldviews_status ON worldviews(status);

CREATE INDEX IF NOT EXISTS idx_power_systems_worldview_id ON power_systems(worldview_id);
CREATE INDEX IF NOT EXISTS idx_geographies_worldview_id ON geographies(worldview_id);
CREATE INDEX IF NOT EXISTS idx_societies_worldview_id ON societies(worldview_id);
CREATE INDEX IF NOT EXISTS idx_history_cultures_worldview_id ON history_cultures(worldview_id);
CREATE INDEX IF NOT EXISTS idx_worldview_metadata_worldview_id ON worldview_metadata(worldview_id);

-- 创建JSONB字段的GIN索引以提高JSON查询性能
CREATE INDEX IF NOT EXISTS idx_power_systems_cultivation_realms ON power_systems USING GIN (cultivation_realms);
CREATE INDEX IF NOT EXISTS idx_power_systems_energy_types ON power_systems USING GIN (energy_types);
CREATE INDEX IF NOT EXISTS idx_power_systems_technique_categories ON power_systems USING GIN (technique_categories);

CREATE INDEX IF NOT EXISTS idx_geographies_main_regions ON geographies USING GIN (main_regions);
CREATE INDEX IF NOT EXISTS idx_geographies_special_locations ON geographies USING GIN (special_locations);

CREATE INDEX IF NOT EXISTS idx_societies_organizations ON societies USING GIN (organizations);
CREATE INDEX IF NOT EXISTS idx_societies_social_system ON societies USING GIN (social_system);

CREATE INDEX IF NOT EXISTS idx_history_cultures_historical_events ON history_cultures USING GIN (historical_events);
CREATE INDEX IF NOT EXISTS idx_history_cultures_cultural_features ON history_cultures USING GIN (cultural_features);
CREATE INDEX IF NOT EXISTS idx_history_cultures_current_conflicts ON history_cultures USING GIN (current_conflicts);

CREATE INDEX IF NOT EXISTS idx_worldview_metadata_value ON worldview_metadata USING GIN (metadata_value);

-- 创建更新时间触发器函数
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 为所有表添加更新时间触发器
CREATE TRIGGER update_worldviews_updated_at BEFORE UPDATE ON worldviews
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_power_systems_updated_at BEFORE UPDATE ON power_systems
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_geographies_updated_at BEFORE UPDATE ON geographies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_societies_updated_at BEFORE UPDATE ON societies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_history_cultures_updated_at BEFORE UPDATE ON history_cultures
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_worldview_metadata_updated_at BEFORE UPDATE ON worldview_metadata
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 创建视图：完整的世界观信息
CREATE OR REPLACE VIEW worldview_complete AS
SELECT 
    w.id,
    w.worldview_id,
    w.name,
    w.description,
    w.core_concept,
    w.created_at,
    w.updated_at,
    w.created_by,
    w.version,
    w.status,
    ps.cultivation_realms,
    ps.energy_types,
    ps.technique_categories,
    g.main_regions,
    g.special_locations,
    s.organizations,
    s.social_system,
    hc.historical_events,
    hc.cultural_features,
    hc.current_conflicts
FROM worldviews w
LEFT JOIN power_systems ps ON w.worldview_id = ps.worldview_id
LEFT JOIN geographies g ON w.worldview_id = g.worldview_id
LEFT JOIN societies s ON w.worldview_id = s.worldview_id
LEFT JOIN history_cultures hc ON w.worldview_id = hc.worldview_id;

-- 插入示例数据（可选）
-- INSERT INTO worldviews (worldview_id, name, description, core_concept, created_by) 
-- VALUES ('test_world_001', '测试世界观', '这是一个测试世界观', '测试核心概念', 'system');

-- 创建存储过程：插入完整的世界观数据
CREATE OR REPLACE FUNCTION insert_worldview_complete(
    p_worldview_id VARCHAR(255),
    p_name VARCHAR(500),
    p_description TEXT,
    p_core_concept TEXT,
    p_created_by VARCHAR(255),
    p_cultivation_realms JSONB DEFAULT NULL,
    p_energy_types JSONB DEFAULT NULL,
    p_technique_categories JSONB DEFAULT NULL,
    p_main_regions JSONB DEFAULT NULL,
    p_special_locations JSONB DEFAULT NULL,
    p_organizations JSONB DEFAULT NULL,
    p_social_system JSONB DEFAULT NULL,
    p_historical_events JSONB DEFAULT NULL,
    p_cultural_features JSONB DEFAULT NULL,
    p_current_conflicts JSONB DEFAULT NULL
) RETURNS INTEGER AS $$
DECLARE
    worldview_pk INTEGER;
BEGIN
    -- 插入主表
    INSERT INTO worldviews (worldview_id, name, description, core_concept, created_by)
    VALUES (p_worldview_id, p_name, p_description, p_core_concept, p_created_by)
    RETURNING id INTO worldview_pk;
    
    -- 插入力量体系
    IF p_cultivation_realms IS NOT NULL OR p_energy_types IS NOT NULL OR p_technique_categories IS NOT NULL THEN
        INSERT INTO power_systems (worldview_id, cultivation_realms, energy_types, technique_categories)
        VALUES (p_worldview_id, p_cultivation_realms, p_energy_types, p_technique_categories);
    END IF;
    
    -- 插入地理设定
    IF p_main_regions IS NOT NULL OR p_special_locations IS NOT NULL THEN
        INSERT INTO geographies (worldview_id, main_regions, special_locations)
        VALUES (p_worldview_id, p_main_regions, p_special_locations);
    END IF;
    
    -- 插入社会组织
    IF p_organizations IS NOT NULL OR p_social_system IS NOT NULL THEN
        INSERT INTO societies (worldview_id, organizations, social_system)
        VALUES (p_worldview_id, p_organizations, p_social_system);
    END IF;
    
    -- 插入历史文化
    IF p_historical_events IS NOT NULL OR p_cultural_features IS NOT NULL OR p_current_conflicts IS NOT NULL THEN
        INSERT INTO history_cultures (worldview_id, historical_events, cultural_features, current_conflicts)
        VALUES (p_worldview_id, p_historical_events, p_cultural_features, p_current_conflicts);
    END IF;
    
    RETURN worldview_pk;
END;
$$ LANGUAGE plpgsql;

-- 创建存储过程：更新完整的世界观数据
CREATE OR REPLACE FUNCTION update_worldview_complete(
    p_worldview_id VARCHAR(255),
    p_name VARCHAR(500) DEFAULT NULL,
    p_description TEXT DEFAULT NULL,
    p_core_concept TEXT DEFAULT NULL,
    p_cultivation_realms JSONB DEFAULT NULL,
    p_energy_types JSONB DEFAULT NULL,
    p_technique_categories JSONB DEFAULT NULL,
    p_main_regions JSONB DEFAULT NULL,
    p_special_locations JSONB DEFAULT NULL,
    p_organizations JSONB DEFAULT NULL,
    p_social_system JSONB DEFAULT NULL,
    p_historical_events JSONB DEFAULT NULL,
    p_cultural_features JSONB DEFAULT NULL,
    p_current_conflicts JSONB DEFAULT NULL
) RETURNS BOOLEAN AS $$
BEGIN
    -- 更新主表
    IF p_name IS NOT NULL OR p_description IS NOT NULL OR p_core_concept IS NOT NULL THEN
        UPDATE worldviews 
        SET 
            name = COALESCE(p_name, name),
            description = COALESCE(p_description, description),
            core_concept = COALESCE(p_core_concept, core_concept),
            version = version + 1
        WHERE worldview_id = p_worldview_id;
    END IF;
    
    -- 更新力量体系
    IF p_cultivation_realms IS NOT NULL OR p_energy_types IS NOT NULL OR p_technique_categories IS NOT NULL THEN
        INSERT INTO power_systems (worldview_id, cultivation_realms, energy_types, technique_categories)
        VALUES (p_worldview_id, p_cultivation_realms, p_energy_types, p_technique_categories)
        ON CONFLICT (worldview_id) DO UPDATE SET
            cultivation_realms = COALESCE(p_cultivation_realms, power_systems.cultivation_realms),
            energy_types = COALESCE(p_energy_types, power_systems.energy_types),
            technique_categories = COALESCE(p_technique_categories, power_systems.technique_categories);
    END IF;
    
    -- 更新地理设定
    IF p_main_regions IS NOT NULL OR p_special_locations IS NOT NULL THEN
        INSERT INTO geographies (worldview_id, main_regions, special_locations)
        VALUES (p_worldview_id, p_main_regions, p_special_locations)
        ON CONFLICT (worldview_id) DO UPDATE SET
            main_regions = COALESCE(p_main_regions, geographies.main_regions),
            special_locations = COALESCE(p_special_locations, geographies.special_locations);
    END IF;
    
    -- 更新社会组织
    IF p_organizations IS NOT NULL OR p_social_system IS NOT NULL THEN
        INSERT INTO societies (worldview_id, organizations, social_system)
        VALUES (p_worldview_id, p_organizations, p_social_system)
        ON CONFLICT (worldview_id) DO UPDATE SET
            organizations = COALESCE(p_organizations, societies.organizations),
            social_system = COALESCE(p_social_system, societies.social_system);
    END IF;
    
    -- 更新历史文化
    IF p_historical_events IS NOT NULL OR p_cultural_features IS NOT NULL OR p_current_conflicts IS NOT NULL THEN
        INSERT INTO history_cultures (worldview_id, historical_events, cultural_features, current_conflicts)
        VALUES (p_worldview_id, p_historical_events, p_cultural_features, p_current_conflicts)
        ON CONFLICT (worldview_id) DO UPDATE SET
            historical_events = COALESCE(p_historical_events, history_cultures.historical_events),
            cultural_features = COALESCE(p_cultural_features, history_cultures.cultural_features),
            current_conflicts = COALESCE(p_current_conflicts, history_cultures.current_conflicts);
    END IF;
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- 添加注释
COMMENT ON TABLE worldviews IS '世界观主表，存储基本信息';
COMMENT ON TABLE power_systems IS '力量体系表，存储修炼境界、能量类型、功法类别';
COMMENT ON TABLE geographies IS '地理设定表，存储主要区域和特殊地点';
COMMENT ON TABLE societies IS '社会组织表，存储组织和社会系统信息';
COMMENT ON TABLE history_cultures IS '历史文化表，存储历史事件、文化特色、当前冲突';
COMMENT ON TABLE worldview_metadata IS '世界观元数据表，存储额外的元信息';

COMMENT ON FUNCTION insert_worldview_complete IS '插入完整的世界观数据';
COMMENT ON FUNCTION update_worldview_complete IS '更新完整的世界观数据';
COMMENT ON VIEW worldview_complete IS '完整的世界观信息视图';

-- 创建角色相关表

-- 角色主表
CREATE TABLE IF NOT EXISTS characters (
    id SERIAL PRIMARY KEY,
    character_id VARCHAR(255) UNIQUE NOT NULL,
    worldview_id VARCHAR(255) NOT NULL REFERENCES worldviews(worldview_id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    age INTEGER,
    gender VARCHAR(50), -- 男, 女, 其他
    role_type VARCHAR(50) NOT NULL, -- 主角, 配角, 反派, 导师, 盟友, 路人
    cultivation_level VARCHAR(255), -- 修炼境界
    element_type VARCHAR(255), -- 元素类型
    background TEXT, -- 背景故事
    current_location VARCHAR(255), -- 当前位置
    organization_id VARCHAR(255), -- 所属组织ID
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    status VARCHAR(50) DEFAULT 'active' -- active, archived, deleted
);

-- 角色性格特质表（JSONB存储）
CREATE TABLE IF NOT EXISTS character_personality_traits (
    id SERIAL PRIMARY KEY,
    character_id VARCHAR(255) NOT NULL REFERENCES characters(character_id) ON DELETE CASCADE,
    personality_traits JSONB, -- 性格特质数组
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(character_id)
);

-- 角色目标表（JSONB存储）
CREATE TABLE IF NOT EXISTS character_goals (
    id SERIAL PRIMARY KEY,
    character_id VARCHAR(255) NOT NULL REFERENCES characters(character_id) ON DELETE CASCADE,
    goals JSONB, -- 目标数组
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(character_id)
);

-- 角色关系表（JSONB存储）
CREATE TABLE IF NOT EXISTS character_relationships (
    id SERIAL PRIMARY KEY,
    character_id VARCHAR(255) NOT NULL REFERENCES characters(character_id) ON DELETE CASCADE,
    relationships JSONB, -- 关系映射
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(character_id)
);

-- 角色技能表（JSONB存储）
CREATE TABLE IF NOT EXISTS character_techniques (
    id SERIAL PRIMARY KEY,
    character_id VARCHAR(255) NOT NULL REFERENCES characters(character_id) ON DELETE CASCADE,
    techniques JSONB, -- 技能数组
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(character_id)
);

-- 角色法宝表（JSONB存储）
CREATE TABLE IF NOT EXISTS character_artifacts (
    id SERIAL PRIMARY KEY,
    character_id VARCHAR(255) NOT NULL REFERENCES characters(character_id) ON DELETE CASCADE,
    artifacts JSONB, -- 法宝数组
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(character_id)
);

-- 角色资源表（JSONB存储）
CREATE TABLE IF NOT EXISTS character_resources (
    id SERIAL PRIMARY KEY,
    character_id VARCHAR(255) NOT NULL REFERENCES characters(character_id) ON DELETE CASCADE,
    resources JSONB, -- 资源映射
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(character_id)
);

-- 角色属性表（JSONB存储）
CREATE TABLE IF NOT EXISTS character_stats (
    id SERIAL PRIMARY KEY,
    character_id VARCHAR(255) NOT NULL REFERENCES characters(character_id) ON DELETE CASCADE,
    stats JSONB, -- 属性映射
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(character_id)
);

-- 角色元数据表（JSONB存储）
CREATE TABLE IF NOT EXISTS character_metadata (
    id SERIAL PRIMARY KEY,
    character_id VARCHAR(255) NOT NULL REFERENCES characters(character_id) ON DELETE CASCADE,
    metadata JSONB, -- 元数据映射
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(character_id)
);

-- 角色组表
CREATE TABLE IF NOT EXISTS character_groups (
    id SERIAL PRIMARY KEY,
    group_id VARCHAR(255) UNIQUE NOT NULL,
    worldview_id VARCHAR(255) NOT NULL REFERENCES worldviews(worldview_id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    group_type VARCHAR(100), -- 门派, 家族, 组织, 团队等
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    status VARCHAR(50) DEFAULT 'active'
);

-- 角色组成员关系表
CREATE TABLE IF NOT EXISTS character_group_members (
    id SERIAL PRIMARY KEY,
    group_id VARCHAR(255) NOT NULL REFERENCES character_groups(group_id) ON DELETE CASCADE,
    character_id VARCHAR(255) NOT NULL REFERENCES characters(character_id) ON DELETE CASCADE,
    role_in_group VARCHAR(100), -- 在组中的角色
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'active', -- active, inactive, expelled
    UNIQUE(group_id, character_id)
);

-- 角色对话表
CREATE TABLE IF NOT EXISTS character_dialogues (
    id SERIAL PRIMARY KEY,
    dialogue_id VARCHAR(255) UNIQUE NOT NULL,
    character_id VARCHAR(255) NOT NULL REFERENCES characters(character_id) ON DELETE CASCADE,
    situation TEXT NOT NULL, -- 对话情境
    dialogue_content TEXT NOT NULL, -- 对话内容
    dialogue_type VARCHAR(50), -- 独白, 对话, 内心独白等
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255)
);

-- 创建角色相关索引
CREATE INDEX IF NOT EXISTS idx_characters_character_id ON characters(character_id);
CREATE INDEX IF NOT EXISTS idx_characters_worldview_id ON characters(worldview_id);
CREATE INDEX IF NOT EXISTS idx_characters_name ON characters(name);
CREATE INDEX IF NOT EXISTS idx_characters_role_type ON characters(role_type);
CREATE INDEX IF NOT EXISTS idx_characters_cultivation_level ON characters(cultivation_level);
CREATE INDEX IF NOT EXISTS idx_characters_created_at ON characters(created_at);
CREATE INDEX IF NOT EXISTS idx_characters_status ON characters(status);

CREATE INDEX IF NOT EXISTS idx_character_personality_traits_character_id ON character_personality_traits(character_id);
CREATE INDEX IF NOT EXISTS idx_character_goals_character_id ON character_goals(character_id);
CREATE INDEX IF NOT EXISTS idx_character_relationships_character_id ON character_relationships(character_id);
CREATE INDEX IF NOT EXISTS idx_character_techniques_character_id ON character_techniques(character_id);
CREATE INDEX IF NOT EXISTS idx_character_artifacts_character_id ON character_artifacts(character_id);
CREATE INDEX IF NOT EXISTS idx_character_resources_character_id ON character_resources(character_id);
CREATE INDEX IF NOT EXISTS idx_character_stats_character_id ON character_stats(character_id);
CREATE INDEX IF NOT EXISTS idx_character_metadata_character_id ON character_metadata(character_id);

CREATE INDEX IF NOT EXISTS idx_character_groups_group_id ON character_groups(group_id);
CREATE INDEX IF NOT EXISTS idx_character_groups_worldview_id ON character_groups(worldview_id);
CREATE INDEX IF NOT EXISTS idx_character_groups_group_type ON character_groups(group_type);

CREATE INDEX IF NOT EXISTS idx_character_group_members_group_id ON character_group_members(group_id);
CREATE INDEX IF NOT EXISTS idx_character_group_members_character_id ON character_group_members(character_id);

CREATE INDEX IF NOT EXISTS idx_character_dialogues_dialogue_id ON character_dialogues(dialogue_id);
CREATE INDEX IF NOT EXISTS idx_character_dialogues_character_id ON character_dialogues(character_id);
CREATE INDEX IF NOT EXISTS idx_character_dialogues_created_at ON character_dialogues(created_at);

-- 创建JSONB字段的GIN索引
CREATE INDEX IF NOT EXISTS idx_character_personality_traits_traits ON character_personality_traits USING GIN (personality_traits);
CREATE INDEX IF NOT EXISTS idx_character_goals_goals ON character_goals USING GIN (goals);
CREATE INDEX IF NOT EXISTS idx_character_relationships_relationships ON character_relationships USING GIN (relationships);
CREATE INDEX IF NOT EXISTS idx_character_techniques_techniques ON character_techniques USING GIN (techniques);
CREATE INDEX IF NOT EXISTS idx_character_artifacts_artifacts ON character_artifacts USING GIN (artifacts);
CREATE INDEX IF NOT EXISTS idx_character_resources_resources ON character_resources USING GIN (resources);
CREATE INDEX IF NOT EXISTS idx_character_stats_stats ON character_stats USING GIN (stats);
CREATE INDEX IF NOT EXISTS idx_character_metadata_metadata ON character_metadata USING GIN (metadata);

-- 为角色相关表添加更新时间触发器
CREATE TRIGGER update_characters_updated_at BEFORE UPDATE ON characters
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_character_personality_traits_updated_at BEFORE UPDATE ON character_personality_traits
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

-- 创建角色完整信息视图
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
    pt.personality_traits,
    cg.goals,
    cr.relationships,
    ct.techniques,
    ca.artifacts,
    cres.resources,
    cst.stats,
    cm.metadata
FROM characters c
LEFT JOIN character_personality_traits pt ON c.character_id = pt.character_id
LEFT JOIN character_goals cg ON c.character_id = cg.character_id
LEFT JOIN character_relationships cr ON c.character_id = cr.character_id
LEFT JOIN character_techniques ct ON c.character_id = ct.character_id
LEFT JOIN character_artifacts ca ON c.character_id = ca.character_id
LEFT JOIN character_resources cres ON c.character_id = cres.character_id
LEFT JOIN character_stats cst ON c.character_id = cst.character_id
LEFT JOIN character_metadata cm ON c.character_id = cm.character_id;

-- 创建存储过程：插入完整的角色数据
CREATE OR REPLACE FUNCTION insert_character_complete(
    p_character_id VARCHAR(255),
    p_worldview_id VARCHAR(255),
    p_name VARCHAR(255),
    p_role_type VARCHAR(50),
    p_age INTEGER DEFAULT NULL,
    p_gender VARCHAR(50) DEFAULT NULL,
    p_cultivation_level VARCHAR(255) DEFAULT NULL,
    p_element_type VARCHAR(255) DEFAULT NULL,
    p_background TEXT DEFAULT NULL,
    p_current_location VARCHAR(255) DEFAULT NULL,
    p_organization_id VARCHAR(255) DEFAULT NULL,
    p_created_by VARCHAR(255) DEFAULT 'system',
    p_personality_traits JSONB DEFAULT NULL,
    p_goals JSONB DEFAULT NULL,
    p_relationships JSONB DEFAULT NULL,
    p_techniques JSONB DEFAULT NULL,
    p_artifacts JSONB DEFAULT NULL,
    p_resources JSONB DEFAULT NULL,
    p_stats JSONB DEFAULT NULL,
    p_metadata JSONB DEFAULT NULL
) RETURNS INTEGER AS $$
DECLARE
    character_pk INTEGER;
BEGIN
    -- 插入角色主表
    INSERT INTO characters (
        character_id, worldview_id, name, age, gender, role_type,
        cultivation_level, element_type, background, current_location,
        organization_id, created_by
    ) VALUES (
        p_character_id, p_worldview_id, p_name, p_age, p_gender, p_role_type,
        p_cultivation_level, p_element_type, p_background, p_current_location,
        p_organization_id, p_created_by
    ) RETURNING id INTO character_pk;
    
    -- 插入性格特质
    IF p_personality_traits IS NOT NULL THEN
        INSERT INTO character_personality_traits (character_id, personality_traits)
        VALUES (p_character_id, p_personality_traits);
    END IF;
    
    -- 插入目标
    IF p_goals IS NOT NULL THEN
        INSERT INTO character_goals (character_id, goals)
        VALUES (p_character_id, p_goals);
    END IF;
    
    -- 插入关系
    IF p_relationships IS NOT NULL THEN
        INSERT INTO character_relationships (character_id, relationships)
        VALUES (p_character_id, p_relationships);
    END IF;
    
    -- 插入技能
    IF p_techniques IS NOT NULL THEN
        INSERT INTO character_techniques (character_id, techniques)
        VALUES (p_character_id, p_techniques);
    END IF;
    
    -- 插入法宝
    IF p_artifacts IS NOT NULL THEN
        INSERT INTO character_artifacts (character_id, artifacts)
        VALUES (p_character_id, p_artifacts);
    END IF;
    
    -- 插入资源
    IF p_resources IS NOT NULL THEN
        INSERT INTO character_resources (character_id, resources)
        VALUES (p_character_id, p_resources);
    END IF;
    
    -- 插入属性
    IF p_stats IS NOT NULL THEN
        INSERT INTO character_stats (character_id, stats)
        VALUES (p_character_id, p_stats);
    END IF;
    
    -- 插入元数据
    IF p_metadata IS NOT NULL THEN
        INSERT INTO character_metadata (character_id, metadata)
        VALUES (p_character_id, p_metadata);
    END IF;
    
    RETURN character_pk;
END;
$$ LANGUAGE plpgsql;

-- 添加角色表注释
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
COMMENT ON TABLE character_dialogues IS '角色对话表，存储角色的对话记录';
COMMENT ON FUNCTION insert_character_complete IS '插入完整的角色数据';
COMMENT ON VIEW character_complete IS '完整的角色信息视图';

-- 显示创建结果
SELECT 'Database tables created successfully!' as status;
