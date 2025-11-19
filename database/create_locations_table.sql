-- 创建地点表
CREATE TABLE IF NOT EXISTS locations (
    id VARCHAR(36) PRIMARY KEY,
    worldview_id VARCHAR(36) NOT NULL,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    x DECIMAL(5,2) NOT NULL CHECK (x >= 0 AND x <= 100),
    y DECIMAL(5,2) NOT NULL CHECK (y >= 0 AND y <= 100),
    size INTEGER NOT NULL CHECK (size >= 1 AND size <= 50),
    importance VARCHAR(20) NOT NULL CHECK (importance IN ('重要', '普通', '次要')),
    features JSONB DEFAULT '[]'::jsonb,
    connections JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_locations_worldview_id ON locations(worldview_id);
CREATE INDEX IF NOT EXISTS idx_locations_type ON locations(type);
CREATE INDEX IF NOT EXISTS idx_locations_importance ON locations(importance);
CREATE INDEX IF NOT EXISTS idx_locations_coordinates ON locations(x, y);

-- 创建触发器自动更新updated_at
CREATE OR REPLACE FUNCTION update_locations_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_locations_updated_at
    BEFORE UPDATE ON locations
    FOR EACH ROW
    EXECUTE FUNCTION update_locations_updated_at();

-- 添加外键约束（如果worldviews表存在）
-- ALTER TABLE locations ADD CONSTRAINT fk_locations_worldview_id 
-- FOREIGN KEY (worldview_id) REFERENCES worldviews(id) ON DELETE CASCADE;