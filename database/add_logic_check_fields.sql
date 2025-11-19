-- 为detailed_plots表添加逻辑检查相关字段
ALTER TABLE detailed_plots 
ADD COLUMN IF NOT EXISTS logic_status VARCHAR(50),
ADD COLUMN IF NOT EXISTS logic_score DECIMAL(5,2);

-- 更新现有记录的默认值
UPDATE detailed_plots 
SET logic_status = NULL, 
    logic_score = NULL 
WHERE logic_status IS NULL;

-- 添加索引以提高查询性能
CREATE INDEX IF NOT EXISTS idx_detailed_plots_logic_status ON detailed_plots(logic_status);
CREATE INDEX IF NOT EXISTS idx_detailed_plots_logic_score ON detailed_plots(logic_score);

-- 创建逻辑检查历史表
CREATE TABLE IF NOT EXISTS logic_check_history (
    id VARCHAR(50) PRIMARY KEY,
    detailed_plot_id VARCHAR(50) NOT NULL,
    check_type VARCHAR(20) NOT NULL DEFAULT 'manual',
    logic_score DECIMAL(5,2) NOT NULL,
    overall_status VARCHAR(50) NOT NULL,
    issues_count INTEGER DEFAULT 0,
    checked_by VARCHAR(100) NOT NULL DEFAULT 'system',
    checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    result JSONB,
    FOREIGN KEY (detailed_plot_id) REFERENCES detailed_plots(id) ON DELETE CASCADE
);

-- 为逻辑检查历史表添加索引
CREATE INDEX IF NOT EXISTS idx_logic_check_history_plot_id ON logic_check_history(detailed_plot_id);
CREATE INDEX IF NOT EXISTS idx_logic_check_history_checked_at ON logic_check_history(checked_at);
CREATE INDEX IF NOT EXISTS idx_logic_check_history_status ON logic_check_history(overall_status);
