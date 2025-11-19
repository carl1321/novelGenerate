-- 为events表添加缺失的字段
-- 用于支持完整的事件编辑功能

-- 添加事件内容相关字段
ALTER TABLE events ADD COLUMN IF NOT EXISTS setting VARCHAR(200);
ALTER TABLE events ADD COLUMN IF NOT EXISTS duration VARCHAR(100);
ALTER TABLE events ADD COLUMN IF NOT EXISTS participants JSONB DEFAULT '[]'::jsonb;

-- 添加剧情相关字段
ALTER TABLE events ADD COLUMN IF NOT EXISTS plot_impact TEXT;
ALTER TABLE events ADD COLUMN IF NOT EXISTS foreshadowing_elements JSONB DEFAULT '[]'::jsonb;

-- 添加核心字段
ALTER TABLE events ADD COLUMN IF NOT EXISTS dramatic_tension INTEGER DEFAULT 5;
ALTER TABLE events ADD COLUMN IF NOT EXISTS emotional_impact INTEGER DEFAULT 5;

-- 添加兼容字段
ALTER TABLE events ADD COLUMN IF NOT EXISTS character_impact JSONB DEFAULT '{}'::jsonb;
ALTER TABLE events ADD COLUMN IF NOT EXISTS conflict_core TEXT;
ALTER TABLE events ADD COLUMN IF NOT EXISTS logical_consistency TEXT;
ALTER TABLE events ADD COLUMN IF NOT EXISTS realistic_elements TEXT;

-- 添加元数据字段
ALTER TABLE events ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '{}'::jsonb;

-- 添加注释
COMMENT ON COLUMN events.setting IS '事件发生地点';
COMMENT ON COLUMN events.duration IS '事件持续时间';
COMMENT ON COLUMN events.participants IS '参与角色列表（JSON数组）';
COMMENT ON COLUMN events.plot_impact IS '对剧情的影响';
COMMENT ON COLUMN events.foreshadowing_elements IS '伏笔元素（JSON数组）';
COMMENT ON COLUMN events.dramatic_tension IS '戏剧张力 (1-10)';
COMMENT ON COLUMN events.emotional_impact IS '情感冲击 (1-10)';
COMMENT ON COLUMN events.character_impact IS '角色影响（JSON对象）';
COMMENT ON COLUMN events.conflict_core IS '核心矛盾';
COMMENT ON COLUMN events.logical_consistency IS '逻辑一致性';
COMMENT ON COLUMN events.realistic_elements IS '现实元素';
COMMENT ON COLUMN events.metadata IS '扩展元数据（JSON对象）';

-- 更新现有数据的默认值
UPDATE events 
SET 
    setting = '',
    duration = '',
    participants = '[]'::jsonb,
    plot_impact = '',
    foreshadowing_elements = '[]'::jsonb,
    dramatic_tension = 5,
    emotional_impact = 5,
    character_impact = '{}'::jsonb,
    conflict_core = '',
    logical_consistency = '',
    realistic_elements = '',
    metadata = '{}'::jsonb
WHERE 
    setting IS NULL 
    OR duration IS NULL 
    OR participants IS NULL 
    OR plot_impact IS NULL 
    OR foreshadowing_elements IS NULL 
    OR dramatic_tension IS NULL 
    OR emotional_impact IS NULL 
    OR character_impact IS NULL 
    OR conflict_core IS NULL 
    OR logical_consistency IS NULL 
    OR realistic_elements IS NULL 
    OR metadata IS NULL;
