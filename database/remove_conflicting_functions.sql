-- 删除冲突的存储过程
-- 由于有多个版本的函数，导致PostgreSQL无法确定调用哪一个

-- 删除所有update_worldview_complete函数
DROP FUNCTION IF EXISTS update_worldview_complete(character varying, character varying, text, text, jsonb, jsonb, jsonb, jsonb, jsonb, jsonb, jsonb, jsonb, jsonb, jsonb) CASCADE;
DROP FUNCTION IF EXISTS update_worldview_complete(character varying, character varying, text, text, jsonb, jsonb, jsonb, jsonb, jsonb, jsonb, jsonb, jsonb, jsonb, jsonb, jsonb) CASCADE;

-- 删除所有insert_worldview_complete函数
DROP FUNCTION IF EXISTS insert_worldview_complete(character varying, character varying, text, text, character varying, jsonb, jsonb, jsonb, jsonb, jsonb, jsonb, jsonb, jsonb, jsonb, jsonb) CASCADE;
DROP FUNCTION IF EXISTS insert_worldview_complete(character varying, character varying, text, text, jsonb, jsonb, jsonb, jsonb, jsonb, jsonb, jsonb, jsonb, jsonb, jsonb, jsonb) CASCADE;
DROP FUNCTION IF EXISTS insert_worldview_complete(character varying, character varying, text, text, character varying, jsonb, jsonb, jsonb, jsonb, jsonb, jsonb, jsonb, jsonb, jsonb, jsonb, jsonb) CASCADE;

-- 验证删除结果
SELECT 
    proname, 
    pronargs, 
    proargtypes::regtype[] as arg_types
FROM pg_proc 
WHERE proname IN ('update_worldview_complete', 'insert_worldview_complete')
ORDER BY proname, pronargs;
