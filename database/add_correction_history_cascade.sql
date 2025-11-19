-- 为修正历史记录添加级联删除约束
-- 确保删除详细剧情时自动删除相关修正记录

-- 检查是否存在外键约束
SELECT 
    tc.constraint_name,
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name 
FROM information_schema.table_constraints AS tc 
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY' 
    AND tc.table_name = 'correction_history';

-- 如果没有外键约束，则添加一个（可选）
-- 注释：由于采用应用层级联删除，这里暂时不添加数据库外键约束
-- 以保持应用的灵活性

-- 添加注释说明约束关系
COMMENT ON TABLE correction_history IS '详细剧情修正历史表 - 与detailed_plots表相关联，应用层处理级联删除';
COMMENT ON COLUMN correction_history.detailed_plot_id IS '详细剧情ID - 删除详细剧情时会级联删除所有相关修正记录';

-- 创建索引以提高关联查询性能
CREATE INDEX IF NOT EXISTS idx_correction_history_detailed_plot_fk 
ON correction_history(detailed_plot_id);

-- 显示最终的约束和索引信息
SELECT 
    'Foreign Keys:' as info_type,
    count(*) as count
FROM information_schema.table_constraints 
WHERE table_name = 'correction_history' 
    AND constraint_type = 'FOREIGN KEY'

UNION ALL

SELECT 
    'Indexes:' as info_type,
    count(*) as count  
FROM pg_indexes 
WHERE tablename = 'correction_history';
