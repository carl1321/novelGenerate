-- 修复correction_history表中字段长度问题
-- detailed_plot_id字段长度不够，需要增加

-- 首先备份数据
CREATE TEMPORARY TABLE correction_history_backup AS 
SELECT * FROM correction_history;

-- 修改字段长度
ALTER TABLE correction_history 
ALTER COLUMN detailed_plot_id TYPE VARCHAR(100);

ALTER TABLE correction_history 
ALTER COLUMN id TYPE VARCHAR(100);

ALTER TABLE correction_history 
ALTER COLUMN corrected_by TYPE VARCHAR(100);

-- 验证修改结果
SELECT 
    column_name, 
    character_maximum_length, 
    data_type
FROM information_schema.columns 
WHERE table_name = 'correction_history' 
AND column_name IN ('id', 'detailed_plot_id', 'corrected_by')
ORDER BY ordinal_position;

-- 添加注释
COMMENT ON COLUMN correction_history.detailed_plot_id IS '详细剧情ID（已修正长度限制）';
COMMENT ON COLUMN correction_history.id IS '修正记录ID（已修正长度限制）';
COMMENT ON COLUMN correction_history.corrected_by IS '修正者（已修正长度限制）';
