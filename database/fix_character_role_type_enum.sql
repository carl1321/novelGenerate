-- 修复角色类型枚举，使其与代码中的CharacterRoleType枚举保持一致
-- 执行前请备份数据库

-- 1. 创建新的角色类型枚举（与代码中的CharacterRoleType一致）
CREATE TYPE character_role_type_v2 AS ENUM ('主角', '配角', '正义伙伴', '反派', '情人', '其他', '特殊');

-- 2. 添加新列到角色表
ALTER TABLE characters ADD COLUMN role_type_v2 character_role_type_v2;

-- 3. 迁移现有数据
UPDATE characters SET role_type_v2 = 
    CASE 
        WHEN role_type = '主角' THEN '主角'::character_role_type_v2
        WHEN role_type = '配角' THEN '配角'::character_role_type_v2
        WHEN role_type = '反派' THEN '反派'::character_role_type_v2
        WHEN role_type = '导师' THEN '特殊'::character_role_type_v2
        WHEN role_type = '盟友' THEN '正义伙伴'::character_role_type_v2
        WHEN role_type = '路人' THEN '其他'::character_role_type_v2
        ELSE '其他'::character_role_type_v2
    END;

-- 4. 删除旧列
ALTER TABLE characters DROP COLUMN role_type;

-- 5. 重命名新列
ALTER TABLE characters RENAME COLUMN role_type_v2 TO role_type;

-- 6. 删除旧枚举类型
DROP TYPE character_role_type;

-- 7. 重命名新枚举类型
ALTER TYPE character_role_type_v2 RENAME TO character_role_type;

-- 8. 添加NOT NULL约束和默认值
ALTER TABLE characters ALTER COLUMN role_type SET NOT NULL;
ALTER TABLE characters ALTER COLUMN role_type SET DEFAULT '配角';

-- 验证更新结果
SELECT DISTINCT role_type FROM characters ORDER BY role_type;
