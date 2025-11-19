-- 完成角色表结构更新
-- 处理剩余的字段类型转换和删除

-- 1. 手动转换 personality_traits 字段类型
-- 先创建一个临时列
ALTER TABLE characters ADD COLUMN personality_traits_temp text;

-- 2. 转换数据（处理现有的jsonb数据）
UPDATE characters SET personality_traits_temp = 
  CASE 
    WHEN personality_traits IS NULL THEN NULL
    WHEN jsonb_typeof(personality_traits) = 'string' THEN personality_traits #>> '{}'
    WHEN jsonb_typeof(personality_traits) = 'array' THEN 
      array_to_string(
        ARRAY(
          SELECT 
            CASE 
              WHEN jsonb_typeof(elem) = 'string' THEN elem #>> '{}'
              WHEN jsonb_typeof(elem) = 'object' THEN COALESCE(elem ->> 'trait', elem ->> 'name', elem #>> '{}')
              ELSE ''
            END
          FROM jsonb_array_elements(personality_traits) AS elem
        ), '、'
      )
    ELSE personality_traits #>> '{}'
  END;

-- 3. 删除旧列并重命名新列
ALTER TABLE characters DROP COLUMN personality_traits;
ALTER TABLE characters RENAME COLUMN personality_traits_temp TO personality_traits;

-- 4. 删除依赖的视图（如果存在）
DROP VIEW IF EXISTS character_complete CASCADE;

-- 5. 删除不再需要的字段
ALTER TABLE characters DROP COLUMN IF EXISTS goals CASCADE;
ALTER TABLE characters DROP COLUMN IF EXISTS artifacts CASCADE;
ALTER TABLE characters DROP COLUMN IF EXISTS stats CASCADE;
ALTER TABLE characters DROP COLUMN IF EXISTS resources CASCADE;

-- 6. 显示最终的表结构
\d characters;
