-- 更新地理设定表结构以支持新的地理势力格式
-- 添加 regions 字段，保留 main_regions 字段以保持向后兼容

-- 为 geographies 表添加 regions 字段
ALTER TABLE geographies 
ADD COLUMN IF NOT EXISTS regions JSONB;

-- 为 regions 字段创建 GIN 索引以提高查询性能
CREATE INDEX IF NOT EXISTS idx_geographies_regions ON geographies USING GIN (regions);

-- 更新世界观完整视图，优先使用 regions 字段
CREATE OR REPLACE VIEW worldview_complete AS
SELECT 
    w.id,
    w.worldview_id,
    w.name,
    w.description,
    w.core_concept,
    w.created_at,
    w.updated_at,
    w.created_by,
    w.version,
    w.status,
    ps.cultivation_realms,
    ps.energy_types,
    ps.technique_categories,
    -- 优先使用 regions，如果没有则使用 main_regions
    COALESCE(g.regions, g.main_regions) as regions,
    g.main_regions,
    g.special_locations,
    s.organizations,
    s.social_hierarchy,
    hc.historical_events,
    hc.cultural_features,
    hc.current_conflicts
FROM worldviews w
LEFT JOIN power_systems ps ON w.worldview_id = ps.worldview_id
LEFT JOIN geographies g ON w.worldview_id = g.worldview_id
LEFT JOIN societies s ON w.worldview_id = s.worldview_id
LEFT JOIN history_cultures hc ON w.worldview_id = hc.worldview_id;

-- 更新存储过程以支持 regions 字段
CREATE OR REPLACE FUNCTION insert_worldview_complete(
    p_worldview_id VARCHAR(255),
    p_name VARCHAR(500),
    p_description TEXT,
    p_core_concept TEXT,
    p_created_by VARCHAR(255),
    p_cultivation_realms JSONB DEFAULT NULL,
    p_energy_types JSONB DEFAULT NULL,
    p_technique_categories JSONB DEFAULT NULL,
    p_regions JSONB DEFAULT NULL,
    p_main_regions JSONB DEFAULT NULL,
    p_special_locations JSONB DEFAULT NULL,
    p_organizations JSONB DEFAULT NULL,
    p_social_system JSONB DEFAULT NULL,
    p_historical_events JSONB DEFAULT NULL,
    p_cultural_features JSONB DEFAULT NULL,
    p_current_conflicts JSONB DEFAULT NULL
) RETURNS INTEGER AS $$
DECLARE
    worldview_pk INTEGER;
BEGIN
    -- 插入主表
    INSERT INTO worldviews (worldview_id, name, description, core_concept, created_by)
    VALUES (p_worldview_id, p_name, p_description, p_core_concept, p_created_by)
    RETURNING id INTO worldview_pk;
    
    -- 插入力量体系
    IF p_cultivation_realms IS NOT NULL OR p_energy_types IS NOT NULL OR p_technique_categories IS NOT NULL THEN
        INSERT INTO power_systems (worldview_id, cultivation_realms, energy_types, technique_categories)
        VALUES (p_worldview_id, p_cultivation_realms, p_energy_types, p_technique_categories);
    END IF;
    
    -- 插入地理设定
    IF p_regions IS NOT NULL OR p_main_regions IS NOT NULL OR p_special_locations IS NOT NULL THEN
        INSERT INTO geographies (worldview_id, regions, main_regions, special_locations)
        VALUES (p_worldview_id, p_regions, p_main_regions, p_special_locations);
    END IF;
    
    -- 插入社会组织
    IF p_organizations IS NOT NULL OR p_social_system IS NOT NULL THEN
        INSERT INTO societies (worldview_id, organizations, social_system)
        VALUES (p_worldview_id, p_organizations, p_social_system);
    END IF;
    
    -- 插入历史文化
    IF p_historical_events IS NOT NULL OR p_cultural_features IS NOT NULL OR p_current_conflicts IS NOT NULL THEN
        INSERT INTO history_cultures (worldview_id, historical_events, cultural_features, current_conflicts)
        VALUES (p_worldview_id, p_historical_events, p_cultural_features, p_current_conflicts);
    END IF;
    
    RETURN worldview_pk;
END;
$$ LANGUAGE plpgsql;

