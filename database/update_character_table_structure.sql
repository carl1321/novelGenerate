-- 更新角色表结构以匹配新的字段格式
-- 删除旧数据并调整字段类型

-- 1. 删除所有角色数据
DELETE FROM characters;

-- 2. 删除相关的对话数据
DELETE FROM character_dialogues;

-- 3. 修改字段类型和默认值
-- 将 personality_traits 从 jsonb 改为 text
ALTER TABLE characters 
ALTER COLUMN personality_traits TYPE text USING 
  CASE 
    WHEN personality_traits IS NULL THEN NULL
    WHEN jsonb_typeof(personality_traits) = 'string' THEN personality_traits #>> '{}'
    WHEN jsonb_typeof(personality_traits) = 'array' THEN 
      (SELECT string_agg(
        CASE 
          WHEN jsonb_typeof(elem) = 'string' THEN elem #>> '{}'
          WHEN jsonb_typeof(elem) = 'object' THEN COALESCE(elem ->> 'trait', elem ->> 'name', elem #>> '{}')
          ELSE ''
        END, '、'
      ) FROM jsonb_array_elements(personality_traits) AS elem)
    ELSE personality_traits #>> '{}'
  END;

-- 4. 添加新的字段
-- 主要目标 (text)
ALTER TABLE characters ADD COLUMN IF NOT EXISTS main_goals text;

-- 短期目标 (text)  
ALTER TABLE characters ADD COLUMN IF NOT EXISTS short_term_goals text;

-- 弱点 (text)
ALTER TABLE characters ADD COLUMN IF NOT EXISTS weaknesses text;

-- 5. 删除不再需要的字段
-- 删除 goals 字段（已被 main_goals 和 short_term_goals 替代）
ALTER TABLE characters DROP COLUMN IF EXISTS goals;

-- 删除 artifacts 字段（已被 weaknesses 替代）
ALTER TABLE characters DROP COLUMN IF EXISTS artifacts;

-- 删除 stats 字段（不再需要数值属性）
ALTER TABLE characters DROP COLUMN IF EXISTS stats;

-- 删除 resources 字段（不再需要资源数值）
ALTER TABLE characters DROP COLUMN IF EXISTS resources;

-- 6. 更新默认值
ALTER TABLE characters ALTER COLUMN personality_traits SET DEFAULT NULL;
ALTER TABLE characters ALTER COLUMN main_goals SET DEFAULT NULL;
ALTER TABLE characters ALTER COLUMN short_term_goals SET DEFAULT NULL;
ALTER TABLE characters ALTER COLUMN weaknesses SET DEFAULT NULL;

-- 7. 添加注释
COMMENT ON COLUMN characters.personality_traits IS '性格特质描述（文本格式）';
COMMENT ON COLUMN characters.main_goals IS '主要目标描述（文本格式）';
COMMENT ON COLUMN characters.short_term_goals IS '短期目标描述（文本格式）';
COMMENT ON COLUMN characters.weaknesses IS '弱点和限制描述（文本格式）';

-- 8. 显示更新后的表结构
\d characters;
