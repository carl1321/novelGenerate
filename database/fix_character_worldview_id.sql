-- 修复现有角色数据的worldview_id字段
-- 这个脚本用于更新现有角色数据，为它们分配默认的世界观ID

-- 首先检查是否有世界观数据
SELECT 'Available worldviews:' as info;
SELECT worldview_id, name FROM worldviews WHERE status = 'active' ORDER BY created_at DESC;

-- 检查现有角色数据的worldview_id情况
SELECT 'Characters with missing worldview_id:' as info;
SELECT character_id, name, worldview_id, created_at 
FROM characters 
WHERE worldview_id IS NULL OR worldview_id = '' 
ORDER BY created_at DESC;

-- 获取第一个可用的世界观ID作为默认值
-- 假设我们使用最新的世界观
DO $$
DECLARE
    default_worldview_id VARCHAR(255);
    character_count INTEGER;
BEGIN
    -- 获取最新的世界观ID
    SELECT worldview_id INTO default_worldview_id
    FROM worldviews 
    WHERE status = 'active' 
    ORDER BY created_at DESC 
    LIMIT 1;
    
    IF default_worldview_id IS NOT NULL THEN
        -- 统计需要更新的角色数量
        SELECT COUNT(*) INTO character_count
        FROM characters 
        WHERE worldview_id IS NULL OR worldview_id = '';
        
        RAISE NOTICE 'Found % characters with missing worldview_id', character_count;
        RAISE NOTICE 'Will update them to use worldview_id: %', default_worldview_id;
        
        -- 更新角色数据
        UPDATE characters 
        SET worldview_id = default_worldview_id,
            updated_at = CURRENT_TIMESTAMP
        WHERE worldview_id IS NULL OR worldview_id = '';
        
        RAISE NOTICE 'Updated % characters successfully', character_count;
    ELSE
        RAISE NOTICE 'No active worldview found, cannot update characters';
    END IF;
END $$;

-- 验证更新结果
SELECT 'Updated characters:' as info;
SELECT character_id, name, worldview_id, updated_at 
FROM characters 
ORDER BY updated_at DESC 
LIMIT 10;

-- 显示统计信息
SELECT 'Character count by worldview:' as info;
SELECT w.name as worldview_name, COUNT(c.character_id) as character_count
FROM worldviews w
LEFT JOIN characters c ON w.worldview_id = c.worldview_id AND c.status = 'active'
GROUP BY w.worldview_id, w.name
ORDER BY character_count DESC;