-- 更新存储过程以支持 regions 字段
CREATE OR REPLACE FUNCTION update_worldview_complete(
    p_worldview_id VARCHAR(255),
    p_name VARCHAR(500) DEFAULT NULL,
    p_description TEXT DEFAULT NULL,
    p_core_concept TEXT DEFAULT NULL,
    p_cultivation_realms JSONB DEFAULT NULL,
    p_energy_types JSONB DEFAULT NULL,
    p_technique_categories JSONB DEFAULT NULL,
    p_regions JSONB DEFAULT NULL,
    p_main_regions JSONB DEFAULT NULL,
    p_special_locations JSONB DEFAULT NULL,
    p_organizations JSONB DEFAULT NULL,
    p_social_system JSONB DEFAULT NULL,
    p_historical_events JSONB DEFAULT NULL,
    p_cultural_features JSONB DEFAULT NULL,
    p_current_conflicts JSONB DEFAULT NULL
) RETURNS BOOLEAN AS $$
BEGIN
    -- 更新主表
    IF p_name IS NOT NULL OR p_description IS NOT NULL OR p_core_concept IS NOT NULL THEN
        UPDATE worldviews 
        SET 
            name = COALESCE(p_name, name),
            description = COALESCE(p_description, description),
            core_concept = COALESCE(p_core_concept, core_concept),
            version = version + 1
        WHERE worldview_id = p_worldview_id;
    END IF;
    
    -- 更新力量体系
    IF p_cultivation_realms IS NOT NULL OR p_energy_types IS NOT NULL OR p_technique_categories IS NOT NULL THEN
        INSERT INTO power_systems (worldview_id, cultivation_realms, energy_types, technique_categories)
        VALUES (p_worldview_id, p_cultivation_realms, p_energy_types, p_technique_categories)
        ON CONFLICT (worldview_id) DO UPDATE SET
            cultivation_realms = COALESCE(p_cultivation_realms, power_systems.cultivation_realms),
            energy_types = COALESCE(p_energy_types, power_systems.energy_types),
            technique_categories = COALESCE(p_technique_categories, power_systems.technique_categories);
    END IF;
    
    -- 更新地理设定
    IF p_regions IS NOT NULL OR p_main_regions IS NOT NULL OR p_special_locations IS NOT NULL THEN
        INSERT INTO geographies (worldview_id, regions, main_regions, special_locations)
        VALUES (p_worldview_id, p_regions, p_main_regions, p_special_locations)
        ON CONFLICT (worldview_id) DO UPDATE SET
            regions = COALESCE(p_regions, geographies.regions),
            main_regions = COALESCE(p_main_regions, geographies.main_regions),
            special_locations = COALESCE(p_special_locations, geographies.special_locations);
    END IF;
    
    -- 更新社会组织
    IF p_organizations IS NOT NULL OR p_social_system IS NOT NULL THEN
        INSERT INTO societies (worldview_id, organizations, social_system)
        VALUES (p_worldview_id, p_organizations, p_social_system)
        ON CONFLICT (worldview_id) DO UPDATE SET
            organizations = COALESCE(p_organizations, societies.organizations),
            social_system = COALESCE(p_social_system, societies.social_system);
    END IF;
    
    -- 更新历史文化
    IF p_historical_events IS NOT NULL OR p_cultural_features IS NOT NULL OR p_current_conflicts IS NOT NULL THEN
        INSERT INTO history_cultures (worldview_id, historical_events, cultural_features, current_conflicts)
        VALUES (p_worldview_id, p_historical_events, p_cultural_features, p_current_conflicts)
        ON CONFLICT (worldview_id) DO UPDATE SET
            historical_events = COALESCE(p_historical_events, history_cultures.historical_events),
            cultural_features = COALESCE(p_cultural_features, history_cultures.cultural_features),
            current_conflicts = COALESCE(p_current_conflicts, history_cultures.current_conflicts);
    END IF;
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- 添加注释
COMMENT ON COLUMN geographies.regions IS '地理区域数组，包含势力分布信息（新格式）';
COMMENT ON COLUMN geographies.main_regions IS '主要区域数组（旧格式，保持向后兼容）';

-- 显示更新结果
SELECT 'Geography format updated successfully!' as status;
