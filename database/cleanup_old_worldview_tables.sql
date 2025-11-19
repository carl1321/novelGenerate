-- 清理旧的世界观表结构
-- 删除不再需要的表，只保留prompt中定义的核心字段

-- 1. 删除不再需要的表（如果存在且有权限）
DO $$
BEGIN
    -- 删除societies表（如果存在）
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'societies') THEN
        DROP TABLE societies CASCADE;
        RAISE NOTICE '已删除societies表';
    END IF;
    
    -- 删除history_cultures表（如果存在）
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'history_cultures') THEN
        DROP TABLE history_cultures CASCADE;
        RAISE NOTICE '已删除history_cultures表';
    END IF;
EXCEPTION
    WHEN insufficient_privilege THEN
        RAISE NOTICE '权限不足，跳过删除表操作';
    WHEN OTHERS THEN
        RAISE NOTICE '删除表时出错: %', SQLERRM;
END $$;

-- 2. 确保power_systems表结构正确
-- 检查并添加缺失的字段（如果不存在）
DO $$
BEGIN
    -- 检查cultivation_realms字段是否存在
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'power_systems' AND column_name = 'cultivation_realms'
    ) THEN
        ALTER TABLE power_systems ADD COLUMN cultivation_realms JSONB;
    END IF;
    
    -- 检查energy_types字段是否存在
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'power_systems' AND column_name = 'energy_types'
    ) THEN
        ALTER TABLE power_systems ADD COLUMN energy_types JSONB;
    END IF;
    
    -- 检查technique_categories字段是否存在
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'power_systems' AND column_name = 'technique_categories'
    ) THEN
        ALTER TABLE power_systems ADD COLUMN technique_categories JSONB;
    END IF;
END $$;

-- 3. 确保geographies表结构正确
-- 检查并添加缺失的字段（如果不存在）
DO $$
BEGIN
    -- 检查regions字段是否存在
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'geographies' AND column_name = 'regions'
    ) THEN
        ALTER TABLE geographies ADD COLUMN regions JSONB;
    END IF;
    
    -- 检查main_regions字段是否存在
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'geographies' AND column_name = 'main_regions'
    ) THEN
        ALTER TABLE geographies ADD COLUMN main_regions JSONB;
    END IF;
    
    -- 检查special_locations字段是否存在
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'geographies' AND column_name = 'special_locations'
    ) THEN
        ALTER TABLE geographies ADD COLUMN special_locations JSONB;
    END IF;
END $$;

-- 4. 为power_systems表添加唯一约束（如果不存在）
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE table_name = 'power_systems' AND constraint_name = 'power_systems_worldview_id_key'
    ) THEN
        ALTER TABLE power_systems ADD CONSTRAINT power_systems_worldview_id_key UNIQUE (worldview_id);
    END IF;
END $$;

-- 5. 为geographies表添加唯一约束（如果不存在）
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE table_name = 'geographies' AND constraint_name = 'geographies_worldview_id_key'
    ) THEN
        ALTER TABLE geographies ADD CONSTRAINT geographies_worldview_id_key UNIQUE (worldview_id);
    END IF;
END $$;

-- 6. 添加外键约束（如果不存在）
DO $$
BEGIN
    -- power_systems表的外键约束
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE table_name = 'power_systems' AND constraint_name = 'power_systems_worldview_id_fkey'
    ) THEN
        ALTER TABLE power_systems 
        ADD CONSTRAINT power_systems_worldview_id_fkey 
        FOREIGN KEY (worldview_id) REFERENCES worldviews(worldview_id) ON DELETE CASCADE;
    END IF;
    
    -- geographies表的外键约束
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE table_name = 'geographies' AND constraint_name = 'geographies_worldview_id_fkey'
    ) THEN
        ALTER TABLE geographies 
        ADD CONSTRAINT geographies_worldview_id_fkey 
        FOREIGN KEY (worldview_id) REFERENCES worldviews(worldview_id) ON DELETE CASCADE;
    END IF;
END $$;

-- 7. 删除不再需要的存储过程
DO $$
DECLARE
    func_record RECORD;
BEGIN
    -- 删除所有insert_worldview_complete函数
    FOR func_record IN 
        SELECT proname, oid 
        FROM pg_proc 
        WHERE proname = 'insert_worldview_complete'
    LOOP
        EXECUTE 'DROP FUNCTION IF EXISTS ' || func_record.oid::regprocedure || ' CASCADE';
        RAISE NOTICE '已删除函数: %', func_record.proname;
    END LOOP;
    
    -- 删除所有update_worldview_complete函数
    FOR func_record IN 
        SELECT proname, oid 
        FROM pg_proc 
        WHERE proname = 'update_worldview_complete'
    LOOP
        EXECUTE 'DROP FUNCTION IF EXISTS ' || func_record.oid::regprocedure || ' CASCADE';
        RAISE NOTICE '已删除函数: %', func_record.proname;
    END LOOP;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '删除函数时出错: %', SQLERRM;
END $$;

-- 8. 创建新的简化存储过程（如果需要）
-- 注意：我们现在直接使用SQL操作，不再依赖存储过程

-- 9. 更新表注释
COMMENT ON TABLE power_systems IS '力量体系表 - 存储修炼境界、能量类型、功法分类';
COMMENT ON TABLE geographies IS '地理设定表 - 存储地理区域、主要区域、特殊地点';

COMMENT ON COLUMN power_systems.cultivation_realms IS '修炼境界数组';
COMMENT ON COLUMN power_systems.energy_types IS '能量类型数组';
COMMENT ON COLUMN power_systems.technique_categories IS '功法分类数组';

COMMENT ON COLUMN geographies.regions IS '地理区域数组（新格式）';
COMMENT ON COLUMN geographies.main_regions IS '主要区域数组（旧格式兼容）';
COMMENT ON COLUMN geographies.special_locations IS '特殊地点数组';

-- 10. 显示最终表结构
SELECT 
    table_name,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns 
WHERE table_name IN ('worldviews', 'power_systems', 'geographies')
ORDER BY table_name, ordinal_position;
