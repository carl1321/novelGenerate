-- 创建世界观相关的视图和存储过程

-- 创建worldview_complete视图
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
    g.main_regions,
    g.special_locations,
    s.organizations,
    s.social_hierarchy,
    s.cultural_norms,
    he.events,
    he.timeline
FROM worldviews w
LEFT JOIN power_systems ps ON w.worldview_id = ps.worldview_id
LEFT JOIN geographies g ON w.worldview_id = g.worldview_id
LEFT JOIN societies s ON w.worldview_id = s.worldview_id
LEFT JOIN historical_events he ON w.worldview_id = he.worldview_id;

-- 创建insert_worldview_complete存储过程
CREATE OR REPLACE FUNCTION insert_worldview_complete(
    p_worldview_id VARCHAR(255),
    p_name VARCHAR(500),
    p_description TEXT,
    p_core_concept TEXT,
    p_created_by VARCHAR(255),
    p_cultivation_realms JSONB DEFAULT NULL,
    p_energy_types JSONB DEFAULT NULL,
    p_technique_categories JSONB DEFAULT NULL,
    p_main_regions JSONB DEFAULT NULL,
    p_special_locations JSONB DEFAULT NULL,
    p_organizations JSONB DEFAULT NULL,
    p_social_hierarchy JSONB DEFAULT NULL,
    p_cultural_norms JSONB DEFAULT NULL,
    p_events JSONB DEFAULT NULL,
    p_timeline JSONB DEFAULT NULL
) RETURNS INTEGER AS $$
DECLARE
    worldview_db_id INTEGER;
BEGIN
    -- 插入世界观主表
    INSERT INTO worldviews (worldview_id, name, description, core_concept, created_by)
    VALUES (p_worldview_id, p_name, p_description, p_core_concept, p_created_by)
    RETURNING id INTO worldview_db_id;
    
    -- 插入力量体系
    IF p_cultivation_realms IS NOT NULL OR p_energy_types IS NOT NULL OR p_technique_categories IS NOT NULL THEN
        INSERT INTO power_systems (worldview_id, cultivation_realms, energy_types, technique_categories)
        VALUES (p_worldview_id, p_cultivation_realms, p_energy_types, p_technique_categories);
    END IF;
    
    -- 插入地理设定
    IF p_main_regions IS NOT NULL OR p_special_locations IS NOT NULL THEN
        INSERT INTO geographies (worldview_id, main_regions, special_locations)
        VALUES (p_worldview_id, p_main_regions, p_special_locations);
    END IF;
    
    -- 插入社会组织
    IF p_organizations IS NOT NULL OR p_social_hierarchy IS NOT NULL OR p_cultural_norms IS NOT NULL THEN
        INSERT INTO societies (worldview_id, organizations, social_hierarchy, cultural_norms)
        VALUES (p_worldview_id, p_organizations, p_social_hierarchy, p_cultural_norms);
    END IF;
    
    -- 插入历史事件
    IF p_events IS NOT NULL OR p_timeline IS NOT NULL THEN
        INSERT INTO historical_events (worldview_id, events, timeline)
        VALUES (p_worldview_id, p_events, p_timeline);
    END IF;
    
    RETURN worldview_db_id;
END;
$$ LANGUAGE plpgsql;

-- 创建update_worldview_complete存储过程
CREATE OR REPLACE FUNCTION update_worldview_complete(
    p_worldview_id VARCHAR(255),
    p_name VARCHAR(500),
    p_description TEXT,
    p_core_concept TEXT,
    p_cultivation_realms JSONB DEFAULT NULL,
    p_energy_types JSONB DEFAULT NULL,
    p_technique_categories JSONB DEFAULT NULL,
    p_main_regions JSONB DEFAULT NULL,
    p_special_locations JSONB DEFAULT NULL,
    p_organizations JSONB DEFAULT NULL,
    p_social_hierarchy JSONB DEFAULT NULL,
    p_cultural_norms JSONB DEFAULT NULL,
    p_events JSONB DEFAULT NULL,
    p_timeline JSONB DEFAULT NULL
) RETURNS BOOLEAN AS $$
BEGIN
    -- 更新世界观主表
    UPDATE worldviews 
    SET name = p_name, description = p_description, core_concept = p_core_concept
    WHERE worldview_id = p_worldview_id;
    
    -- 更新或插入力量体系
    IF p_cultivation_realms IS NOT NULL OR p_energy_types IS NOT NULL OR p_technique_categories IS NOT NULL THEN
        INSERT INTO power_systems (worldview_id, cultivation_realms, energy_types, technique_categories)
        VALUES (p_worldview_id, p_cultivation_realms, p_energy_types, p_technique_categories)
        ON CONFLICT (worldview_id) 
        DO UPDATE SET 
            cultivation_realms = EXCLUDED.cultivation_realms,
            energy_types = EXCLUDED.energy_types,
            technique_categories = EXCLUDED.technique_categories;
    END IF;
    
    -- 更新或插入地理设定
    IF p_main_regions IS NOT NULL OR p_special_locations IS NOT NULL THEN
        INSERT INTO geographies (worldview_id, main_regions, special_locations)
        VALUES (p_worldview_id, p_main_regions, p_special_locations)
        ON CONFLICT (worldview_id) 
        DO UPDATE SET 
            main_regions = EXCLUDED.main_regions,
            special_locations = EXCLUDED.special_locations;
    END IF;
    
    -- 更新或插入社会组织
    IF p_organizations IS NOT NULL OR p_social_hierarchy IS NOT NULL OR p_cultural_norms IS NOT NULL THEN
        INSERT INTO societies (worldview_id, organizations, social_hierarchy, cultural_norms)
        VALUES (p_worldview_id, p_organizations, p_social_hierarchy, p_cultural_norms)
        ON CONFLICT (worldview_id) 
        DO UPDATE SET 
            organizations = EXCLUDED.organizations,
            social_hierarchy = EXCLUDED.social_hierarchy,
            cultural_norms = EXCLUDED.cultural_norms;
    END IF;
    
    -- 更新或插入历史事件
    IF p_events IS NOT NULL OR p_timeline IS NOT NULL THEN
        INSERT INTO historical_events (worldview_id, events, timeline)
        VALUES (p_worldview_id, p_events, p_timeline)
        ON CONFLICT (worldview_id) 
        DO UPDATE SET 
            events = EXCLUDED.events,
            timeline = EXCLUDED.timeline;
    END IF;
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- 授权
GRANT SELECT ON worldview_complete TO postgres;
GRANT EXECUTE ON FUNCTION insert_worldview_complete TO postgres;
GRANT EXECUTE ON FUNCTION update_worldview_complete TO postgres;
