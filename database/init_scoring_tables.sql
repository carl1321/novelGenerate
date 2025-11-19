-- 创建评分智能体相关表

-- 1. 评分记录主表
CREATE TABLE IF NOT EXISTS scoring_records (
    id VARCHAR(100) PRIMARY KEY,
    detailed_plot_id VARCHAR(100) NOT NULL,
    scorer_id VARCHAR(100) NOT NULL DEFAULT 'system',
    scoring_type VARCHAR(50) NOT NULL DEFAULT 'intelligent', -- intelligent, manual, auto
    total_score DECIMAL(5,2) NOT NULL CHECK (total_score >= 0 AND total_score <= 100),
    scoring_level VARCHAR(20) NOT NULL, -- 优秀, 良好, 一般, 较差, 很差
    overall_feedback TEXT,
    improvement_suggestions TEXT[], -- PostgreSQL array
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 2. 评分维度详情表
CREATE TABLE IF NOT EXISTS scoring_dimensions (
    id VARCHAR(100) PRIMARY KEY,
    scoring_record_id VARCHAR(100) NOT NULL REFERENCES scoring_records(id) ON DELETE CASCADE,
    dimension_name VARCHAR(50) NOT NULL, -- logic_consistency, dramatic_conflict, etc.
    dimension_display_name VARCHAR(100) NOT NULL, -- 逻辑自洽性, 戏剧冲突性, etc.
    score DECIMAL(5,2) NOT NULL CHECK (score >= 0 AND score <= 100),
    feedback TEXT,
    weight DECIMAL(3,2) DEFAULT 1.0, -- 权重
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(scoring_record_id, dimension_name)
);

-- 3. 评分维度映射表（用于标准化维度名称）
CREATE TABLE IF NOT EXISTS dimension_mappings (
    id VARCHAR(100) PRIMARY KEY,
    technical_name VARCHAR(50) UNIQUE NOT NULL, -- logic_consistency, dramatic_conflict, etc.
    display_name VARCHAR(100) NOT NULL, -- 逻辑自洽性, 戏剧冲突性, etc.
    description TEXT,
    color_code VARCHAR(7), -- #1890ff, #52c41a, etc.
    weight DECIMAL(3,2) DEFAULT 1.0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 添加详细剧情表的外键引用
ALTER TABLE scoring_records 
ADD CONSTRAINT fk_scoring_detailed_plot 
FOREIGN KEY (detailed_plot_id) REFERENCES detailed_plots(id) ON DELETE CASCADE;

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_scoring_records_detailed_plot_id ON scoring_records(detailed_plot_id);
CREATE INDEX IF NOT EXISTS idx_scoring_records_created_at ON scoring_records(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_scoring_dimensions_scoring_record_id ON scoring_dimensions(scoring_record_id);
CREATE INDEX IF NOT EXISTS idx_scoring_dimensions_dimension_name ON scoring_dimensions(dimension_name);

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

-- 添加表注释
COMMENT ON TABLE scoring_records IS '评分智能体记录表 - 存储每次评分的总体信息';
COMMENT ON TABLE scoring_dimensions IS '评分维度详情表 - 存储各个维度的具体评分';
COMMENT ON TABLE dimension_mappings IS '维度映射表 - 维度名称和属性的标准化配置';

COMMENT ON COLUMN scoring_records.scoring_type IS '评分类型：intelligent-智能评分，manual-人工评分，auto-自动评分';
COMMENT ON COLUMN scoring_records.total_score IS '总分（0-100）';
COMMENT ON COLUMN scoring_records.scoring_level IS '评分等级：优秀/良好/一般/较差/很差';
COMMENT ON COLUMN scoring_records.improvement_suggestions IS '改进建议列表';
COMMENT ON COLUMN scoring_dimensions.score IS '维度分数（0-100）';
COMMENT ON COLUMN scoring_dimensions.weight IS '维度权重';
COMMENT ON COLUMN dimension_mappings.color_code IS '前端显示用的颜色代码';
COMMENT ON COLUMN dimension_mappings.weight IS '默认权重';
