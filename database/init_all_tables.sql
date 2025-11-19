-- 统一数据库初始化脚本
-- 按正确顺序执行所有必要的表创建
-- PostgreSQL 17 兼容

-- ============================================
-- 第一部分：基础表和函数
-- ============================================

-- 创建更新时间触发器函数（所有表共用）
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- ============================================
-- 第二部分：世界观相关表
-- ============================================

-- 创建世界观主表
CREATE TABLE IF NOT EXISTS worldviews (
    id SERIAL PRIMARY KEY,
    worldview_id VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(500) NOT NULL,
    description TEXT,
    core_concept TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    version INTEGER DEFAULT 1,
    status VARCHAR(50) DEFAULT 'active'
);

-- 创建力量体系表
CREATE TABLE IF NOT EXISTS power_systems (
    id SERIAL PRIMARY KEY,
    worldview_id VARCHAR(255) NOT NULL REFERENCES worldviews(worldview_id) ON DELETE CASCADE,
    cultivation_realms JSONB,
    energy_types JSONB,
    technique_categories JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(worldview_id)
);

-- 创建地理设定表
CREATE TABLE IF NOT EXISTS geographies (
    id SERIAL PRIMARY KEY,
    worldview_id VARCHAR(255) NOT NULL REFERENCES worldviews(worldview_id) ON DELETE CASCADE,
    main_regions JSONB,
    special_locations JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(worldview_id)
);

-- 创建社会组织表
CREATE TABLE IF NOT EXISTS societies (
    id SERIAL PRIMARY KEY,
    worldview_id VARCHAR(255) NOT NULL REFERENCES worldviews(worldview_id) ON DELETE CASCADE,
    organizations JSONB,
    social_hierarchy JSONB,
    cultural_norms JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(worldview_id)
);

-- 创建历史事件表
CREATE TABLE IF NOT EXISTS historical_events (
    id SERIAL PRIMARY KEY,
    worldview_id VARCHAR(255) NOT NULL REFERENCES worldviews(worldview_id) ON DELETE CASCADE,
    events JSONB,
    timeline JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(worldview_id)
);

-- ============================================
-- 第三部分：角色相关表
-- ============================================

-- 创建角色类型枚举
DO $$ BEGIN
    CREATE TYPE character_role_type AS ENUM ('主角', '配角', '反派', '导师', '盟友', '路人');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- 创建角色主表
