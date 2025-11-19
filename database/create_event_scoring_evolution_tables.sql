-- 事件评分与进化系统数据库表结构
-- 用于存储事件评分结果和进化历史

-- 1. 事件评分表
CREATE TABLE IF NOT EXISTS event_scores (
    id SERIAL PRIMARY KEY,
    event_id VARCHAR(50) NOT NULL,
    protagonist_involvement DECIMAL(3,1) NOT NULL DEFAULT 0.0,
    plot_coherence DECIMAL(3,1) NOT NULL DEFAULT 0.0,
    character_development DECIMAL(3,1) NOT NULL DEFAULT 0.0,
    world_consistency DECIMAL(3,1) NOT NULL DEFAULT 0.0,
    dramatic_tension DECIMAL(3,1) NOT NULL DEFAULT 0.0,
    emotional_impact DECIMAL(3,1) NOT NULL DEFAULT 0.0,
    foreshadowing DECIMAL(3,1) NOT NULL DEFAULT 0.0,
    overall_quality DECIMAL(3,1) NOT NULL DEFAULT 0.0,
    feedback TEXT,
    strengths TEXT[],
    weaknesses TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. 事件进化历史表
CREATE TABLE IF NOT EXISTS event_evolution_history (
    id SERIAL PRIMARY KEY,
    original_event_id VARCHAR(50) NOT NULL,
    evolved_event_id VARCHAR(50) NOT NULL,
    score_id INTEGER REFERENCES event_scores(id),
    evolution_reason TEXT,
    status VARCHAR(20) DEFAULT 'pending', -- pending, accepted, rejected
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. 创建索引
CREATE INDEX IF NOT EXISTS idx_event_scores_event_id ON event_scores(event_id);
CREATE INDEX IF NOT EXISTS idx_event_scores_created_at ON event_scores(created_at);
CREATE INDEX IF NOT EXISTS idx_event_evolution_original_event_id ON event_evolution_history(original_event_id);
CREATE INDEX IF NOT EXISTS idx_event_evolution_evolved_event_id ON event_evolution_history(evolved_event_id);
CREATE INDEX IF NOT EXISTS idx_event_evolution_score_id ON event_evolution_history(score_id);
CREATE INDEX IF NOT EXISTS idx_event_evolution_status ON event_evolution_history(status);

-- 4. 创建触发器函数，自动更新 updated_at 字段
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 5. 为表创建触发器
CREATE TRIGGER update_event_scores_updated_at 
    BEFORE UPDATE ON event_scores 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_event_evolution_history_updated_at 
    BEFORE UPDATE ON event_evolution_history 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 6. 添加约束
ALTER TABLE event_scores 
    ADD CONSTRAINT chk_protagonist_involvement 
    CHECK (protagonist_involvement >= 0 AND protagonist_involvement <= 10);

ALTER TABLE event_scores 
    ADD CONSTRAINT chk_plot_coherence 
    CHECK (plot_coherence >= 0 AND plot_coherence <= 10);

ALTER TABLE event_scores 
    ADD CONSTRAINT chk_character_development 
    CHECK (character_development >= 0 AND character_development <= 10);

ALTER TABLE event_scores 
    ADD CONSTRAINT chk_world_consistency 
    CHECK (world_consistency >= 0 AND world_consistency <= 10);

ALTER TABLE event_scores 
    ADD CONSTRAINT chk_dramatic_tension 
    CHECK (dramatic_tension >= 0 AND dramatic_tension <= 10);

ALTER TABLE event_scores 
    ADD CONSTRAINT chk_emotional_impact 
    CHECK (emotional_impact >= 0 AND emotional_impact <= 10);

ALTER TABLE event_scores 
    ADD CONSTRAINT chk_foreshadowing 
    CHECK (foreshadowing >= 0 AND foreshadowing <= 10);

ALTER TABLE event_scores 
    ADD CONSTRAINT chk_overall_quality 
    CHECK (overall_quality >= 0 AND overall_quality <= 10);

ALTER TABLE event_evolution_history 
    ADD CONSTRAINT chk_status 
    CHECK (status IN ('pending', 'accepted', 'rejected'));

-- 7. 创建视图，方便查询
CREATE OR REPLACE VIEW event_score_summary AS
SELECT 
    es.event_id,
    es.overall_quality,
    es.protagonist_involvement,
    es.plot_coherence,
    es.character_development,
    es.world_consistency,
    es.dramatic_tension,
    es.emotional_impact,
    es.foreshadowing,
    es.created_at as score_date,
    COUNT(eeh.id) as evolution_count
FROM event_scores es
LEFT JOIN event_evolution_history eeh ON es.id = eeh.score_id
GROUP BY es.id, es.event_id, es.overall_quality, es.protagonist_involvement, 
         es.plot_coherence, es.character_development, es.world_consistency,
         es.dramatic_tension, es.emotional_impact, es.foreshadowing, es.created_at;

-- 8. 创建函数，获取事件的最新评分
CREATE OR REPLACE FUNCTION get_latest_event_score(event_id_param VARCHAR(50))
RETURNS TABLE (
    id INTEGER,
    event_id VARCHAR(50),
    protagonist_involvement DECIMAL(3,1),
    plot_coherence DECIMAL(3,1),
    character_development DECIMAL(3,1),
    world_consistency DECIMAL(3,1),
    dramatic_tension DECIMAL(3,1),
    emotional_impact DECIMAL(3,1),
    foreshadowing DECIMAL(3,1),
    overall_quality DECIMAL(3,1),
    feedback TEXT,
    strengths TEXT[],
    weaknesses TEXT[],
    created_at TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        es.id,
        es.event_id,
        es.protagonist_involvement,
        es.plot_coherence,
        es.character_development,
        es.world_consistency,
        es.dramatic_tension,
        es.emotional_impact,
        es.foreshadowing,
        es.overall_quality,
        es.feedback,
        es.strengths,
        es.weaknesses,
        es.created_at
    FROM event_scores es
    WHERE es.event_id = event_id_param
    ORDER BY es.created_at DESC
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;

-- 9. 创建函数，获取事件的评分历史
CREATE OR REPLACE FUNCTION get_event_score_history(event_id_param VARCHAR(50))
RETURNS TABLE (
    id INTEGER,
    event_id VARCHAR(50),
    protagonist_involvement DECIMAL(3,1),
    plot_coherence DECIMAL(3,1),
    character_development DECIMAL(3,1),
    world_consistency DECIMAL(3,1),
    dramatic_tension DECIMAL(3,1),
    emotional_impact DECIMAL(3,1),
    foreshadowing DECIMAL(3,1),
    overall_quality DECIMAL(3,1),
    feedback TEXT,
    strengths TEXT[],
    weaknesses TEXT[],
    created_at TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        es.id,
        es.event_id,
        es.protagonist_involvement,
        es.plot_coherence,
        es.character_development,
        es.world_consistency,
        es.dramatic_tension,
        es.emotional_impact,
        es.foreshadowing,
        es.overall_quality,
        es.feedback,
        es.strengths,
        es.weaknesses,
        es.created_at
    FROM event_scores es
    WHERE es.event_id = event_id_param
    ORDER BY es.created_at DESC;
END;
$$ LANGUAGE plpgsql;

-- 10. 创建函数，获取事件的进化历史
CREATE OR REPLACE FUNCTION get_event_evolution_history(event_id_param VARCHAR(50))
RETURNS TABLE (
    id INTEGER,
    original_event_id VARCHAR(50),
    evolved_event_id VARCHAR(50),
    score_id INTEGER,
    evolution_reason TEXT,
    status VARCHAR(20),
    created_at TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        eeh.id,
        eeh.original_event_id,
        eeh.evolved_event_id,
        eeh.score_id,
        eeh.evolution_reason,
        eeh.status,
        eeh.created_at
    FROM event_evolution_history eeh
    WHERE eeh.original_event_id = event_id_param
    ORDER BY eeh.created_at DESC;
END;
$$ LANGUAGE plpgsql;

-- 11. 插入示例数据（可选）
-- INSERT INTO event_scores (event_id, protagonist_involvement, plot_coherence, character_development, world_consistency, dramatic_tension, emotional_impact, foreshadowing, overall_quality, feedback, strengths, weaknesses) VALUES
-- ('event_example_1', 8.5, 7.0, 9.0, 8.0, 7.5, 8.0, 6.5, 8.0, '事件整体质量较高，主角参与度突出，角色发展明显。建议加强伏笔设置，为后续剧情做更多铺垫。', ARRAY['主角在事件中发挥核心作用', '角色成长轨迹清晰', '情感表达深刻动人', '符合世界观设定'], ARRAY['伏笔设置不够充分', '部分情节逻辑可以更严密', '戏剧张力有待提升']);

-- 12. 创建统计视图
CREATE OR REPLACE VIEW event_scoring_statistics AS
SELECT 
    COUNT(*) as total_scores,
    AVG(overall_quality) as avg_overall_quality,
    AVG(protagonist_involvement) as avg_protagonist_involvement,
    AVG(plot_coherence) as avg_plot_coherence,
    AVG(character_development) as avg_character_development,
    AVG(world_consistency) as avg_world_consistency,
    AVG(dramatic_tension) as avg_dramatic_tension,
    AVG(emotional_impact) as avg_emotional_impact,
    AVG(foreshadowing) as avg_foreshadowing,
    MAX(created_at) as latest_score_date,
    MIN(created_at) as earliest_score_date
FROM event_scores;

-- 13. 创建进化统计视图
CREATE OR REPLACE VIEW event_evolution_statistics AS
SELECT 
    COUNT(*) as total_evolutions,
    COUNT(CASE WHEN status = 'accepted' THEN 1 END) as accepted_evolutions,
    COUNT(CASE WHEN status = 'rejected' THEN 1 END) as rejected_evolutions,
    COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending_evolutions,
    AVG(CASE WHEN status = 'accepted' THEN 1.0 ELSE 0.0 END) as acceptance_rate,
    MAX(created_at) as latest_evolution_date,
    MIN(created_at) as earliest_evolution_date
FROM event_evolution_history;

-- 完成
SELECT 'Event scoring and evolution system database tables created successfully!' as message;
