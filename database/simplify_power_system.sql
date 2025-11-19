-- 简化力量体系表结构
-- 去掉 energy_types 和 technique_categories 字段
-- 在 cultivation_realms 中每个境界包含 energy_type 字段

-- 1. 备份现有数据
CREATE TABLE IF NOT EXISTS power_systems_backup AS 
SELECT * FROM power_systems;

-- 2. 删除旧表
DROP TABLE IF EXISTS power_systems CASCADE;

-- 3. 创建新的简化表结构
CREATE TABLE power_systems (
    worldview_id VARCHAR(50) PRIMARY KEY,
    cultivation_realms JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (worldview_id) REFERENCES worldviews(worldview_id) ON DELETE CASCADE
);

-- 4. 从备份表恢复数据（只保留 cultivation_realms 字段）
INSERT INTO power_systems (worldview_id, cultivation_realms, created_at, updated_at)
SELECT 
    worldview_id, 
    cultivation_realms, 
    created_at, 
    updated_at
FROM power_systems_backup
WHERE cultivation_realms IS NOT NULL;

-- 5. 添加更新触发器
CREATE OR REPLACE FUNCTION update_power_systems_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_power_systems_updated_at
    BEFORE UPDATE ON power_systems
    FOR EACH ROW
    EXECUTE FUNCTION update_power_systems_updated_at();

-- 6. 清理备份表（可选，建议保留一段时间）
-- DROP TABLE power_systems_backup;

COMMENT ON TABLE power_systems IS '力量体系表 - 简化版本，只包含修炼境界';
COMMENT ON COLUMN power_systems.cultivation_realms IS '修炼境界数组，每个境界包含name、level、description、requirements、energy_type字段';