CREATE TABLE IF NOT EXISTS characters (
    id SERIAL PRIMARY KEY,
    character_id VARCHAR(255) UNIQUE NOT NULL,
    worldview_id VARCHAR(255) NOT NULL REFERENCES worldviews(worldview_id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    age INTEGER NOT NULL CHECK (age >= 0),
    gender VARCHAR(10) NOT NULL CHECK (gender IN ('男', '女', '其他')),
    role_type character_role_type NOT NULL DEFAULT '配角',
    cultivation_level VARCHAR(50),
    element_type VARCHAR(50),
    background TEXT,
    current_location VARCHAR(255),
    organization_id VARCHAR(255),
    personality_traits JSONB DEFAULT '[]'::jsonb,
    goals JSONB DEFAULT '[]'::jsonb,
    relationships JSONB DEFAULT '{}'::jsonb,
    techniques JSONB DEFAULT '[]'::jsonb,
    artifacts JSONB DEFAULT '[]'::jsonb,
    resources JSONB DEFAULT '{}'::jsonb,
    stats JSONB DEFAULT '{}'::jsonb,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    status VARCHAR(50) DEFAULT 'active'
);

-- 创建角色组表
CREATE TABLE IF NOT EXISTS character_groups (
    id SERIAL PRIMARY KEY,
    group_id VARCHAR(255) UNIQUE NOT NULL,
    worldview_id VARCHAR(255) NOT NULL REFERENCES worldviews(worldview_id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    group_type VARCHAR(100),
    members JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    status VARCHAR(50) DEFAULT 'active'
);

-- ============================================
-- 第四部分：事件相关表
-- ============================================

CREATE TABLE IF NOT EXISTS events (
    id VARCHAR(50) PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    event_type VARCHAR(50) NOT NULL,
    importance VARCHAR(20) NOT NULL,
    category VARCHAR(50) NOT NULL,
    setting VARCHAR(200),
    participants JSONB DEFAULT '[]'::jsonb,
    duration VARCHAR(100),
    outcome TEXT,
    plot_impact TEXT,
    character_impact JSONB DEFAULT '{}'::jsonb,
    foreshadowing_elements JSONB DEFAULT '[]'::jsonb,
    prerequisites JSONB DEFAULT '[]'::jsonb,
    consequences JSONB DEFAULT '[]'::jsonb,
    tags JSONB DEFAULT '[]'::jsonb,
    plot_outline_id VARCHAR(50),
    chapter_number INTEGER,
    sequence_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 第五部分：剧情大纲相关表
-- ============================================

CREATE TABLE IF NOT EXISTS plot_outlines (
    id VARCHAR(50) PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    worldview_id VARCHAR(50) NOT NULL,
    story_tone VARCHAR(50) NOT NULL,
    narrative_structure VARCHAR(50) NOT NULL,
    story_structure VARCHAR(50) NOT NULL,
    target_word_count INTEGER DEFAULT 100000,
    estimated_chapters INTEGER DEFAULT 20,
    story_framework JSONB NOT NULL,
    character_positions JSONB DEFAULT '{}'::jsonb,
    plot_blocks JSONB DEFAULT '[]'::jsonb,
    story_flow JSONB NOT NULL,
    status VARCHAR(20) DEFAULT '草稿',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50)
);

-- ============================================
-- 第六部分：章节大纲相关表
-- ============================================

CREATE TABLE IF NOT EXISTS chapter_outlines (
    id VARCHAR(50) PRIMARY KEY,
    plot_outline_id VARCHAR(50) NOT NULL REFERENCES plot_outlines(id) ON DELETE CASCADE,
    chapter_number INTEGER NOT NULL,
    title VARCHAR(200) NOT NULL,
    story_position DECIMAL(3,2) NOT NULL,
    act_belonging VARCHAR(50),
    chapter_summary TEXT NOT NULL,
    character_appearances JSONB DEFAULT '[]'::jsonb,
    plot_function VARCHAR(50) NOT NULL,
    conflict_development TEXT,
    character_development JSONB DEFAULT '[]'::jsonb,
    writing_notes TEXT,
    emotional_tone VARCHAR(50) NOT NULL,
    atmosphere TEXT,
    tension_level INTEGER DEFAULT 5,
    worldview_elements JSONB DEFAULT '[]'::jsonb,
    estimated_word_count INTEGER DEFAULT 5000,
    status VARCHAR(20) DEFAULT '大纲',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    core_event VARCHAR(200),
    key_scenes JSONB DEFAULT '[]'::jsonb,
    UNIQUE(plot_outline_id, chapter_number)
);

-- ============================================
-- 第七部分：详细剧情相关表
-- ============================================

CREATE TABLE IF NOT EXISTS detailed_plots (
    id VARCHAR(255) PRIMARY KEY,
    chapter_outline_id VARCHAR(255) NOT NULL,
    plot_outline_id VARCHAR(255) NOT NULL,
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    word_count INTEGER DEFAULT 0,
    status VARCHAR(50) DEFAULT '草稿',
    logic_status VARCHAR(50),
    logic_check_result JSONB,
    scoring_status VARCHAR(50),
    total_score DECIMAL(5,2),
    scoring_result JSONB,
    scoring_feedback TEXT,
    scored_at TIMESTAMP,
    scored_by VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (chapter_outline_id) REFERENCES chapter_outlines(id) ON DELETE CASCADE,
    FOREIGN KEY (plot_outline_id) REFERENCES plot_outlines(id) ON DELETE CASCADE
);

-- ============================================
-- 第八部分：评分相关表
-- ============================================

CREATE TABLE IF NOT EXISTS scoring_records (
    id VARCHAR(100) PRIMARY KEY,
    detailed_plot_id VARCHAR(100) NOT NULL,
    scorer_id VARCHAR(100) NOT NULL DEFAULT 'system',
    scoring_type VARCHAR(50) NOT NULL DEFAULT 'intelligent',
    total_score DECIMAL(5,2) NOT NULL CHECK (total_score >= 0 AND total_score <= 100),
    scoring_level VARCHAR(20) NOT NULL,
    overall_feedback TEXT,
    improvement_suggestions TEXT[],
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (detailed_plot_id) REFERENCES detailed_plots(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS scoring_dimensions (
    id VARCHAR(100) PRIMARY KEY,
    scoring_record_id VARCHAR(100) NOT NULL REFERENCES scoring_records(id) ON DELETE CASCADE,
    dimension_name VARCHAR(50) NOT NULL,
    dimension_display_name VARCHAR(100) NOT NULL,
    score DECIMAL(5,2) NOT NULL CHECK (score >= 0 AND score <= 100),
    feedback TEXT,
    weight DECIMAL(3,2) DEFAULT 1.0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(scoring_record_id, dimension_name)
);

CREATE TABLE IF NOT EXISTS dimension_mappings (
    id VARCHAR(100) PRIMARY KEY,
    technical_name VARCHAR(50) UNIQUE NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    description TEXT,
    color_code VARCHAR(7),
    weight DECIMAL(3,2) DEFAULT 1.0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- 第九部分：版本管理相关表
-- ============================================

CREATE TABLE IF NOT EXISTS detailed_plot_versions (
    id SERIAL PRIMARY KEY,
    detailed_plot_id VARCHAR(255) NOT NULL,
    version_type VARCHAR(50) NOT NULL,
    version_number INTEGER NOT NULL DEFAULT 1,
    is_current_version BOOLEAN DEFAULT FALSE,
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    word_count INTEGER DEFAULT 0,
    source_table VARCHAR(50),
    source_record_id VARCHAR(255),
    version_notes TEXT,
    created_by VARCHAR(50) DEFAULT 'system',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (detailed_plot_id) REFERENCES detailed_plots(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS evolution_history (
    id VARCHAR(255) PRIMARY KEY,
    detailed_plot_id VARCHAR(255) NOT NULL,
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    word_count INTEGER DEFAULT 0,
    evolution_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50) DEFAULT 'system',
    FOREIGN KEY (detailed_plot_id) REFERENCES detailed_plots(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS correction_history (
    id VARCHAR(255) PRIMARY KEY,
    detailed_plot_id VARCHAR(255) NOT NULL,
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    word_count INTEGER DEFAULT 0,
    correction_notes TEXT,
    logic_check_result JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50) DEFAULT 'system',
    FOREIGN KEY (detailed_plot_id) REFERENCES detailed_plots(id) ON DELETE CASCADE
);

-- ============================================
-- 第十部分：创建索引
-- ============================================

-- 世界观索引
CREATE INDEX IF NOT EXISTS idx_worldviews_worldview_id ON worldviews(worldview_id);
CREATE INDEX IF NOT EXISTS idx_characters_worldview_id ON characters(worldview_id);
CREATE INDEX IF NOT EXISTS idx_characters_character_id ON characters(character_id);
CREATE INDEX IF NOT EXISTS idx_characters_name ON characters(name);
CREATE INDEX IF NOT EXISTS idx_characters_role_type ON characters(role_type);

-- 事件索引
CREATE INDEX IF NOT EXISTS idx_events_plot_outline_id ON events(plot_outline_id);
CREATE INDEX IF NOT EXISTS idx_events_chapter_number ON events(chapter_number);
CREATE INDEX IF NOT EXISTS idx_events_event_type ON events(event_type);
CREATE INDEX IF NOT EXISTS idx_events_importance ON events(importance);

-- 剧情大纲索引
CREATE INDEX IF NOT EXISTS idx_plot_outlines_worldview_id ON plot_outlines(worldview_id);
CREATE INDEX IF NOT EXISTS idx_plot_outlines_status ON plot_outlines(status);

-- 章节大纲索引
CREATE INDEX IF NOT EXISTS idx_chapter_outlines_plot_id ON chapter_outlines(plot_outline_id);
CREATE INDEX IF NOT EXISTS idx_chapter_outlines_number ON chapter_outlines(plot_outline_id, chapter_number);

-- 详细剧情索引
CREATE INDEX IF NOT EXISTS idx_detailed_plots_chapter_outline_id ON detailed_plots(chapter_outline_id);
CREATE INDEX IF NOT EXISTS idx_detailed_plots_plot_outline_id ON detailed_plots(plot_outline_id);
CREATE INDEX IF NOT EXISTS idx_detailed_plots_status ON detailed_plots(status);

-- 评分索引
CREATE INDEX IF NOT EXISTS idx_scoring_records_detailed_plot_id ON scoring_records(detailed_plot_id);
CREATE INDEX IF NOT EXISTS idx_scoring_dimensions_scoring_record_id ON scoring_dimensions(scoring_record_id);

-- 版本管理索引
CREATE INDEX IF NOT EXISTS idx_detailed_plot_versions_detailed_plot_id ON detailed_plot_versions(detailed_plot_id);
CREATE INDEX IF NOT EXISTS idx_detailed_plot_versions_current ON detailed_plot_versions(detailed_plot_id, is_current_version);

-- ============================================
-- 第十一部分：创建触发器
-- ============================================

CREATE TRIGGER update_worldviews_updated_at BEFORE UPDATE ON worldviews FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_power_systems_updated_at BEFORE UPDATE ON power_systems FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_geographies_updated_at BEFORE UPDATE ON geographies FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_societies_updated_at BEFORE UPDATE ON societies FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_historical_events_updated_at BEFORE UPDATE ON historical_events FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_characters_updated_at BEFORE UPDATE ON characters FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_character_groups_updated_at BEFORE UPDATE ON character_groups FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_plot_outlines_updated_at BEFORE UPDATE ON plot_outlines FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_chapter_outlines_updated_at BEFORE UPDATE ON chapter_outlines FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_detailed_plots_updated_at BEFORE UPDATE ON detailed_plots FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- 第十二部分：创建视图
-- ============================================

-- 详细剧情与最新版本视图
CREATE OR REPLACE VIEW detailed_plots_with_latest_version AS
SELECT 
    dp.id as original_id,
    dp.chapter_outline_id,
    dp.plot_outline_id,
    dp.status,
    dp.logic_status,
    dp.logic_check_result,
    dp.scoring_status,
    dp.total_score,
    dp.scoring_result,
    dp.scoring_feedback,
    dp.scored_at,
    dp.scored_by,
    dp.created_at as original_created_at,
    dp.updated_at as original_updated_at,
    dpv.id as current_version_id,
    dpv.version_type as current_version_type,
    dpv.version_number as current_version_number,
    COALESCE(dpv.title, dp.title) as title,
    COALESCE(dpv.content, dp.content) as content,
    COALESCE(dpv.word_count, dp.word_count) as word_count,
    dpv.source_table as current_source_table,
    dpv.source_record_id as current_source_record_id,
    dpv.version_notes as current_version_notes,
    dpv.created_by as current_created_by,
    dpv.created_at as current_created_at,
    dpv.updated_at as current_updated_at,
    CASE WHEN dpv.id IS NOT NULL THEN TRUE ELSE FALSE END as has_version_record
FROM detailed_plots dp
LEFT JOIN detailed_plot_versions dpv ON (
    dp.id = dpv.detailed_plot_id 
    AND dpv.is_current_version = TRUE
)
ORDER BY 
    CASE 
        WHEN dpv.updated_at IS NOT NULL THEN dpv.updated_at 
        ELSE dp.updated_at 
    END DESC;

-- ============================================
-- 第十三部分：插入初始数据
-- ============================================

-- 插入标准化的维度映射数据
INSERT INTO dimension_mappings (id, technical_name, display_name, description, color_code, weight) VALUES
    ('dim_logic_consistency', 'logic_consistency', '逻辑自洽性', '故事逻辑是否严密合理', '#1890ff', 0.25),
    ('dim_dramatic_conflict', 'dramatic_conflict', '戏剧冲突性', '冲突设置是否激烈有效', '#52c41a', 0.20),
    ('dim_character_development', 'character_development', '角色发展性', '角色塑造是否生动深化', '#fa8c16', 0.20),
    ('dim_world_usage', 'world_usage', '世界观运用', '世界观设定运用是否到位', '#722ed1', 0.15),
    ('dim_writing_style', 'writing_style', '文笔风格', '语言文字表达是否优美', '#eb2f96', 0.20),
    ('dim_dramatic_tension', 'dramatic_tension', '戏剧张力', '故事张力是否饱满', '#1890ff', 0.10),
    ('dim_emotional_impact', 'emotional_impact', '情感冲击', '情感表达是否深刻', '#52c41a', 0.10),
    ('dim_thematic_depth', 'thematic_depth', '主题深度', '主题内涵是否深刻', '#722ed1', 0.10),
    ('dim_pacing_fluency', 'pacing_fluency', '节奏流畅度', '叙事节奏是否合理', '#eb2f96', 0.10),
    ('dim_originality_creativity', 'originality_creativity', '创新性', '内容是否新颖有创意', '#fa8c16', 0.10)
ON CONFLICT (technical_name) DO NOTHING;

-- ============================================
-- 完成提示
-- ============================================

SELECT 'Database initialization completed successfully!' as status;

