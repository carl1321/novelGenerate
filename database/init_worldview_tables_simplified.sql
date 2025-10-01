-- 简化的世界观数据库表结构初始化脚本
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
    social_hierarchy JSONB, -- 社会等级结构
    cultural_norms JSONB, -- 文化规范
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(worldview_id)
);

-- 创建历史事件表
CREATE TABLE IF NOT EXISTS historical_events (
    id SERIAL PRIMARY KEY,
    worldview_id VARCHAR(255) NOT NULL REFERENCES worldviews(worldview_id) ON DELETE CASCADE,
    events JSONB, -- 历史事件数组
    timeline JSONB, -- 时间线
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(worldview_id)
);

-- 创建角色主表（简化版，所有信息存储在JSONB字段中）
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
    
    -- 所有复杂信息存储在JSONB字段中
    personality_traits JSONB DEFAULT '[]'::jsonb, -- 性格特质数组
    goals JSONB DEFAULT '[]'::jsonb, -- 目标数组
    relationships JSONB DEFAULT '{}'::jsonb, -- 关系映射
    techniques JSONB DEFAULT '[]'::jsonb, -- 技能数组
    artifacts JSONB DEFAULT '[]'::jsonb, -- 法宝数组
    resources JSONB DEFAULT '{}'::jsonb, -- 资源映射
    stats JSONB DEFAULT '{}'::jsonb, -- 属性映射
    metadata JSONB DEFAULT '{}'::jsonb, -- 元数据映射
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    status VARCHAR(50) DEFAULT 'active' -- active, inactive, deleted
);

-- 创建角色组表（简化版）
CREATE TABLE IF NOT EXISTS character_groups (
    id SERIAL PRIMARY KEY,
    group_id VARCHAR(255) UNIQUE NOT NULL,
    worldview_id VARCHAR(255) NOT NULL REFERENCES worldviews(worldview_id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    group_type VARCHAR(100), -- 门派, 家族, 组织, 团队等
    members JSONB DEFAULT '[]'::jsonb, -- 成员列表
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    status VARCHAR(50) DEFAULT 'active'
);

-- 创建角色对话表（简化版）
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

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_characters_worldview_id ON characters(worldview_id);
CREATE INDEX IF NOT EXISTS idx_characters_role_type ON characters(role_type);
CREATE INDEX IF NOT EXISTS idx_characters_name ON characters(name);
CREATE INDEX IF NOT EXISTS idx_character_groups_worldview_id ON character_groups(worldview_id);
CREATE INDEX IF NOT EXISTS idx_character_dialogues_character_id ON character_dialogues(character_id);

-- 创建更新触发器
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 为所有表添加更新触发器
CREATE TRIGGER update_worldviews_updated_at BEFORE UPDATE ON worldviews FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_power_systems_updated_at BEFORE UPDATE ON power_systems FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_geographies_updated_at BEFORE UPDATE ON geographies FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_societies_updated_at BEFORE UPDATE ON societies FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_historical_events_updated_at BEFORE UPDATE ON historical_events FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_characters_updated_at BEFORE UPDATE ON characters FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_character_groups_updated_at BEFORE UPDATE ON character_groups FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 添加表注释
COMMENT ON TABLE worldviews IS '世界观主表，存储世界观的基本信息';
COMMENT ON TABLE power_systems IS '力量体系表，存储修炼境界、能量类型等';
COMMENT ON TABLE geographies IS '地理设定表，存储区域和地点信息';
COMMENT ON TABLE societies IS '社会组织表，存储组织、等级、文化等信息';
COMMENT ON TABLE historical_events IS '历史事件表，存储历史事件和时间线';
COMMENT ON TABLE characters IS '角色主表，存储角色的所有信息（简化版）';
COMMENT ON TABLE character_groups IS '角色组表，存储角色分组信息';
COMMENT ON TABLE character_dialogues IS '角色对话表，存储角色的对话记录';
