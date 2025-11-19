-- 创建进化历史表
CREATE TABLE IF NOT EXISTS evolution_history (
    id VARCHAR(50) PRIMARY KEY,
    detailed_plot_id VARCHAR(50) NOT NULL,
    evolution_type VARCHAR(50) NOT NULL DEFAULT 'general',
    original_content TEXT NOT NULL,
    evolved_content TEXT NOT NULL,
    improvements JSONB,
    evolution_summary TEXT,
    word_count_change INTEGER DEFAULT 0,
    quality_score DECIMAL(5,2) DEFAULT 0.0,
    evolution_notes TEXT,
    evolved_by VARCHAR(50) NOT NULL DEFAULT 'system',
    evolved_at TIMESTAMP NOT NULL DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_evolution_history_detailed_plot_id ON evolution_history(detailed_plot_id);
CREATE INDEX IF NOT EXISTS idx_evolution_history_evolution_type ON evolution_history(evolution_type);
CREATE INDEX IF NOT EXISTS idx_evolution_history_evolved_at ON evolution_history(evolved_at);

-- 添加注释
COMMENT ON TABLE evolution_history IS '详细剧情进化历史表';
COMMENT ON COLUMN evolution_history.id IS '进化记录ID';
COMMENT ON COLUMN evolution_history.detailed_plot_id IS '详细剧情ID';
COMMENT ON COLUMN evolution_history.evolution_type IS '进化类型';
COMMENT ON COLUMN evolution_history.original_content IS '原始内容';
COMMENT ON COLUMN evolution_history.evolved_content IS '进化后内容';
COMMENT ON COLUMN evolution_history.improvements IS '改进详情';
COMMENT ON COLUMN evolution_history.evolution_summary IS '进化总结';
COMMENT ON COLUMN evolution_history.word_count_change IS '字数变化';
COMMENT ON COLUMN evolution_history.quality_score IS '质量评分';
COMMENT ON COLUMN evolution_history.evolution_notes IS '进化说明';
COMMENT ON COLUMN evolution_history.evolved_by IS '进化者';
COMMENT ON COLUMN evolution_history.evolved_at IS '进化时间';
