-- 更新角色类型枚举支持新的简化角色类型
-- 执行前请备份数据库

-- 1. 创建新的角色类型枚举
CREATE TYPE character_role_type_new AS ENUM ('主角', '正义伙伴', '反派', '情人', '其他', '特殊');

-- 2. 添加新列到角色表
ALTER TABLE characters ADD COLUMN role_type_new character_role_type_new;

-- 3. 迁移现有数据
UPDATE characters SET role_type_new = 
    CASE 
        WHEN role_type = '主角' THEN '主角'::character_role_type_new
        WHEN role_type = '配角' THEN '其他'::character_role_type_new
        WHEN role_type = '反派' THEN '反派'::character_role_type_new
        WHEN role_type = '导师' THEN '特殊'::character_role_type_new
        WHEN role_type = '盟友' THEN '正义伙伴'::character_role_type_new
        WHEN role_type = '路人' THEN '其他'::character_role_type_new
        WHEN role_type = '忠诚伙伴' THEN '正义伙伴'::character_role_type_new
        WHEN role_type = '叛逆盟友' THEN '正义伙伴'::character_role_type_new
        WHEN role_type = '技术支援' THEN '特殊'::character_role_type_new
        WHEN role_type = '神秘向导' THEN '特殊'::character_role_type_new
        WHEN role_type = '亦敌亦友' THEN '其他'::character_role_type_new
        WHEN role_type = '治愈辅助' THEN '特殊'::character_role_type_new
        WHEN role_type = '热血斗士' THEN '正义伙伴'::character_role_type_new
        WHEN role_type = '智囊谋士' THEN '特殊'::character_role_type_new
        WHEN role_type = '情报联络' THEN '特殊'::character_role_type_new
        WHEN role_type = '悲情守护者' THEN '特殊'::character_role_type_new
        WHEN role_type = '正义伙伴' THEN '正义伙伴'::character_role_type_new
        WHEN role_type = '叛逆伙伴' THEN '正义伙伴'::character_role_type_new
        WHEN role_type = '神秘导师型伙伴' THEN '特殊'::character_role_type_new
        WHEN role_type = '技术型伙伴' THEN '特殊'::character_role_type_new
        WHEN role_type = '忠诚护卫型伙伴' THEN '正义伙伴'::character_role_type_new
        WHEN role_type = '治愈型伙伴' THEN '特殊'::character_role_type_new
        WHEN role_type = '自由奔放型伙伴' THEN '其他'::character_role_type_new
        WHEN role_type = '赎罪型伙伴' THEN '其他'::character_role_type_new
        WHEN role_type = '自然亲和型伙伴' THEN '特殊'::character_role_type_new
        WHEN role_type = '智囊型伙伴' THEN '特殊'::character_role_type_new
        ELSE '其他'::character_role_type_new
    END;

-- 4. 删除旧列
ALTER TABLE characters DROP COLUMN role_type;

-- 5. 重命名新列
ALTER TABLE characters RENAME COLUMN role_type_new TO role_type;

-- 6. 删除旧枚举类型
DROP TYPE character_role_type;

-- 7. 重命名新枚举类型
ALTER TYPE character_role_type_new RENAME TO character_role_type;

-- 8. 创建角色关系表
CREATE TABLE IF NOT EXISTS character_relationships (
    id SERIAL PRIMARY KEY,
    character1_id VARCHAR(255) REFERENCES characters(character_id) ON DELETE CASCADE,
    character2_id VARCHAR(255) REFERENCES characters(character_id) ON DELETE CASCADE,
    relationship_type VARCHAR(50) NOT NULL,
    intimacy_level INTEGER DEFAULT 5 CHECK (intimacy_level >= 1 AND intimacy_level <= 10),
    trust_level INTEGER DEFAULT 5 CHECK (trust_level >= 1 AND trust_level <= 10),
    relationship_description TEXT,
    relationship_history JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(character1_id, character2_id)
);

-- 9. 创建关系分析表
CREATE TABLE IF NOT EXISTS relationship_analyses (
    id SERIAL PRIMARY KEY,
    analysis_id VARCHAR(255) UNIQUE NOT NULL,
    worldview_id VARCHAR(255) REFERENCES worldviews(worldview_id) ON DELETE CASCADE,
    analysis_type VARCHAR(50) NOT NULL,
    analysis_data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 10. 创建索引
CREATE INDEX IF NOT EXISTS idx_character_relationships_char1 ON character_relationships(character1_id);
CREATE INDEX IF NOT EXISTS idx_character_relationships_char2 ON character_relationships(character2_id);
CREATE INDEX IF NOT EXISTS idx_character_relationships_type ON character_relationships(relationship_type);
CREATE INDEX IF NOT EXISTS idx_relationship_analyses_worldview ON relationship_analyses(worldview_id);

-- 11. 添加注释
COMMENT ON TABLE character_relationships IS '角色关系表';
COMMENT ON TABLE relationship_analyses IS '关系分析表';
COMMENT ON COLUMN character_relationships.intimacy_level IS '亲密度 (1-10)';
COMMENT ON COLUMN character_relationships.trust_level IS '信任度 (1-10)';
COMMENT ON COLUMN character_relationships.relationship_type IS '关系类型：朋友、敌人、情人、导师、盟友、竞争对手、家人、弟子';
