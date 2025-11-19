-- 更新角色表结构以匹配新的prompt输出格式
-- 添加新字段，删除不需要的字段

-- 1. 添加新字段
ALTER TABLE characters ADD COLUMN IF NOT EXISTS appearance text;
ALTER TABLE characters ADD COLUMN IF NOT EXISTS turning_point text;
ALTER TABLE characters ADD COLUMN IF NOT EXISTS relationship_text text;

-- 2. 删除不需要的字段
ALTER TABLE characters DROP COLUMN IF EXISTS relationships CASCADE;

-- 3. 添加字段注释
COMMENT ON COLUMN characters.appearance IS '外貌描述';
COMMENT ON COLUMN characters.turning_point IS '重要转折点';
COMMENT ON COLUMN characters.relationship_text IS '个人关系视角';

-- 4. 显示更新后的表结构
\d characters;
