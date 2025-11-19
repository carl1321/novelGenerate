-- 创建修正历史表
CREATE TABLE IF NOT EXISTS correction_history (
    id VARCHAR(50) PRIMARY KEY,
    detailed_plot_id VARCHAR(50) NOT NULL,
    original_content TEXT NOT NULL,
    corrected_content TEXT NOT NULL,
    logic_check_result JSONB,
    corrections_made JSONB,
    correction_summary TEXT,
    word_count_change INTEGER DEFAULT 0,
    quality_improvement TEXT,
    correction_notes TEXT,
    corrected_by VARCHAR(50) NOT NULL DEFAULT 'system',
    corrected_at TIMESTAMP NOT NULL DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_correction_history_detailed_plot_id ON correction_history(detailed_plot_id);
CREATE INDEX IF NOT EXISTS idx_correction_history_corrected_at ON correction_history(corrected_at);
CREATE INDEX IF NOT EXISTS idx_correction_history_corrected_by ON correction_history(corrected_by);

-- 添加注释
COMMENT ON TABLE correction_history IS '详细剧情修正历史表';
COMMENT ON COLUMN correction_history.id IS '修正记录ID';
COMMENT ON COLUMN correction_history.detailed_plot_id IS '详细剧情ID';
COMMENT ON COLUMN correction_history.original_content IS '原始内容';
COMMENT ON COLUMN correction_history.corrected_content IS '修正后内容';
COMMENT ON COLUMN correction_history.logic_check_result IS '逻辑检查结果';
COMMENT ON COLUMN correction_history.corrections_made IS '修正详情';
COMMENT ON COLUMN correction_history.correction_summary IS '修正总结';
COMMENT ON COLUMN correction_history.word_count_change IS '字数变化';
COMMENT ON COLUMN correction_history.quality_improvement IS '质量提升说明';
COMMENT ON COLUMN correction_history.correction_notes IS '修正说明';
COMMENT ON COLUMN correction_history.corrected_by IS '修正者';
COMMENT ON COLUMN correction_history.corrected_at IS '修正时间';
