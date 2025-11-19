-- 详细剧情表
CREATE TABLE IF NOT EXISTS detailed_plots (
    id VARCHAR(255) PRIMARY KEY,
    chapter_outline_id VARCHAR(255) NOT NULL,
    plot_outline_id VARCHAR(255) NOT NULL,
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    word_count INTEGER DEFAULT 0,
    status VARCHAR(50) DEFAULT '草稿',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (chapter_outline_id) REFERENCES chapter_outlines(id) ON DELETE CASCADE,
    FOREIGN KEY (plot_outline_id) REFERENCES plot_outlines(id) ON DELETE CASCADE
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_detailed_plots_chapter_outline_id ON detailed_plots(chapter_outline_id);
CREATE INDEX IF NOT EXISTS idx_detailed_plots_plot_outline_id ON detailed_plots(plot_outline_id);
CREATE INDEX IF NOT EXISTS idx_detailed_plots_status ON detailed_plots(status);
CREATE INDEX IF NOT EXISTS idx_detailed_plots_created_at ON detailed_plots(created_at);

-- 添加注释
COMMENT ON TABLE detailed_plots IS '详细剧情表';
COMMENT ON COLUMN detailed_plots.id IS '详细剧情ID';
COMMENT ON COLUMN detailed_plots.chapter_outline_id IS '所属章节大纲ID';
COMMENT ON COLUMN detailed_plots.plot_outline_id IS '所属剧情大纲ID';
COMMENT ON COLUMN detailed_plots.title IS '详细剧情标题';
COMMENT ON COLUMN detailed_plots.content IS '详细剧情内容';
COMMENT ON COLUMN detailed_plots.word_count IS '字数统计';
COMMENT ON COLUMN detailed_plots.status IS '状态：草稿、已完成、已发布';
COMMENT ON COLUMN detailed_plots.created_at IS '创建时间';
COMMENT ON COLUMN detailed_plots.updated_at IS '更新时间';
