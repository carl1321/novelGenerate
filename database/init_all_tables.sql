-- ============================================
-- 完整数据库初始化脚本
-- 生成时间: 2025-11-19 11:13:24
-- PostgreSQL 17 兼容
-- 包含所有表、视图、函数、索引、触发器等
-- ============================================

-- ============================================
-- 第一部分：枚举类型
-- ============================================

DO $$ BEGIN
    CREATE TYPE character_role_type AS ENUM ('主角', '配角', '反派', '导师', '盟友', '路人');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;


-- ============================================
-- 第二部分：函数
-- ============================================

CREATE OR REPLACE FUNCTION public.cleanup_sync_functions()
 RETURNS void
 LANGUAGE plpgsql
AS $function$
BEGIN
    DROP FUNCTION IF EXISTS sync_chapter_outline_fields_from_plot();
    DROP FUNCTION IF EXISTS extract_worldview_elements_from_acts();
    DROP FUNCTION IF EXISTS validate_chapter_outline_sync();
    RAISE NOTICE '同步函数已清理';
END;
$function$
;

CREATE OR REPLACE FUNCTION public.create_characters_batch_simple(p_worldview_id character varying, p_characters_data jsonb, p_created_by character varying DEFAULT 'system'::character varying)
 RETURNS jsonb
 LANGUAGE plpgsql
AS $function$
DECLARE
    char_data JSONB;
    char_id VARCHAR(255);
    result JSONB := '[]'::jsonb;
    char_record RECORD;
BEGIN
    -- 遍历角色数据数组
    FOR char_data IN SELECT * FROM jsonb_array_elements(p_characters_data)
    LOOP
        -- 生成角色ID
        char_id := 'char_' || extract(epoch from now())::bigint || '_' || floor(random() * 10000)::int;
        
        -- 插入角色记录
        INSERT INTO characters (
            character_id, worldview_id, name, age, gender, role_type,
            cultivation_level, element_type, background, current_location,
            organization_id, personality_traits, goals, relationships,
            techniques, artifacts, resources, stats, metadata, created_by
        ) VALUES (
            char_id,
            p_worldview_id,
            char_data->>'name',
            (char_data->>'age')::integer,
            char_data->>'gender',
            COALESCE(char_data->>'role_type', '配角')::character_role_type,
            char_data->>'cultivation_level',
            char_data->>'element_type',
            char_data->>'background',
            char_data->>'current_location',
            char_data->>'organization_id',
            COALESCE(char_data->'personality_traits', '[]'::jsonb),
            COALESCE(char_data->'goals', '[]'::jsonb),
            COALESCE(char_data->'relationships', '{}'::jsonb),
            COALESCE(char_data->'techniques', '[]'::jsonb),
            COALESCE(char_data->'artifacts', '[]'::jsonb),
            COALESCE(char_data->'resources', '{}'::jsonb),
            COALESCE(char_data->'stats', '{}'::jsonb),
            COALESCE(char_data->'metadata', '{}'::jsonb),
            p_created_by
        ) RETURNING character_id, name INTO char_record;
        
        -- 添加角色ID到结果
        result := result || jsonb_build_object('character_id', char_record.character_id, 'name', char_record.name);
    END LOOP;
    
    RETURN result;
END;
$function$
;

CREATE OR REPLACE FUNCTION public.create_event_evolution_version(p_original_event_id character varying, p_new_title character varying, p_new_event_type character varying, p_new_description text, p_new_outcome text, p_evolution_reason text DEFAULT ''::text, p_score_id integer DEFAULT NULL::integer)
 RETURNS character varying
 LANGUAGE plpgsql
AS $function$
DECLARE
    v_new_evolution_id VARCHAR(50);
    v_next_version INTEGER;
    v_plot_outline_id VARCHAR(50);
    v_chapter_number INTEGER;
    v_sequence_order INTEGER;
    v_current_version_id VARCHAR(50);
BEGIN
    -- 获取原始事件信息
    SELECT plot_outline_id, chapter_number, sequence_order
    INTO v_plot_outline_id, v_chapter_number, v_sequence_order
    FROM events 
    WHERE id = p_original_event_id
    LIMIT 1;
    
    -- 获取当前版本ID
    SELECT id INTO v_current_version_id
    FROM event_evolution_history 
    WHERE original_event_id = p_original_event_id 
      AND is_current_version = TRUE
    LIMIT 1;
    
    -- 获取下一个版本号
    SELECT COALESCE(MAX(version), 0) + 1
    INTO v_next_version
    FROM event_evolution_history 
    WHERE original_event_id = p_original_event_id;
    
    -- 生成新的进化ID
    v_new_evolution_id := 'evo_' || substr(md5(random()::text), 1, 8);
    
    -- 将当前版本标记为非当前版本
    UPDATE event_evolution_history 
    SET is_current_version = FALSE 
    WHERE original_event_id = p_original_event_id 
      AND is_current_version = TRUE;
    
    -- 插入新版本到进化历史表
    INSERT INTO event_evolution_history (
        id, original_event_id, version, is_current_version,
        title, event_type, description, outcome,
        plot_outline_id, chapter_number, sequence_order,
        evolution_reason, score_id, parent_version_id,
        created_at, updated_at
    ) VALUES (
        v_new_evolution_id, p_original_event_id, v_next_version, TRUE,
        p_new_title, p_new_event_type, p_new_description, p_new_outcome,
        v_plot_outline_id, v_chapter_number, v_sequence_order,
        p_evolution_reason, p_score_id, v_current_version_id,
        CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
    );
    
    RETURN v_new_evolution_id;
END;
$function$
;

CREATE OR REPLACE FUNCTION public.create_event_version(p_event_id character varying, p_new_title character varying, p_new_event_type character varying, p_new_description text, p_new_outcome text)
 RETURNS character varying
 LANGUAGE plpgsql
AS $function$
DECLARE
    v_next_version INTEGER;
    v_plot_outline_id VARCHAR(50);
    v_chapter_number INTEGER;
    v_sequence_order INTEGER;
BEGIN
    -- 获取原始事件信息
    SELECT plot_outline_id, chapter_number, sequence_order
    INTO v_plot_outline_id, v_chapter_number, v_sequence_order
    FROM events 
    WHERE id = p_event_id 
      AND is_current_version = TRUE
    LIMIT 1;
    
    -- 获取下一个版本号
    SELECT COALESCE(MAX(version), 0) + 1
    INTO v_next_version
    FROM events 
    WHERE id = p_event_id;
    
    -- 将当前版本标记为非当前版本
    UPDATE events 
    SET is_current_version = FALSE 
    WHERE id = p_event_id 
      AND is_current_version = TRUE;
    
    -- 插入新版本（使用相同的ID）
    INSERT INTO events (
        id, version, is_current_version,
        title, event_type, description, outcome,
        plot_outline_id, chapter_number, sequence_order,
        created_at, updated_at
    ) VALUES (
        p_event_id, v_next_version, TRUE,
        p_new_title, p_new_event_type, p_new_description, p_new_outcome,
        v_plot_outline_id, v_chapter_number, v_sequence_order,
        CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
    );
    
    RETURN p_event_id;
END;
$function$
;

CREATE OR REPLACE FUNCTION public.delete_event(p_id character varying)
 RETURNS boolean
 LANGUAGE plpgsql
AS $function$
BEGIN
    DELETE FROM events WHERE id = p_id;
    RETURN FOUND;
EXCEPTION
    WHEN OTHERS THEN
        RETURN FALSE;
END;
$function$
;

CREATE OR REPLACE FUNCTION public.delete_event_evolution_version(p_original_event_id character varying, p_version integer DEFAULT NULL::integer)
 RETURNS boolean
 LANGUAGE plpgsql
AS $function$
BEGIN
    IF p_version IS NULL THEN
        -- 删除所有版本
        DELETE FROM event_evolution_history 
        WHERE original_event_id = p_original_event_id;
    ELSE
        -- 删除指定版本
        DELETE FROM event_evolution_history 
        WHERE original_event_id = p_original_event_id 
          AND version = p_version;
    END IF;
    
    RETURN TRUE;
END;
$function$
;

CREATE OR REPLACE FUNCTION public.delete_event_version(p_event_id character varying, p_version integer DEFAULT NULL::integer)
 RETURNS boolean
 LANGUAGE plpgsql
AS $function$
DECLARE
    v_deleted_count INTEGER;
BEGIN
    IF p_version IS NULL THEN
        -- 删除整个事件的所有版本
        DELETE FROM events WHERE id = p_event_id;
        GET DIAGNOSTICS v_deleted_count = ROW_COUNT;
    ELSE
        -- 只删除指定版本
        DELETE FROM events WHERE id = p_event_id AND version = p_version;
        GET DIAGNOSTICS v_deleted_count = ROW_COUNT;
        
        -- 如果删除的是当前版本，需要将其他版本设为当前版本
        IF v_deleted_count > 0 THEN
            UPDATE events 
            SET is_current_version = TRUE 
            WHERE id = p_event_id 
              AND version = (
                  SELECT MAX(version) 
                  FROM events 
                  WHERE id = p_event_id
              );
        END IF;
    END IF;
    
    RETURN v_deleted_count > 0;
END;
$function$
;

CREATE OR REPLACE FUNCTION public.delete_simple_event_new(p_id character varying)
 RETURNS boolean
 LANGUAGE plpgsql
AS $function$
BEGIN
    DELETE FROM simple_events_table WHERE id = p_id;
    RETURN FOUND;
EXCEPTION
    WHEN OTHERS THEN
        RETURN FALSE;
END;
$function$
;

CREATE OR REPLACE FUNCTION public.extract_worldview_elements_from_acts()
 RETURNS integer
 LANGUAGE plpgsql
AS $function$
DECLARE
    updated_count INTEGER := 0;
    plot_record RECORD;
    act_data JSONB;
    worldview_elements JSONB;
    chapter_record RECORD;
BEGIN
    -- 遍历所有剧情大纲
    FOR plot_record IN 
        SELECT id, story_framework 
        FROM plot_outlines 
        WHERE story_framework IS NOT NULL
    LOOP
        -- 提取世界观元素
        worldview_elements := '[]'::jsonb;
        
        -- 从幕次中提取世界观元素
        FOR act_data IN 
            SELECT jsonb_array_elements(plot_record.story_framework->'acts')
        LOOP
            IF act_data ? 'worldview_elements' THEN
                worldview_elements := worldview_elements || (act_data->'worldview_elements');
            END IF;
        END LOOP;
        
        -- 去重
        SELECT jsonb_agg(DISTINCT value) 
        INTO worldview_elements
        FROM jsonb_array_elements(worldview_elements);
        
        -- 更新该剧情大纲下的所有章节大纲
        UPDATE chapter_outlines 
        SET 
            worldview_elements = worldview_elements,
            updated_at = CURRENT_TIMESTAMP
        WHERE plot_outline_id = plot_record.id
        AND (
            chapter_outlines.worldview_elements IS NULL 
            OR chapter_outlines.worldview_elements = '[]'::jsonb
        );
        
        GET DIAGNOSTICS updated_count = ROW_COUNT;
        
        RAISE NOTICE '剧情大纲 % 提取了世界观元素，更新了 % 个章节大纲', plot_record.id, updated_count;
    END LOOP;
    
    RETURN updated_count;
END;
$function$
;

CREATE OR REPLACE FUNCTION public.get_chapter_outline_stats(plot_id character varying)
 RETURNS jsonb
 LANGUAGE plpgsql
AS $function$
DECLARE
    result JSONB;
BEGIN
    SELECT jsonb_build_object(
        'total_chapters', COUNT(*),
        'outline_chapters', COUNT(*) FILTER (WHERE status = '大纲'),
        'draft_chapters', COUNT(*) FILTER (WHERE status = '草稿'),
        'completed_chapters', COUNT(*) FILTER (WHERE status = '已完成'),
        'total_estimated_words', COALESCE(SUM(estimated_word_count), 0),
        'avg_words_per_chapter', COALESCE(AVG(estimated_word_count), 0),
        'total_scenes', COALESCE(
            (SELECT COUNT(*) FROM scenes s 
             JOIN chapter_outlines co ON s.chapter_outline_id = co.id 
             WHERE co.plot_outline_id = plot_id), 0
        )
    ) INTO result
    FROM chapter_outlines
    WHERE plot_outline_id = plot_id;
    
    RETURN result;
END;
$function$
;

CREATE OR REPLACE FUNCTION public.get_chapter_outline_v2_stats(plot_id character varying)
 RETURNS jsonb
 LANGUAGE plpgsql
AS $function$
DECLARE
    result JSONB;
BEGIN
    SELECT jsonb_build_object(
        'total_chapters', COUNT(*),
        'outline_chapters', COUNT(*) FILTER (WHERE status = '大纲'),
        'draft_chapters', COUNT(*) FILTER (WHERE status = '草稿'),
        'completed_chapters', COUNT(*) FILTER (WHERE status = '已完成'),
        'total_estimated_words', COALESCE(SUM(estimated_word_count), 0),
        'total_estimated_reading_time', COALESCE(SUM(estimated_reading_time), 0),
        'avg_words_per_chapter', COALESCE(AVG(estimated_word_count), 0),
        'avg_reading_time_per_chapter', COALESCE(AVG(estimated_reading_time), 0),
        'total_scenes', COALESCE(
            (SELECT COUNT(*) FROM scenes s 
             JOIN chapter_outlines_v2 co ON s.chapter_outline_id = co.id 
             WHERE co.plot_outline_id = plot_id), 0
        )
    ) INTO result
    FROM chapter_outlines_v2
    WHERE plot_outline_id = plot_id;
    
    RETURN result;
END;
$function$
;

CREATE OR REPLACE FUNCTION public.get_chapter_outline_v2_with_details(chapter_id character varying)
 RETURNS jsonb
 LANGUAGE plpgsql
AS $function$
DECLARE
    result JSONB;
BEGIN
    SELECT jsonb_build_object(
        'chapter_outline', row_to_json(co),
        'scenes', COALESCE(
            (SELECT jsonb_agg(row_to_json(s) ORDER BY s.scene_number)
             FROM scenes s 
             WHERE s.chapter_outline_id = chapter_id),
            '[]'::jsonb
        ),
        'character_developments', COALESCE(
            (SELECT jsonb_agg(row_to_json(cd))
             FROM character_developments cd 
             WHERE cd.chapter_outline_id = chapter_id),
            '[]'::jsonb
        )
    ) INTO result
    FROM chapter_outlines_v2 co
    WHERE co.id = chapter_id;
    
    RETURN result;
END;
$function$
;

CREATE OR REPLACE FUNCTION public.get_chapter_outline_with_details(chapter_id character varying)
 RETURNS jsonb
 LANGUAGE plpgsql
AS $function$
DECLARE
    result JSONB;
BEGIN
    SELECT jsonb_build_object(
        'chapter_outline', row_to_json(co),
        'scenes', COALESCE(
            (SELECT jsonb_agg(row_to_json(s) ORDER BY s.scene_number)
             FROM scenes s 
             WHERE s.chapter_outline_id = chapter_id),
            '[]'::jsonb
        )
    ) INTO result
    FROM chapter_outlines co
    WHERE co.id = chapter_id;
    
    RETURN result;
END;
$function$
;

CREATE OR REPLACE FUNCTION public.get_character_stats_by_type_simple(p_worldview_id character varying)
 RETURNS jsonb
 LANGUAGE plpgsql
AS $function$
DECLARE
    result JSONB;
BEGIN
    SELECT jsonb_object_agg(role_type, count) INTO result
    FROM (
        SELECT role_type, COUNT(*) as count
        FROM characters 
        WHERE worldview_id = p_worldview_id AND status = 'active'
        GROUP BY role_type
    ) as stats;
    
    RETURN COALESCE(result, '{}'::jsonb);
END;
$function$
;

CREATE OR REPLACE FUNCTION public.get_detailed_plot_all_versions(p_detailed_plot_id character varying)
 RETURNS TABLE(id integer, detailed_plot_id character varying, version_type character varying, version_number integer, is_current_version boolean, title character varying, content text, word_count integer, source_table character varying, source_record_id character varying, version_notes text, created_by character varying, created_at timestamp without time zone, updated_at timestamp without time zone)
 LANGUAGE plpgsql
AS $function$
BEGIN
    RETURN QUERY
    SELECT dpv.id, dpv.detailed_plot_id, dpv.version_type, dpv.version_number,
           dpv.is_current_version, dpv.title, dpv.content, dpv.word_count,
           dpv.source_table, dpv.source_record_id, dpv.version_notes,
           dpv.created_by, dpv.created_at, dpv.updated_at
    FROM detailed_plot_versions dpv
    WHERE dpv.detailed_plot_id = p_detailed_plot_id
    ORDER BY dpv.updated_at DESC, dpv.created_at DESC;
END;
$function$
;

CREATE OR REPLACE FUNCTION public.get_detailed_plot_latest_version(p_detailed_plot_id character varying)
 RETURNS TABLE(id integer, detailed_plot_id character varying, version_type character varying, version_number integer, is_current_version boolean, title character varying, content text, word_count integer, source_table character varying, source_record_id character varying, version_notes text, created_by character varying, created_at timestamp without time zone, updated_at timestamp without time zone)
 LANGUAGE plpgsql
AS $function$
BEGIN
    RETURN QUERY
    SELECT dpv.id, dpv.detailed_plot_id, dpv.version_type, dpv.version_number,
           dpv.is_current_version, dpv.title, dpv.content, dpv.word_count,
           dpv.source_table, dpv.source_record_id, dpv.version_notes,
           dpv.created_by, dpv.created_at, dpv.updated_at
    FROM detailed_plot_versions dpv
    WHERE dpv.detailed_plot_id = p_detailed_plot_id 
      AND dpv.is_current_version = TRUE
    LIMIT 1;
END;
$function$
;

CREATE OR REPLACE FUNCTION public.get_event_all_evolution_versions(p_original_event_id character varying)
 RETURNS TABLE(id character varying, original_event_id character varying, version integer, is_current_version boolean, title character varying, event_type character varying, description text, outcome text, plot_outline_id character varying, chapter_number integer, sequence_order integer, evolution_reason text, score_id integer, parent_version_id character varying, created_at timestamp without time zone, updated_at timestamp without time zone)
 LANGUAGE plpgsql
AS $function$
BEGIN
    RETURN QUERY
    SELECT 
        eeh.id, eeh.original_event_id, eeh.version, eeh.is_current_version,
        eeh.title, eeh.event_type, eeh.description, eeh.outcome,
        eeh.plot_outline_id, eeh.chapter_number, eeh.sequence_order,
        eeh.evolution_reason, eeh.score_id, eeh.parent_version_id,
        eeh.created_at, eeh.updated_at
    FROM event_evolution_history eeh
    WHERE eeh.original_event_id = p_original_event_id
    ORDER BY eeh.version ASC;
END;
$function$
;

CREATE OR REPLACE FUNCTION public.get_event_all_versions(p_event_id character varying)
 RETURNS TABLE(id character varying, version integer, is_current_version boolean, title character varying, event_type character varying, description text, outcome text, plot_outline_id character varying, chapter_number integer, sequence_order integer, created_at timestamp without time zone, updated_at timestamp without time zone)
 LANGUAGE plpgsql
AS $function$
BEGIN
    RETURN QUERY
    SELECT 
        e.id, e.version, e.is_current_version,
        e.title, e.event_type, e.description, e.outcome,
        e.plot_outline_id, e.chapter_number, e.sequence_order,
        e.created_at, e.updated_at
    FROM events e
    WHERE e.id = p_event_id
    ORDER BY e.version ASC;
END;
$function$
;

CREATE OR REPLACE FUNCTION public.get_event_by_id(event_id character varying)
 RETURNS TABLE(id character varying, plot_outline_id character varying, chapter_number integer, sequence_order integer, title character varying, event_type character varying, description text, outcome text, created_at timestamp without time zone, updated_at timestamp without time zone)
 LANGUAGE plpgsql
AS $function$
BEGIN
    RETURN QUERY
    SELECT 
        e.id, e.plot_outline_id, e.chapter_number, e.sequence_order,
        e.title, e.event_type, e.description, e.outcome,
        e.created_at, e.updated_at
    FROM events e
    WHERE e.id = event_id;
END;
$function$
;

CREATE OR REPLACE FUNCTION public.get_event_evolution_history(event_id_param character varying)
 RETURNS TABLE(id integer, original_event_id character varying, evolved_event_id character varying, score_id integer, evolution_reason text, status character varying, created_at timestamp without time zone)
 LANGUAGE plpgsql
AS $function$
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
$function$
;

CREATE OR REPLACE FUNCTION public.get_event_latest_version(p_original_event_id character varying)
 RETURNS TABLE(id character varying, original_event_id character varying, version integer, is_current_version boolean, title character varying, event_type character varying, description text, outcome text, plot_outline_id character varying, chapter_number integer, sequence_order integer, evolution_reason text, score_id integer, parent_version_id character varying, created_at timestamp without time zone, updated_at timestamp without time zone)
 LANGUAGE plpgsql
AS $function$
BEGIN
    RETURN QUERY
    SELECT 
        eeh.id, eeh.original_event_id, eeh.version, eeh.is_current_version,
        eeh.title, eeh.event_type, eeh.description, eeh.outcome,
        eeh.plot_outline_id, eeh.chapter_number, eeh.sequence_order,
        eeh.evolution_reason, eeh.score_id, eeh.parent_version_id,
        eeh.created_at, eeh.updated_at
    FROM event_evolution_history eeh
    WHERE eeh.original_event_id = p_original_event_id 
      AND eeh.is_current_version = TRUE
    LIMIT 1;
END;
$function$
;

CREATE OR REPLACE FUNCTION public.get_event_score_history(event_id_param character varying)
 RETURNS TABLE(id integer, event_id character varying, protagonist_involvement numeric, plot_coherence numeric, character_development numeric, world_consistency numeric, dramatic_tension numeric, emotional_impact numeric, foreshadowing numeric, overall_quality numeric, feedback text, strengths text[], weaknesses text[], created_at timestamp without time zone)
 LANGUAGE plpgsql
AS $function$
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
$function$
;

CREATE OR REPLACE FUNCTION public.get_events_by_plot(plot_id character varying)
 RETURNS TABLE(id character varying, plot_outline_id character varying, chapter_number integer, sequence_order integer, title character varying, event_type character varying, description text, outcome text, created_at timestamp without time zone, updated_at timestamp without time zone)
 LANGUAGE plpgsql
AS $function$
BEGIN
    RETURN QUERY
    SELECT 
        e.id, e.plot_outline_id, e.chapter_number, e.sequence_order,
        e.title, e.event_type, e.description, e.outcome,
        e.created_at, e.updated_at
    FROM events e
    WHERE e.plot_outline_id = plot_id
    ORDER BY e.sequence_order, e.created_at;
END;
$function$
;

CREATE OR REPLACE FUNCTION public.get_events_paginated(p_plot_id character varying, p_page integer DEFAULT 1, p_page_size integer DEFAULT 20)
 RETURNS TABLE(id character varying, plot_outline_id character varying, chapter_number integer, sequence_order integer, title character varying, event_type character varying, description text, outcome text, created_at timestamp without time zone, updated_at timestamp without time zone, total_count bigint)
 LANGUAGE plpgsql
AS $function$
DECLARE
    offset_value INTEGER;
BEGIN
    offset_value := (p_page - 1) * p_page_size;
    
    RETURN QUERY
    SELECT 
        e.id, e.plot_outline_id, e.chapter_number, e.sequence_order,
        e.title, e.event_type, e.description, e.outcome,
        e.created_at, e.updated_at,
        COUNT(*) OVER() as total_count
    FROM events e
    WHERE e.plot_outline_id = p_plot_id
    ORDER BY e.sequence_order, e.created_at
    LIMIT p_page_size OFFSET offset_value;
END;
$function$
;

CREATE OR REPLACE FUNCTION public.get_events_stats(plot_id character varying)
 RETURNS TABLE(total_events bigint, events_by_type jsonb, events_by_chapter jsonb)
 LANGUAGE plpgsql
AS $function$
DECLARE
    type_stats JSONB;
    chapter_stats JSONB;
BEGIN
    -- 获取总数
    SELECT COUNT(*) INTO total_events FROM events WHERE plot_outline_id = plot_id;
    
    -- 按类型统计
    SELECT jsonb_object_agg(event_type, type_count) INTO type_stats
    FROM (
        SELECT event_type, COUNT(*) as type_count
        FROM events 
        WHERE plot_outline_id = plot_id
        GROUP BY event_type
    ) t;
    
    -- 按章节统计
    SELECT jsonb_object_agg(
        COALESCE(chapter_number::TEXT, '未分配'), 
        chapter_count
    ) INTO chapter_stats
    FROM (
        SELECT chapter_number, COUNT(*) as chapter_count
        FROM events 
        WHERE plot_outline_id = plot_id
        GROUP BY chapter_number
    ) c;
    
    RETURN QUERY SELECT total_events, type_stats, chapter_stats;
END;
$function$
;

CREATE OR REPLACE FUNCTION public.get_latest_event_score(event_id_param character varying)
 RETURNS TABLE(id integer, event_id character varying, protagonist_involvement numeric, plot_coherence numeric, character_development numeric, world_consistency numeric, dramatic_tension numeric, emotional_impact numeric, foreshadowing numeric, overall_quality numeric, feedback text, strengths text[], weaknesses text[], created_at timestamp without time zone)
 LANGUAGE plpgsql
AS $function$
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
$function$
;

CREATE OR REPLACE FUNCTION public.get_latest_event_version(p_event_id character varying)
 RETURNS TABLE(id character varying, version integer, is_current_version boolean, title character varying, event_type character varying, description text, outcome text, plot_outline_id character varying, chapter_number integer, sequence_order integer, created_at timestamp without time zone, updated_at timestamp without time zone)
 LANGUAGE plpgsql
AS $function$
BEGIN
    RETURN QUERY
    SELECT 
        e.id, e.version, e.is_current_version,
        e.title, e.event_type, e.description, e.outcome,
        e.plot_outline_id, e.chapter_number, e.sequence_order,
        e.created_at, e.updated_at
    FROM events e
    WHERE e.id = p_event_id 
      AND e.is_current_version = TRUE;
END;
$function$
;

CREATE OR REPLACE FUNCTION public.get_latest_versions_by_plot(p_plot_outline_id character varying)
 RETURNS TABLE(id character varying, version integer, is_current_version boolean, title character varying, event_type character varying, description text, outcome text, plot_outline_id character varying, chapter_number integer, sequence_order integer, created_at timestamp without time zone, updated_at timestamp without time zone)
 LANGUAGE plpgsql
AS $function$
BEGIN
    RETURN QUERY
    SELECT 
        e.id, e.version, e.is_current_version,
        e.title, e.event_type, e.description, e.outcome,
        e.plot_outline_id, e.chapter_number, e.sequence_order,
        e.created_at, e.updated_at
    FROM events e
    WHERE e.plot_outline_id = p_plot_outline_id 
      AND e.is_current_version = TRUE
    ORDER BY e.chapter_number ASC, e.sequence_order ASC;
END;
$function$
;

CREATE OR REPLACE FUNCTION public.get_plot_outline_chapters(plot_id character varying)
 RETURNS jsonb
 LANGUAGE plpgsql
AS $function$
DECLARE
    result JSONB;
BEGIN
    SELECT jsonb_agg(
        jsonb_build_object(
            'chapter_outline', row_to_json(co),
            'scenes', COALESCE(
                (SELECT jsonb_agg(row_to_json(s) ORDER BY s.scene_number)
                 FROM scenes s 
                 WHERE s.chapter_outline_id = co.id),
                '[]'::jsonb
            )
        ) ORDER BY co.chapter_number
    ) INTO result
    FROM chapter_outlines co
    WHERE co.plot_outline_id = plot_id;
    
    RETURN COALESCE(result, '[]'::jsonb);
END;
$function$
;

CREATE OR REPLACE FUNCTION public.get_plot_outline_chapters_v2(plot_id character varying)
 RETURNS jsonb
 LANGUAGE plpgsql
AS $function$
DECLARE
    result JSONB;
BEGIN
    SELECT jsonb_agg(
        jsonb_build_object(
            'chapter_outline', row_to_json(co),
            'scenes', COALESCE(
                (SELECT jsonb_agg(row_to_json(s) ORDER BY s.scene_number)
                 FROM scenes s 
                 WHERE s.chapter_outline_id = co.id),
                '[]'::jsonb
            ),
            'character_developments', COALESCE(
                (SELECT jsonb_agg(row_to_json(cd))
                 FROM character_developments cd 
                 WHERE cd.chapter_outline_id = co.id),
                '[]'::jsonb
            )
        ) ORDER BY co.chapter_number
    ) INTO result
    FROM chapter_outlines_v2 co
    WHERE co.plot_outline_id = plot_id;
    
    RETURN COALESCE(result, '[]'::jsonb);
END;
$function$
;

CREATE OR REPLACE FUNCTION public.get_plot_outline_stats()
 RETURNS jsonb
 LANGUAGE plpgsql
AS $function$
DECLARE
    result JSONB;
BEGIN
    SELECT jsonb_build_object(
        'total_plots', COUNT(*),
        'draft_plots', COUNT(*) FILTER (WHERE status = '草稿'),
        'planning_plots', COUNT(*) FILTER (WHERE status = '规划中'),
        'writing_plots', COUNT(*) FILTER (WHERE status = '写作中'),
        'completed_plots', COUNT(*) FILTER (WHERE status = '已完成'),
        'total_estimated_chapters', COALESCE(SUM(estimated_chapters), 0),
        'total_target_words', COALESCE(SUM(target_word_count), 0),
        'avg_word_count', COALESCE(AVG(target_word_count), 0),
        'avg_chapters', COALESCE(AVG(estimated_chapters), 0)
    ) INTO result
    FROM plot_outlines;
    
    RETURN result;
END;
$function$
;

CREATE OR REPLACE FUNCTION public.get_plot_outline_v2_stats()
 RETURNS jsonb
 LANGUAGE plpgsql
AS $function$
DECLARE
    result JSONB;
BEGIN
    SELECT jsonb_build_object(
        'total_plots', COUNT(*),
        'draft_plots', COUNT(*) FILTER (WHERE status = '草稿'),
        'planning_plots', COUNT(*) FILTER (WHERE status = '规划中'),
        'writing_plots', COUNT(*) FILTER (WHERE status = '写作中'),
        'completed_plots', COUNT(*) FILTER (WHERE status = '已完成'),
        'total_estimated_chapters', COALESCE(SUM(estimated_chapters), 0),
        'total_target_words', COALESCE(SUM(target_word_count), 0),
        'avg_word_count', COALESCE(AVG(target_word_count), 0),
        'avg_chapters', COALESCE(AVG(estimated_chapters), 0)
    ) INTO result
    FROM plot_outlines_v2;
    
    RETURN result;
END;
$function$
;

CREATE OR REPLACE FUNCTION public.get_plot_outline_v2_with_details(plot_id character varying)
 RETURNS jsonb
 LANGUAGE plpgsql
AS $function$
DECLARE
    result JSONB;
BEGIN
    SELECT jsonb_build_object(
        'plot_outline', row_to_json(po),
        'plot_points', COALESCE(
            (SELECT jsonb_agg(row_to_json(pp) ORDER BY pp.position)
             FROM plot_points pp 
             WHERE pp.plot_outline_id = plot_id),
            '[]'::jsonb
        ),
        'acts', COALESCE(
            (SELECT jsonb_agg(row_to_json(a) ORDER BY a.act_number)
             FROM acts a 
             WHERE a.plot_outline_id = plot_id),
            '[]'::jsonb
        ),
        'turning_points', COALESCE(
            (SELECT jsonb_agg(row_to_json(tp) ORDER BY tp.position)
             FROM turning_points tp 
             WHERE tp.plot_outline_id = plot_id),
            '[]'::jsonb
        ),
        'story_arc_points', COALESCE(
            (SELECT jsonb_agg(row_to_json(sap) ORDER BY sap.position)
             FROM story_arc_points sap 
             WHERE sap.plot_outline_id = plot_id),
            '[]'::jsonb
        )
    ) INTO result
    FROM plot_outlines_v2 po
    WHERE po.id = plot_id;
    
    RETURN result;
END;
$function$
;

CREATE OR REPLACE FUNCTION public.get_plot_outline_with_details(plot_id character varying)
 RETURNS jsonb
 LANGUAGE plpgsql
AS $function$
DECLARE
    result JSONB;
BEGIN
    SELECT jsonb_build_object(
        'plot_outline', row_to_json(po),
        'plot_points', COALESCE(
            (SELECT jsonb_agg(row_to_json(pp) ORDER BY pp.position)
             FROM plot_points pp 
             WHERE pp.plot_outline_id = plot_id),
            '[]'::jsonb
        ),
        'acts', COALESCE(
            (SELECT jsonb_agg(row_to_json(a) ORDER BY a.act_number)
             FROM acts a 
             WHERE a.plot_outline_id = plot_id),
            '[]'::jsonb
        ),
        'turning_points', COALESCE(
            (SELECT jsonb_agg(row_to_json(tp) ORDER BY tp.position)
             FROM turning_points tp 
             WHERE tp.plot_outline_id = plot_id),
            '[]'::jsonb
        ),
        'story_arc_points', COALESCE(
            (SELECT jsonb_agg(row_to_json(sap) ORDER BY sap.position)
             FROM story_arc_points sap 
             WHERE sap.plot_outline_id = plot_id),
            '[]'::jsonb
        )
    ) INTO result
    FROM plot_outlines po
    WHERE po.id = plot_id;
    
    RETURN result;
END;
$function$
;

CREATE OR REPLACE FUNCTION public.get_simple_event_by_id_new(event_id character varying)
 RETURNS TABLE(id character varying, plot_outline_id character varying, chapter_number integer, sequence_order integer, title character varying, event_type character varying, description text, outcome text, created_at timestamp without time zone, updated_at timestamp without time zone)
 LANGUAGE plpgsql
AS $function$
BEGIN
    RETURN QUERY
    SELECT 
        e.id, e.plot_outline_id, e.chapter_number, e.sequence_order,
        e.title, e.event_type, e.description, e.outcome,
        e.created_at, e.updated_at
    FROM simple_events_table e
    WHERE e.id = event_id;
END;
$function$
;

CREATE OR REPLACE FUNCTION public.get_simple_events_by_plot_new(plot_id character varying)
 RETURNS TABLE(id character varying, plot_outline_id character varying, chapter_number integer, sequence_order integer, title character varying, event_type character varying, description text, outcome text, created_at timestamp without time zone, updated_at timestamp without time zone)
 LANGUAGE plpgsql
AS $function$
BEGIN
    RETURN QUERY
    SELECT 
        e.id, e.plot_outline_id, e.chapter_number, e.sequence_order,
        e.title, e.event_type, e.description, e.outcome,
        e.created_at, e.updated_at
    FROM simple_events_table e
    WHERE e.plot_outline_id = plot_id
    ORDER BY e.sequence_order, e.created_at;
END;
$function$
;

CREATE OR REPLACE FUNCTION public.get_simple_events_paginated_new(p_plot_id character varying, p_page integer DEFAULT 1, p_page_size integer DEFAULT 20)
 RETURNS TABLE(id character varying, plot_outline_id character varying, chapter_number integer, sequence_order integer, title character varying, event_type character varying, description text, outcome text, created_at timestamp without time zone, updated_at timestamp without time zone, total_count bigint)
 LANGUAGE plpgsql
AS $function$
DECLARE
    offset_value INTEGER;
BEGIN
    offset_value := (p_page - 1) * p_page_size;
    
    RETURN QUERY
    SELECT 
        e.id, e.plot_outline_id, e.chapter_number, e.sequence_order,
        e.title, e.event_type, e.description, e.outcome,
        e.created_at, e.updated_at,
        COUNT(*) OVER() as total_count
    FROM simple_events_table e
    WHERE e.plot_outline_id = p_plot_id
    ORDER BY e.sequence_order, e.created_at
    LIMIT p_page_size OFFSET offset_value;
END;
$function$
;

CREATE OR REPLACE FUNCTION public.get_simple_events_stats_new(plot_id character varying)
 RETURNS TABLE(total_events bigint, events_by_type jsonb, events_by_chapter jsonb)
 LANGUAGE plpgsql
AS $function$
DECLARE
    type_stats JSONB;
    chapter_stats JSONB;
BEGIN
    -- 获取总数
    SELECT COUNT(*) INTO total_events FROM simple_events_table WHERE plot_outline_id = plot_id;
    
    -- 按类型统计
    SELECT jsonb_object_agg(event_type, type_count) INTO type_stats
    FROM (
        SELECT event_type, COUNT(*) as type_count
        FROM simple_events_table 
        WHERE plot_outline_id = plot_id
        GROUP BY event_type
    ) t;
    
    -- 按章节统计
    SELECT jsonb_object_agg(
        COALESCE(chapter_number::TEXT, '未分配'), 
        chapter_count
    ) INTO chapter_stats
    FROM (
        SELECT chapter_number, COUNT(*) as chapter_count
        FROM simple_events_table 
        WHERE plot_outline_id = plot_id
        GROUP BY chapter_number
    ) c;
    
    RETURN QUERY SELECT total_events, type_stats, chapter_stats;
END;
$function$
;

CREATE OR REPLACE FUNCTION public.insert_character_complete(p_character_id character varying, p_worldview_id character varying, p_name character varying, p_role_type character varying, p_age integer DEFAULT NULL::integer, p_gender character varying DEFAULT NULL::character varying, p_cultivation_level character varying DEFAULT NULL::character varying, p_element_type character varying DEFAULT NULL::character varying, p_background text DEFAULT NULL::text, p_current_location character varying DEFAULT NULL::character varying, p_organization_id character varying DEFAULT NULL::character varying, p_created_by character varying DEFAULT 'system'::character varying, p_personality_traits jsonb DEFAULT NULL::jsonb, p_goals jsonb DEFAULT NULL::jsonb, p_relationships jsonb DEFAULT NULL::jsonb, p_techniques jsonb DEFAULT NULL::jsonb, p_artifacts jsonb DEFAULT NULL::jsonb, p_resources jsonb DEFAULT NULL::jsonb, p_stats jsonb DEFAULT NULL::jsonb, p_metadata jsonb DEFAULT NULL::jsonb)
 RETURNS integer
 LANGUAGE plpgsql
AS $function$
DECLARE
    character_pk INTEGER;
BEGIN
    -- 插入角色主表
    INSERT INTO characters (
        character_id, worldview_id, name, age, gender, role_type,
        cultivation_level, element_type, background, current_location,
        organization_id, created_by
    ) VALUES (
        p_character_id, p_worldview_id, p_name, p_age, p_gender, p_role_type,
        p_cultivation_level, p_element_type, p_background, p_current_location,
        p_organization_id, p_created_by
    ) RETURNING id INTO character_pk;
    
    -- 插入性格特质
    IF p_personality_traits IS NOT NULL THEN
        INSERT INTO character_personality_traits (character_id, personality_traits)
        VALUES (p_character_id, p_personality_traits);
    END IF;
    
    -- 插入目标
    IF p_goals IS NOT NULL THEN
        INSERT INTO character_goals (character_id, goals)
        VALUES (p_character_id, p_goals);
    END IF;
    
    -- 插入关系
    IF p_relationships IS NOT NULL THEN
        INSERT INTO character_relationships (character_id, relationships)
        VALUES (p_character_id, p_relationships);
    END IF;
    
    -- 插入技能
    IF p_techniques IS NOT NULL THEN
        INSERT INTO character_techniques (character_id, techniques)
        VALUES (p_character_id, p_techniques);
    END IF;
    
    -- 插入法宝
    IF p_artifacts IS NOT NULL THEN
        INSERT INTO character_artifacts (character_id, artifacts)
        VALUES (p_character_id, p_artifacts);
    END IF;
    
    -- 插入资源
    IF p_resources IS NOT NULL THEN
        INSERT INTO character_resources (character_id, resources)
        VALUES (p_character_id, p_resources);
    END IF;
    
    -- 插入属性
    IF p_stats IS NOT NULL THEN
        INSERT INTO character_stats (character_id, stats)
        VALUES (p_character_id, p_stats);
    END IF;
    
    -- 插入元数据
    IF p_metadata IS NOT NULL THEN
        INSERT INTO character_metadata (character_id, metadata)
        VALUES (p_character_id, p_metadata);
    END IF;
    
    RETURN character_pk;
END;
$function$
;

CREATE OR REPLACE FUNCTION public.insert_event(p_id character varying, p_plot_outline_id character varying, p_title character varying, p_event_type character varying, p_description text, p_outcome text, p_chapter_number integer DEFAULT NULL::integer, p_sequence_order integer DEFAULT 0)
 RETURNS boolean
 LANGUAGE plpgsql
AS $function$
BEGIN
    INSERT INTO events (
        id, plot_outline_id, chapter_number, sequence_order,
        title, event_type, description, outcome, created_at
    ) VALUES (
        p_id, p_plot_outline_id, p_chapter_number, p_sequence_order,
        p_title, p_event_type, p_description, p_outcome, CURRENT_TIMESTAMP
    );
    RETURN TRUE;
EXCEPTION
    WHEN OTHERS THEN
        RETURN FALSE;
END;
$function$
;

CREATE OR REPLACE FUNCTION public.insert_simple_event_new(p_id character varying, p_plot_outline_id character varying, p_title character varying, p_event_type character varying, p_description text, p_outcome text, p_chapter_number integer DEFAULT NULL::integer, p_sequence_order integer DEFAULT 0)
 RETURNS boolean
 LANGUAGE plpgsql
AS $function$
BEGIN
    INSERT INTO simple_events_table (
        id, plot_outline_id, chapter_number, sequence_order,
        title, event_type, description, outcome, created_at
    ) VALUES (
        p_id, p_plot_outline_id, p_chapter_number, p_sequence_order,
        p_title, p_event_type, p_description, p_outcome, CURRENT_TIMESTAMP
    );
    RETURN TRUE;
EXCEPTION
    WHEN OTHERS THEN
        RETURN FALSE;
END;
$function$
;

CREATE OR REPLACE FUNCTION public.insert_worldview_complete(p_worldview_id character varying, p_name character varying, p_description text, p_core_concept text, p_created_by character varying, p_cultivation_realms jsonb DEFAULT NULL::jsonb, p_energy_types jsonb DEFAULT NULL::jsonb, p_technique_categories jsonb DEFAULT NULL::jsonb, p_regions jsonb DEFAULT NULL::jsonb, p_main_regions jsonb DEFAULT NULL::jsonb, p_special_locations jsonb DEFAULT NULL::jsonb, p_organizations jsonb DEFAULT NULL::jsonb, p_social_system jsonb DEFAULT NULL::jsonb, p_historical_events jsonb DEFAULT NULL::jsonb, p_cultural_features jsonb DEFAULT NULL::jsonb, p_current_conflicts jsonb DEFAULT NULL::jsonb)
 RETURNS integer
 LANGUAGE plpgsql
AS $function$
DECLARE
    worldview_pk INTEGER;
BEGIN
    -- 插入主表
    INSERT INTO worldviews (worldview_id, name, description, core_concept, created_by)
    VALUES (p_worldview_id, p_name, p_description, p_core_concept, p_created_by)
    RETURNING id INTO worldview_pk;
    
    -- 插入力量体系
    IF p_cultivation_realms IS NOT NULL OR p_energy_types IS NOT NULL OR p_technique_categories IS NOT NULL THEN
        INSERT INTO power_systems (worldview_id, cultivation_realms, energy_types, technique_categories)
        VALUES (p_worldview_id, p_cultivation_realms, p_energy_types, p_technique_categories);
    END IF;
    
    -- 插入地理设定
    IF p_regions IS NOT NULL OR p_main_regions IS NOT NULL OR p_special_locations IS NOT NULL THEN
        INSERT INTO geographies (worldview_id, regions, main_regions, special_locations)
        VALUES (p_worldview_id, p_regions, p_main_regions, p_special_locations);
    END IF;
    
    -- 插入社会组织
    IF p_organizations IS NOT NULL OR p_social_system IS NOT NULL THEN
        INSERT INTO societies (worldview_id, organizations, social_system)
        VALUES (p_worldview_id, p_organizations, p_social_system);
    END IF;
    
    -- 插入历史文化
    IF p_historical_events IS NOT NULL OR p_cultural_features IS NOT NULL OR p_current_conflicts IS NOT NULL THEN
        INSERT INTO history_cultures (worldview_id, historical_events, cultural_features, current_conflicts)
        VALUES (p_worldview_id, p_historical_events, p_cultural_features, p_current_conflicts);
    END IF;
    
    RETURN worldview_pk;
END;
$function$
;

CREATE OR REPLACE FUNCTION public.insert_worldview_complete(p_worldview_id character varying, p_name character varying, p_description text, p_core_concept text, p_created_by character varying, p_cultivation_realms jsonb DEFAULT NULL::jsonb, p_energy_types jsonb DEFAULT NULL::jsonb, p_technique_categories jsonb DEFAULT NULL::jsonb, p_main_regions jsonb DEFAULT NULL::jsonb, p_special_locations jsonb DEFAULT NULL::jsonb, p_organizations jsonb DEFAULT NULL::jsonb, p_social_hierarchy jsonb DEFAULT NULL::jsonb, p_cultural_norms jsonb DEFAULT NULL::jsonb, p_events jsonb DEFAULT NULL::jsonb, p_timeline jsonb DEFAULT NULL::jsonb)
 RETURNS integer
 LANGUAGE plpgsql
AS $function$
DECLARE
    worldview_db_id INTEGER;
BEGIN
    -- 插入世界观主表
    INSERT INTO worldviews (worldview_id, name, description, core_concept, created_by)
    VALUES (p_worldview_id, p_name, p_description, p_core_concept, p_created_by)
    RETURNING id INTO worldview_db_id;
    
    -- 插入力量体系
    IF p_cultivation_realms IS NOT NULL OR p_energy_types IS NOT NULL OR p_technique_categories IS NOT NULL THEN
        INSERT INTO power_systems (worldview_id, cultivation_realms, energy_types, technique_categories)
        VALUES (p_worldview_id, p_cultivation_realms, p_energy_types, p_technique_categories);
    END IF;
    
    -- 插入地理设定
    IF p_main_regions IS NOT NULL OR p_special_locations IS NOT NULL THEN
        INSERT INTO geographies (worldview_id, main_regions, special_locations)
        VALUES (p_worldview_id, p_main_regions, p_special_locations);
    END IF;
    
    -- 插入社会组织
    IF p_organizations IS NOT NULL OR p_social_hierarchy IS NOT NULL OR p_cultural_norms IS NOT NULL THEN
        INSERT INTO societies (worldview_id, organizations, social_hierarchy, cultural_norms)
        VALUES (p_worldview_id, p_organizations, p_social_hierarchy, p_cultural_norms);
    END IF;
    
    -- 插入历史事件
    IF p_events IS NOT NULL OR p_timeline IS NOT NULL THEN
        INSERT INTO historical_events (worldview_id, events, timeline)
        VALUES (p_worldview_id, p_events, p_timeline);
    END IF;
    
    RETURN worldview_db_id;
END;
$function$
;

CREATE OR REPLACE FUNCTION public.insert_worldview_complete(p_worldview_id character varying, p_name character varying DEFAULT NULL::character varying, p_description text DEFAULT NULL::text, p_core_concept text DEFAULT NULL::text, p_cultivation_realms jsonb DEFAULT NULL::jsonb, p_energy_types jsonb DEFAULT NULL::jsonb, p_technique_categories jsonb DEFAULT NULL::jsonb, p_regions jsonb DEFAULT NULL::jsonb, p_main_regions jsonb DEFAULT NULL::jsonb, p_special_locations jsonb DEFAULT NULL::jsonb, p_organizations jsonb DEFAULT NULL::jsonb, p_social_hierarchy jsonb DEFAULT NULL::jsonb, p_historical_events jsonb DEFAULT NULL::jsonb, p_cultural_features jsonb DEFAULT NULL::jsonb, p_current_conflicts jsonb DEFAULT NULL::jsonb)
 RETURNS boolean
 LANGUAGE plpgsql
AS $function$
BEGIN
    -- 插入世界观基本信息
    INSERT INTO worldviews (worldview_id, name, description, core_concept)
    VALUES (p_worldview_id, p_name, p_description, p_core_concept);

    -- 插入力量体系
    INSERT INTO power_systems (worldview_id, cultivation_realms, energy_types, technique_categories)
    VALUES (p_worldview_id, p_cultivation_realms, p_energy_types, p_technique_categories);

    -- 插入地理设定
    INSERT INTO geographies (worldview_id, regions, main_regions, special_locations)
    VALUES (p_worldview_id, p_regions, p_main_regions, p_special_locations);

    -- 插入社会结构
    INSERT INTO societies (worldview_id, organizations, social_hierarchy)
    VALUES (p_worldview_id, p_organizations, p_social_hierarchy);

    -- 插入历史文化
    INSERT INTO history_cultures (worldview_id, historical_events, cultural_features, current_conflicts)
    VALUES (p_worldview_id, p_historical_events, p_cultural_features, p_current_conflicts);

    RETURN TRUE;
EXCEPTION
    WHEN OTHERS THEN
        RETURN FALSE;
END;
$function$
;

CREATE OR REPLACE FUNCTION public.rollback_event_evolution_version(p_original_event_id character varying, p_target_version integer)
 RETURNS boolean
 LANGUAGE plpgsql
AS $function$
BEGIN
    -- 将当前版本标记为非当前版本
    UPDATE event_evolution_history 
    SET is_current_version = FALSE 
    WHERE original_event_id = p_original_event_id 
      AND is_current_version = TRUE;
    
    -- 将目标版本标记为当前版本
    UPDATE event_evolution_history 
    SET is_current_version = TRUE 
    WHERE original_event_id = p_original_event_id 
      AND version = p_target_version;
    
    RETURN TRUE;
END;
$function$
;

CREATE OR REPLACE FUNCTION public.search_characters_simple(p_worldview_id character varying, p_keyword character varying DEFAULT NULL::character varying, p_role_type character varying DEFAULT NULL::character varying, p_limit integer DEFAULT 50)
 RETURNS jsonb
 LANGUAGE plpgsql
AS $function$
DECLARE
    result JSONB;
    where_clause TEXT := 'WHERE worldview_id = $1 AND status = ''active''';
    query_params TEXT[] := ARRAY[p_worldview_id];
    param_count INTEGER := 1;
BEGIN
    -- 构建动态WHERE子句
    IF p_keyword IS NOT NULL THEN
        param_count := param_count + 1;
        where_clause := where_clause || ' AND (name ILIKE $' || param_count || ' OR background ILIKE $' || param_count || ')';
        query_params := array_append(query_params, '%' || p_keyword || '%');
    END IF;
    
    IF p_role_type IS NOT NULL THEN
        param_count := param_count + 1;
        where_clause := where_clause || ' AND role_type = $' || param_count;
        query_params := array_append(query_params, p_role_type);
    END IF;
    
    -- 执行查询
    EXECUTE 'SELECT jsonb_agg(
        jsonb_build_object(
            ''character_id'', character_id,
            ''name'', name,
            ''age'', age,
            ''gender'', gender,
            ''role_type'', role_type,
            ''cultivation_level'', cultivation_level,
            ''element_type'', element_type,
            ''background'', background,
            ''personality_traits'', personality_traits,
            ''goals'', goals,
            ''relationships'', relationships,
            ''techniques'', techniques,
            ''artifacts'', artifacts,
            ''resources'', resources,
            ''stats'', stats,
            ''metadata'', metadata,
            ''created_at'', created_at
        )
    ) FROM characters ' || where_clause || ' LIMIT ' || p_limit
    USING query_params
    INTO result;
    
    RETURN COALESCE(result, '[]'::jsonb);
END;
$function$
;

CREATE OR REPLACE FUNCTION public.search_events(p_plot_id character varying, p_search_term text)
 RETURNS TABLE(id character varying, plot_outline_id character varying, chapter_number integer, sequence_order integer, title character varying, event_type character varying, description text, outcome text, created_at timestamp without time zone, updated_at timestamp without time zone, relevance_score real)
 LANGUAGE plpgsql
AS $function$
BEGIN
    RETURN QUERY
    SELECT 
        e.id, e.plot_outline_id, e.chapter_number, e.sequence_order,
        e.title, e.event_type, e.description, e.outcome,
        e.created_at, e.updated_at,
        (
            CASE 
                WHEN e.title ILIKE '%' || p_search_term || '%' THEN 3.0
                WHEN e.description ILIKE '%' || p_search_term || '%' THEN 2.0
                WHEN e.outcome ILIKE '%' || p_search_term || '%' THEN 1.0
                ELSE 0.0
            END
        ) as relevance_score
    FROM events e
    WHERE e.plot_outline_id = p_plot_id
    AND (
        e.title ILIKE '%' || p_search_term || '%' OR
        e.description ILIKE '%' || p_search_term || '%' OR
        e.outcome ILIKE '%' || p_search_term || '%'
    )
    ORDER BY relevance_score DESC, e.sequence_order, e.created_at;
END;
$function$
;

CREATE OR REPLACE FUNCTION public.search_simple_events_new(p_plot_id character varying, p_search_term text)
 RETURNS TABLE(id character varying, plot_outline_id character varying, chapter_number integer, sequence_order integer, title character varying, event_type character varying, description text, outcome text, created_at timestamp without time zone, updated_at timestamp without time zone, relevance_score real)
 LANGUAGE plpgsql
AS $function$
BEGIN
    RETURN QUERY
    SELECT 
        e.id, e.plot_outline_id, e.chapter_number, e.sequence_order,
        e.title, e.event_type, e.description, e.outcome,
        e.created_at, e.updated_at,
        (
            CASE 
                WHEN e.title ILIKE '%' || p_search_term || '%' THEN 3.0
                WHEN e.description ILIKE '%' || p_search_term || '%' THEN 2.0
                WHEN e.outcome ILIKE '%' || p_search_term || '%' THEN 1.0
                ELSE 0.0
            END
        ) as relevance_score
    FROM simple_events_table e
    WHERE e.plot_outline_id = p_plot_id
    AND (
        e.title ILIKE '%' || p_search_term || '%' OR
        e.description ILIKE '%' || p_search_term || '%' OR
        e.outcome ILIKE '%' || p_search_term || '%'
    )
    ORDER BY relevance_score DESC, e.sequence_order, e.created_at;
END;
$function$
;

CREATE OR REPLACE FUNCTION public.set_detailed_plot_current_version(p_detailed_plot_id character varying, p_version_record_id integer)
 RETURNS boolean
 LANGUAGE plpgsql
AS $function$
DECLARE
    version_exists BOOLEAN;
BEGIN
    -- 检查版本记录是否存在
    SELECT EXISTS(
        SELECT 1 FROM detailed_plot_versions 
        WHERE id = p_version_record_id 
          AND detailed_plot_id = p_detailed_plot_id
    ) INTO version_exists;
    
    IF NOT version_exists THEN
        RETURN FALSE;
    END IF;
    
    -- 先将该详细剧情的所有版本设为非当前版本
    UPDATE detailed_plot_versions 
    SET is_current_version = FALSE, updated_at = CURRENT_TIMESTAMP
    WHERE detailed_plot_id = p_detailed_plot_id;
    
    -- 设置指定版本为当前版本
    UPDATE detailed_plot_versions 
    SET is_current_version = TRUE, updated_at = CURRENT_TIMESTAMP
    WHERE id = p_version_record_id;
    
    RETURN TRUE;
END;
$function$
;

CREATE OR REPLACE FUNCTION public.sync_chapter_outline_fields()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
BEGIN
    -- 当剧情大纲更新时，同步更新相关章节大纲的字段
    UPDATE chapter_outlines 
    SET 
        story_tone = NEW.story_tone,
        narrative_structure = NEW.narrative_structure,
        story_structure = NEW.story_structure,
        updated_at = CURRENT_TIMESTAMP
    WHERE plot_outline_id = NEW.id;
    
    RETURN NEW;
END;
$function$
;

CREATE OR REPLACE FUNCTION public.sync_chapter_outline_fields_from_plot()
 RETURNS integer
 LANGUAGE plpgsql
AS $function$
DECLARE
    updated_count INTEGER := 0;
    plot_record RECORD;
    chapter_record RECORD;
BEGIN
    -- 遍历所有剧情大纲
    FOR plot_record IN 
        SELECT id, story_tone, narrative_structure, story_structure 
        FROM plot_outlines 
        WHERE story_tone IS NOT NULL 
        AND narrative_structure IS NOT NULL 
        AND story_structure IS NOT NULL
    LOOP
        -- 更新该剧情大纲下的所有章节大纲
        UPDATE chapter_outlines 
        SET 
            story_tone = plot_record.story_tone,
            narrative_structure = plot_record.narrative_structure,
            story_structure = plot_record.story_structure,
            updated_at = CURRENT_TIMESTAMP
        WHERE plot_outline_id = plot_record.id
        AND (
            story_tone IS NULL 
            OR narrative_structure IS NULL 
            OR story_structure IS NULL
            OR story_tone != plot_record.story_tone
            OR narrative_structure != plot_record.narrative_structure
            OR story_structure != plot_record.story_structure
        );
        
        GET DIAGNOSTICS updated_count = ROW_COUNT;
        
        RAISE NOTICE '剧情大纲 % 同步了 % 个章节大纲', plot_record.id, updated_count;
    END LOOP;
    
    RETURN updated_count;
END;
$function$
;

CREATE OR REPLACE FUNCTION public.update_chapter_outline_updated_at()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$function$
;

CREATE OR REPLACE FUNCTION public.update_chapter_outline_v2_updated_at()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$function$
;

CREATE OR REPLACE FUNCTION public.update_event(p_id character varying, p_title character varying DEFAULT NULL::character varying, p_event_type character varying DEFAULT NULL::character varying, p_description text DEFAULT NULL::text, p_outcome text DEFAULT NULL::text, p_chapter_number integer DEFAULT NULL::integer, p_sequence_order integer DEFAULT NULL::integer)
 RETURNS boolean
 LANGUAGE plpgsql
AS $function$
DECLARE
    update_fields TEXT[] := ARRAY[]::TEXT[];
    update_values TEXT[] := ARRAY[]::TEXT[];
    sql_query TEXT;
BEGIN
    -- 构建动态更新字段
    IF p_title IS NOT NULL THEN
        update_fields := array_append(update_fields, 'title = $' || (array_length(update_values, 1) + 2)::TEXT);
        update_values := array_append(update_values, p_title);
    END IF;
    
    IF p_event_type IS NOT NULL THEN
        update_fields := array_append(update_fields, 'event_type = $' || (array_length(update_values, 1) + 2)::TEXT);
        update_values := array_append(update_values, p_event_type);
    END IF;
    
    IF p_description IS NOT NULL THEN
        update_fields := array_append(update_fields, 'description = $' || (array_length(update_values, 1) + 2)::TEXT);
        update_values := array_append(update_values, p_description);
    END IF;
    
    IF p_outcome IS NOT NULL THEN
        update_fields := array_append(update_fields, 'outcome = $' || (array_length(update_values, 1) + 2)::TEXT);
        update_values := array_append(update_values, p_outcome);
    END IF;
    
    IF p_chapter_number IS NOT NULL THEN
        update_fields := array_append(update_fields, 'chapter_number = $' || (array_length(update_values, 1) + 2)::TEXT);
        update_values := array_append(update_values, p_chapter_number::TEXT);
    END IF;
    
    IF p_sequence_order IS NOT NULL THEN
        update_fields := array_append(update_fields, 'sequence_order = $' || (array_length(update_values, 1) + 2)::TEXT);
        update_values := array_append(update_values, p_sequence_order::TEXT);
    END IF;
    
    -- 如果没有要更新的字段，返回false
    IF array_length(update_fields, 1) IS NULL THEN
        RETURN FALSE;
    END IF;
    
    -- 添加updated_at字段
    update_fields := array_append(update_fields, 'updated_at = CURRENT_TIMESTAMP');
    
    -- 构建SQL查询
    sql_query := 'UPDATE events SET ' || array_to_string(update_fields, ', ') || ' WHERE id = $1';
    
    -- 执行更新
    EXECUTE sql_query USING p_id, update_values[1], update_values[2], update_values[3], update_values[4], update_values[5], update_values[6];
    
    RETURN TRUE;
EXCEPTION
    WHEN OTHERS THEN
        RETURN FALSE;
END;
$function$
;

CREATE OR REPLACE FUNCTION public.update_events_updated_at()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$function$
;

CREATE OR REPLACE FUNCTION public.update_locations_updated_at()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$function$
;

CREATE OR REPLACE FUNCTION public.update_plot_outline_updated_at()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$function$
;

CREATE OR REPLACE FUNCTION public.update_plot_outline_v2_updated_at()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$function$
;

CREATE OR REPLACE FUNCTION public.update_power_systems_updated_at()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$function$
;

CREATE OR REPLACE FUNCTION public.update_regions_updated_at()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$function$
;

CREATE OR REPLACE FUNCTION public.update_simple_event_new(p_id character varying, p_title character varying DEFAULT NULL::character varying, p_event_type character varying DEFAULT NULL::character varying, p_description text DEFAULT NULL::text, p_outcome text DEFAULT NULL::text, p_chapter_number integer DEFAULT NULL::integer, p_sequence_order integer DEFAULT NULL::integer)
 RETURNS boolean
 LANGUAGE plpgsql
AS $function$
DECLARE
    update_fields TEXT[] := ARRAY[]::TEXT[];
    update_values TEXT[] := ARRAY[]::TEXT[];
    sql_query TEXT;
BEGIN
    -- 构建动态更新字段
    IF p_title IS NOT NULL THEN
        update_fields := array_append(update_fields, 'title = $' || (array_length(update_values, 1) + 2)::TEXT);
        update_values := array_append(update_values, p_title);
    END IF;
    
    IF p_event_type IS NOT NULL THEN
        update_fields := array_append(update_fields, 'event_type = $' || (array_length(update_values, 1) + 2)::TEXT);
        update_values := array_append(update_values, p_event_type);
    END IF;
    
    IF p_description IS NOT NULL THEN
        update_fields := array_append(update_fields, 'description = $' || (array_length(update_values, 1) + 2)::TEXT);
        update_values := array_append(update_values, p_description);
    END IF;
    
    IF p_outcome IS NOT NULL THEN
        update_fields := array_append(update_fields, 'outcome = $' || (array_length(update_values, 1) + 2)::TEXT);
        update_values := array_append(update_values, p_outcome);
    END IF;
    
    IF p_chapter_number IS NOT NULL THEN
        update_fields := array_append(update_fields, 'chapter_number = $' || (array_length(update_values, 1) + 2)::TEXT);
        update_values := array_append(update_values, p_chapter_number::TEXT);
    END IF;
    
    IF p_sequence_order IS NOT NULL THEN
        update_fields := array_append(update_fields, 'sequence_order = $' || (array_length(update_values, 1) + 2)::TEXT);
        update_values := array_append(update_values, p_sequence_order::TEXT);
    END IF;
    
    -- 如果没有要更新的字段，返回false
    IF array_length(update_fields, 1) IS NULL THEN
        RETURN FALSE;
    END IF;
    
    -- 添加updated_at字段
    update_fields := array_append(update_fields, 'updated_at = CURRENT_TIMESTAMP');
    
    -- 构建SQL查询
    sql_query := 'UPDATE simple_events_table SET ' || array_to_string(update_fields, ', ') || ' WHERE id = $1';
    
    -- 执行更新
    EXECUTE sql_query USING p_id, update_values[1], update_values[2], update_values[3], update_values[4], update_values[5], update_values[6];
    
    RETURN TRUE;
EXCEPTION
    WHEN OTHERS THEN
        RETURN FALSE;
END;
$function$
;

CREATE OR REPLACE FUNCTION public.update_simple_events_updated_at()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$function$
;

CREATE OR REPLACE FUNCTION public.update_updated_at_column()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$function$
;

CREATE OR REPLACE FUNCTION public.update_version_number()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
BEGIN
    -- 如果是新插入的记录，自动设置版本号
    IF TG_OP = 'INSERT' THEN
        SELECT COALESCE(MAX(version_number), 0) + 1
        INTO NEW.version_number
        FROM detailed_plot_versions
        WHERE detailed_plot_id = NEW.detailed_plot_id
          AND version_type = NEW.version_type;
    END IF;
    
    RETURN NEW;
END;
$function$
;

CREATE OR REPLACE FUNCTION public.update_worldview_complete(p_worldview_id character varying, p_name character varying DEFAULT NULL::character varying, p_description text DEFAULT NULL::text, p_core_concept text DEFAULT NULL::text, p_cultivation_realms jsonb DEFAULT NULL::jsonb, p_energy_types jsonb DEFAULT NULL::jsonb, p_technique_categories jsonb DEFAULT NULL::jsonb, p_regions jsonb DEFAULT NULL::jsonb, p_main_regions jsonb DEFAULT NULL::jsonb, p_special_locations jsonb DEFAULT NULL::jsonb, p_organizations jsonb DEFAULT NULL::jsonb, p_social_hierarchy jsonb DEFAULT NULL::jsonb, p_historical_events jsonb DEFAULT NULL::jsonb, p_cultural_features jsonb DEFAULT NULL::jsonb, p_current_conflicts jsonb DEFAULT NULL::jsonb)
 RETURNS boolean
 LANGUAGE plpgsql
AS $function$
BEGIN
    -- 更新世界观基本信息
    UPDATE worldviews 
    SET 
        name = COALESCE(p_name, worldviews.name),
        description = COALESCE(p_description, worldviews.description),
        core_concept = COALESCE(p_core_concept, worldviews.core_concept),
        updated_at = CURRENT_TIMESTAMP
    WHERE worldview_id = p_worldview_id;

    -- 更新或插入力量体系
    INSERT INTO power_systems (worldview_id, cultivation_realms, energy_types, technique_categories)
    VALUES (p_worldview_id, p_cultivation_realms, p_energy_types, p_technique_categories)
    ON CONFLICT (worldview_id) DO UPDATE SET
        cultivation_realms = COALESCE(p_cultivation_realms, power_systems.cultivation_realms),
        energy_types = COALESCE(p_energy_types, power_systems.energy_types),
        technique_categories = COALESCE(p_technique_categories, power_systems.technique_categories),
        updated_at = CURRENT_TIMESTAMP;

    -- 更新或插入地理设定
    INSERT INTO geographies (worldview_id, regions, main_regions, special_locations)
    VALUES (p_worldview_id, p_regions, p_main_regions, p_special_locations)
    ON CONFLICT (worldview_id) DO UPDATE SET
        regions = COALESCE(p_regions, geographies.regions),
        main_regions = COALESCE(p_main_regions, geographies.main_regions),
        special_locations = COALESCE(p_special_locations, geographies.special_locations),
        updated_at = CURRENT_TIMESTAMP;

    -- 更新或插入社会结构
    INSERT INTO societies (worldview_id, organizations, social_hierarchy)
    VALUES (p_worldview_id, p_organizations, p_social_hierarchy)
    ON CONFLICT (worldview_id) DO UPDATE SET
        organizations = COALESCE(p_organizations, societies.organizations),
        social_hierarchy = COALESCE(p_social_hierarchy, societies.social_hierarchy),
        updated_at = CURRENT_TIMESTAMP;

    -- 更新或插入历史文化
    INSERT INTO history_cultures (worldview_id, historical_events, cultural_features, current_conflicts)
    VALUES (p_worldview_id, p_historical_events, p_cultural_features, p_current_conflicts)
    ON CONFLICT (worldview_id) DO UPDATE SET
        historical_events = COALESCE(p_historical_events, history_cultures.historical_events),
        cultural_features = COALESCE(p_cultural_features, history_cultures.cultural_features),
        current_conflicts = COALESCE(p_current_conflicts, history_cultures.current_conflicts),
        updated_at = CURRENT_TIMESTAMP;

    RETURN TRUE;
EXCEPTION
    WHEN OTHERS THEN
        RETURN FALSE;
END;
$function$
;

CREATE OR REPLACE FUNCTION public.update_worldview_complete(p_worldview_id character varying, p_name character varying, p_description text, p_core_concept text, p_cultivation_realms jsonb DEFAULT NULL::jsonb, p_energy_types jsonb DEFAULT NULL::jsonb, p_technique_categories jsonb DEFAULT NULL::jsonb, p_main_regions jsonb DEFAULT NULL::jsonb, p_special_locations jsonb DEFAULT NULL::jsonb, p_organizations jsonb DEFAULT NULL::jsonb, p_social_hierarchy jsonb DEFAULT NULL::jsonb, p_cultural_norms jsonb DEFAULT NULL::jsonb, p_events jsonb DEFAULT NULL::jsonb, p_timeline jsonb DEFAULT NULL::jsonb)
 RETURNS boolean
 LANGUAGE plpgsql
AS $function$
BEGIN
    -- 更新世界观主表
    UPDATE worldviews 
    SET name = p_name, description = p_description, core_concept = p_core_concept
    WHERE worldview_id = p_worldview_id;
    
    -- 更新或插入力量体系
    IF p_cultivation_realms IS NOT NULL OR p_energy_types IS NOT NULL OR p_technique_categories IS NOT NULL THEN
        INSERT INTO power_systems (worldview_id, cultivation_realms, energy_types, technique_categories)
        VALUES (p_worldview_id, p_cultivation_realms, p_energy_types, p_technique_categories)
        ON CONFLICT (worldview_id) 
        DO UPDATE SET 
            cultivation_realms = EXCLUDED.cultivation_realms,
            energy_types = EXCLUDED.energy_types,
            technique_categories = EXCLUDED.technique_categories;
    END IF;
    
    -- 更新或插入地理设定
    IF p_main_regions IS NOT NULL OR p_special_locations IS NOT NULL THEN
        INSERT INTO geographies (worldview_id, main_regions, special_locations)
        VALUES (p_worldview_id, p_main_regions, p_special_locations)
        ON CONFLICT (worldview_id) 
        DO UPDATE SET 
            main_regions = EXCLUDED.main_regions,
            special_locations = EXCLUDED.special_locations;
    END IF;
    
    -- 更新或插入社会组织
    IF p_organizations IS NOT NULL OR p_social_hierarchy IS NOT NULL OR p_cultural_norms IS NOT NULL THEN
        INSERT INTO societies (worldview_id, organizations, social_hierarchy, cultural_norms)
        VALUES (p_worldview_id, p_organizations, p_social_hierarchy, p_cultural_norms)
        ON CONFLICT (worldview_id) 
        DO UPDATE SET 
            organizations = EXCLUDED.organizations,
            social_hierarchy = EXCLUDED.social_hierarchy,
            cultural_norms = EXCLUDED.cultural_norms;
    END IF;
    
    -- 更新或插入历史事件
    IF p_events IS NOT NULL OR p_timeline IS NOT NULL THEN
        INSERT INTO historical_events (worldview_id, events, timeline)
        VALUES (p_worldview_id, p_events, p_timeline)
        ON CONFLICT (worldview_id) 
        DO UPDATE SET 
            events = EXCLUDED.events,
            timeline = EXCLUDED.timeline;
    END IF;
    
    RETURN TRUE;
END;
$function$
;

CREATE OR REPLACE FUNCTION public.validate_chapter_outline_sync()
 RETURNS TABLE(plot_id character varying, plot_title character varying, total_chapters integer, synced_chapters integer, unsynced_chapters integer, sync_status text)
 LANGUAGE plpgsql
AS $function$
BEGIN
    RETURN QUERY
    SELECT 
        po.id as plot_id,
        po.title as plot_title,
        COUNT(co.id)::INTEGER as total_chapters,
        COUNT(CASE 
            WHEN co.story_tone = po.story_tone 
            AND co.narrative_structure = po.narrative_structure 
            AND co.story_structure = po.story_structure 
            THEN 1 
        END)::INTEGER as synced_chapters,
        COUNT(CASE 
            WHEN co.story_tone != po.story_tone 
            OR co.narrative_structure != po.narrative_structure 
            OR co.story_structure != po.story_structure 
            THEN 1 
        END)::INTEGER as unsynced_chapters,
        CASE 
            WHEN COUNT(co.id) = 0 THEN '无章节大纲'
            WHEN COUNT(CASE 
                WHEN co.story_tone != po.story_tone 
                OR co.narrative_structure != po.narrative_structure 
                OR co.story_structure != po.story_structure 
                THEN 1 
            END) = 0 THEN '完全同步'
            ELSE '部分同步'
        END as sync_status
    FROM plot_outlines po
    LEFT JOIN chapter_outlines co ON po.id = co.plot_outline_id
    GROUP BY po.id, po.title, po.story_tone, po.narrative_structure, po.story_structure
    ORDER BY po.title;
END;
$function$
;


-- ============================================
-- 第三部分：表结构
-- ============================================

-- 表: acts
CREATE TABLE IF NOT EXISTS acts (
    id character varying(50) NOT NULL,
    plot_outline_id character varying(50) NOT NULL,
    act_number integer NOT NULL,
    act_name character varying(100) NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    core_mission text NOT NULL,
    daily_events text NOT NULL,
    conflict_events text NOT NULL,
    special_events text NOT NULL,
    major_events text NOT NULL,
    stage_result text NOT NULL,
    PRIMARY KEY (id),
    UNIQUE (plot_outline_id, act_number)
);

-- 表: acts_backup
CREATE TABLE IF NOT EXISTS acts_backup (
    id character varying(50),
    plot_outline_id character varying(50),
    act_number integer,
    act_name character varying(100),
    start_position numeric(3,2),
    end_position numeric(3,2),
    purpose text,
    key_events jsonb,
    emotional_tone character varying(50),
    created_at timestamp without time zone
);

-- 表: chapter_outlines
CREATE TABLE IF NOT EXISTS chapter_outlines (
    id character varying(50) NOT NULL,
    plot_outline_id character varying(50) NOT NULL,
    chapter_number integer NOT NULL,
    title character varying(200) NOT NULL,
    act_belonging character varying(50),
    chapter_summary text NOT NULL,
    status character varying(20) DEFAULT '大纲'::character varying,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    story_tone character varying(50),
    narrative_structure character varying(50),
    story_structure character varying(50),
    worldview_elements jsonb DEFAULT '[]'::jsonb,
    core_event character varying(50),
    PRIMARY KEY (id),
    UNIQUE (plot_outline_id, chapter_number)
);

-- 表: chapter_templates
CREATE TABLE IF NOT EXISTS chapter_templates (
    template_id character varying(50) NOT NULL,
    template_name character varying(100) NOT NULL,
    plot_function character varying(50) NOT NULL,
    structure jsonb DEFAULT '[]'::jsonb,
    scene_types jsonb DEFAULT '[]'::jsonb,
    emotional_tone character varying(50) NOT NULL,
    writing_tips jsonb DEFAULT '[]'::jsonb,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (template_id)
);

-- 表: character_dialogues
CREATE TABLE IF NOT EXISTS character_dialogues (
    id integer NOT NULL DEFAULT nextval('character_dialogues_id_seq'::regclass),
    dialogue_id character varying(255) NOT NULL,
    character_id character varying(255) NOT NULL,
    situation text NOT NULL,
    dialogue_content text NOT NULL,
    dialogue_type character varying(50),
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    created_by character varying(255),
    PRIMARY KEY (id),
    UNIQUE (dialogue_id)
);

ALTER TABLE character_dialogues ADD CONSTRAINT character_dialogues_character_id_fkey FOREIGN KEY (character_id) REFERENCES characters(character_id);

-- 表: character_groups
CREATE TABLE IF NOT EXISTS character_groups (
    id integer NOT NULL DEFAULT nextval('character_groups_id_seq'::regclass),
    group_id character varying(255) NOT NULL,
    worldview_id character varying(255) NOT NULL,
    name character varying(255) NOT NULL,
    description text,
    group_type character varying(100),
    members jsonb DEFAULT '[]'::jsonb,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    created_by character varying(255),
    status character varying(50) DEFAULT 'active'::character varying,
    PRIMARY KEY (id),
    UNIQUE (group_id)
);

ALTER TABLE character_groups ADD CONSTRAINT character_groups_worldview_id_fkey FOREIGN KEY (worldview_id) REFERENCES worldviews(worldview_id);

-- 表: characters
CREATE TABLE IF NOT EXISTS characters (
    id integer NOT NULL DEFAULT nextval('characters_id_seq'::regclass),
    character_id character varying(255) NOT NULL,
    worldview_id character varying(255) NOT NULL,
    name character varying(255) NOT NULL,
    age integer,
    gender character varying(50),
    role_type character varying(50) NOT NULL,
    cultivation_level character varying(255),
    element_type character varying(255),
    background text,
    current_location character varying(255),
    organization_id character varying(255),
    techniques jsonb DEFAULT '[]'::jsonb,
    metadata jsonb DEFAULT '{}'::jsonb,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    created_by character varying(255),
    status character varying(50) DEFAULT 'active'::character varying,
    main_goals text,
    short_term_goals text,
    weaknesses text,
    personality_traits text,
    appearance text,
    turning_point text,
    relationship_text text,
    values text,
    PRIMARY KEY (id),
    UNIQUE (character_id)
);

ALTER TABLE characters ADD CONSTRAINT characters_worldview_id_fkey FOREIGN KEY (worldview_id) REFERENCES worldviews(worldview_id);

-- 表: correction_history
CREATE TABLE IF NOT EXISTS correction_history (
    id character varying(100) NOT NULL,
    detailed_plot_id character varying(100) NOT NULL,
    original_content text NOT NULL,
    corrected_content text NOT NULL,
    logic_check_result jsonb,
    corrections_made jsonb,
    correction_summary text,
    word_count_change integer DEFAULT 0,
    quality_improvement text,
    correction_notes text,
    corrected_by character varying(100) NOT NULL DEFAULT 'system'::character varying,
    corrected_at timestamp without time zone NOT NULL DEFAULT now(),
    created_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone DEFAULT now(),
    PRIMARY KEY (id)
);

-- 表: detailed_plot_versions
CREATE TABLE IF NOT EXISTS detailed_plot_versions (
    id integer NOT NULL DEFAULT nextval('detailed_plot_versions_id_seq'::regclass),
    detailed_plot_id character varying(255) NOT NULL,
    version_type character varying(50) NOT NULL,
    version_number integer NOT NULL DEFAULT 1,
    is_current_version boolean DEFAULT false,
    title character varying(500) NOT NULL,
    content text NOT NULL,
    word_count integer DEFAULT 0,
    source_table character varying(50),
    source_record_id character varying(255),
    version_notes text,
    created_by character varying(50) DEFAULT 'system'::character varying,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
);

ALTER TABLE detailed_plot_versions ADD CONSTRAINT fk_detailed_plot_versions_detailed_plot_id FOREIGN KEY (detailed_plot_id) REFERENCES detailed_plots(id);

-- 表: detailed_plots
CREATE TABLE IF NOT EXISTS detailed_plots (
    id character varying(255) NOT NULL,
    chapter_outline_id character varying(255) NOT NULL,
    plot_outline_id character varying(255) NOT NULL,
    title character varying(500) NOT NULL,
    content text NOT NULL,
    word_count integer DEFAULT 0,
    status character varying(50) DEFAULT '草稿'::character varying,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    logic_status character varying(50),
    logic_check_result jsonb,
    scoring_status character varying(50) DEFAULT '未评分'::character varying,
    total_score numeric(5,2),
    scoring_result jsonb,
    scoring_feedback text,
    scored_at timestamp without time zone,
    scored_by character varying(100),
    PRIMARY KEY (id)
);

ALTER TABLE detailed_plots ADD CONSTRAINT detailed_plots_chapter_outline_id_fkey FOREIGN KEY (chapter_outline_id) REFERENCES chapter_outlines(id);
ALTER TABLE detailed_plots ADD CONSTRAINT detailed_plots_plot_outline_id_fkey FOREIGN KEY (plot_outline_id) REFERENCES plot_outlines(id);

-- 表: dimension_mappings
CREATE TABLE IF NOT EXISTS dimension_mappings (
    id character varying(100) NOT NULL,
    technical_name character varying(50) NOT NULL,
    display_name character varying(100) NOT NULL,
    description text,
    color_code character varying(7),
    weight numeric(3,2) DEFAULT 1.0,
    is_active boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone DEFAULT now(),
    PRIMARY KEY (id),
    UNIQUE (technical_name)
);

-- 表: event_evolution_history
CREATE TABLE IF NOT EXISTS event_evolution_history (
    id character varying(50) NOT NULL DEFAULT ('evo_'::text || substr(md5((random())::text), 1, 8)),
    original_event_id character varying(50) NOT NULL,
    version integer NOT NULL DEFAULT 1,
    is_current_version boolean DEFAULT true,
    title character varying(200) NOT NULL,
    event_type character varying(50) NOT NULL,
    description text,
    outcome text,
    plot_outline_id character varying(50),
    chapter_number integer,
    sequence_order integer,
    evolution_reason text,
    score_id integer,
    parent_version_id character varying(50),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
);

ALTER TABLE event_evolution_history ADD CONSTRAINT fk_original_event FOREIGN KEY (original_event_id) REFERENCES events(id);
ALTER TABLE event_evolution_history ADD CONSTRAINT fk_parent_version FOREIGN KEY (parent_version_id) REFERENCES event_evolution_history(id);

-- 表: event_scores
CREATE TABLE IF NOT EXISTS event_scores (
    id integer NOT NULL DEFAULT nextval('event_scores_id_seq'::regclass),
    event_id character varying(50) NOT NULL,
    protagonist_involvement numeric(3,1) NOT NULL DEFAULT 0.0,
    plot_coherence numeric(3,1) NOT NULL DEFAULT 0.0,
    character_development numeric(3,1) NOT NULL DEFAULT 0.0,
    world_consistency numeric(3,1) NOT NULL DEFAULT 0.0,
    dramatic_tension numeric(3,1) NOT NULL DEFAULT 0.0,
    emotional_impact numeric(3,1) NOT NULL DEFAULT 0.0,
    foreshadowing numeric(3,1) NOT NULL DEFAULT 0.0,
    overall_quality numeric(3,1) NOT NULL DEFAULT 0.0,
    feedback text,
    strengths text[],
    weaknesses text[],
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
);

-- 表: events
CREATE TABLE IF NOT EXISTS events (
    id character varying(50) NOT NULL,
    plot_outline_id character varying(50) NOT NULL,
    chapter_number integer,
    sequence_order integer DEFAULT 0,
    title character varying(200) NOT NULL,
    event_type character varying(50) NOT NULL,
    description text NOT NULL,
    outcome text NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    version integer NOT NULL DEFAULT 1,
    is_current_version boolean NOT NULL DEFAULT true,
    PRIMARY KEY (id),
    UNIQUE (id, version)
);

ALTER TABLE events ADD CONSTRAINT fk_events_plot_outline FOREIGN KEY (plot_outline_id) REFERENCES plot_outlines(id);

-- 表: evolution_history
CREATE TABLE IF NOT EXISTS evolution_history (
    id character varying(50) NOT NULL,
    detailed_plot_id character varying(50) NOT NULL,
    evolution_type character varying(50) NOT NULL DEFAULT 'general'::character varying,
    original_content text NOT NULL,
    evolved_content text NOT NULL,
    improvements jsonb,
    evolution_summary text,
    word_count_change integer DEFAULT 0,
    quality_score numeric(5,2) DEFAULT 0.0,
    evolution_notes text,
    evolved_by character varying(50) NOT NULL DEFAULT 'system'::character varying,
    evolved_at timestamp without time zone NOT NULL DEFAULT now(),
    created_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone DEFAULT now(),
    PRIMARY KEY (id)
);

-- 表: geographies
CREATE TABLE IF NOT EXISTS geographies (
    id integer NOT NULL DEFAULT nextval('geographies_id_seq'::regclass),
    worldview_id character varying(255) NOT NULL,
    main_regions jsonb,
    special_locations jsonb,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    regions jsonb,
    PRIMARY KEY (id),
    UNIQUE (worldview_id)
);

ALTER TABLE geographies ADD CONSTRAINT geographies_worldview_id_fkey FOREIGN KEY (worldview_id) REFERENCES worldviews(worldview_id);

-- 表: historical_events
CREATE TABLE IF NOT EXISTS historical_events (
    id integer NOT NULL DEFAULT nextval('historical_events_id_seq'::regclass),
    worldview_id character varying(255) NOT NULL,
    events jsonb,
    timeline jsonb,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE (worldview_id)
);

ALTER TABLE historical_events ADD CONSTRAINT historical_events_worldview_id_fkey FOREIGN KEY (worldview_id) REFERENCES worldviews(worldview_id);

-- 表: history_cultures
CREATE TABLE IF NOT EXISTS history_cultures (
    id integer NOT NULL DEFAULT nextval('history_cultures_id_seq'::regclass),
    worldview_id character varying(255) NOT NULL,
    historical_events jsonb,
    cultural_features jsonb,
    current_conflicts jsonb,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE (worldview_id)
);

-- 表: locations
CREATE TABLE IF NOT EXISTS locations (
    id character varying(36) NOT NULL,
    worldview_id character varying(36) NOT NULL,
    name character varying(100) NOT NULL,
    type character varying(50) NOT NULL,
    description text NOT NULL,
    x numeric(5,2) NOT NULL,
    y numeric(5,2) NOT NULL,
    size integer NOT NULL,
    importance character varying(20) NOT NULL,
    features jsonb DEFAULT '[]'::jsonb,
    connections jsonb DEFAULT '[]'::jsonb,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    metadata jsonb DEFAULT '{}'::jsonb,
    PRIMARY KEY (id)
);

-- 表: logic_check_history
CREATE TABLE IF NOT EXISTS logic_check_history (
    id character varying(50) NOT NULL,
    detailed_plot_id character varying(50) NOT NULL,
    check_type character varying(20) NOT NULL DEFAULT 'manual'::character varying,
    logic_score numeric(5,2) NOT NULL,
    overall_status character varying(50) NOT NULL,
    issues_count integer DEFAULT 0,
    checked_by character varying(100) NOT NULL DEFAULT 'system'::character varying,
    checked_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    result jsonb,
    PRIMARY KEY (id)
);

ALTER TABLE logic_check_history ADD CONSTRAINT logic_check_history_detailed_plot_id_fkey FOREIGN KEY (detailed_plot_id) REFERENCES detailed_plots(id);

-- 表: plot_outlines
CREATE TABLE IF NOT EXISTS plot_outlines (
    id character varying(50) NOT NULL,
    title character varying(200) NOT NULL,
    worldview_id character varying(50) NOT NULL,
    story_tone character varying(50) NOT NULL,
    narrative_structure character varying(50) NOT NULL,
    target_word_count integer DEFAULT 100000,
    estimated_chapters integer DEFAULT 20,
    status character varying(20) DEFAULT '草稿'::character varying,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    created_by character varying(50),
    story_summary text NOT NULL,
    core_conflict text NOT NULL,
    theme text NOT NULL,
    protagonist_name character varying(255) NOT NULL,
    protagonist_background text NOT NULL,
    protagonist_personality text NOT NULL,
    protagonist_goals text NOT NULL,
    core_concept text NOT NULL,
    world_description text NOT NULL,
    geography_setting text NOT NULL,
    story_structure character varying(50) DEFAULT '5幕式'::character varying,
    PRIMARY KEY (id)
);

-- 表: plot_outlines_backup
CREATE TABLE IF NOT EXISTS plot_outlines_backup (
    id character varying(50),
    title character varying(200),
    description text,
    worldview_id character varying(50),
    story_tone character varying(50),
    narrative_structure character varying(50),
    story_structure character varying(50),
    target_word_count integer,
    estimated_chapters integer,
    story_framework jsonb,
    character_positions jsonb,
    plot_blocks jsonb,
    story_flow jsonb,
    status character varying(20),
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    created_by character varying(50)
);

-- 表: plot_points
CREATE TABLE IF NOT EXISTS plot_points (
    id character varying(50) NOT NULL,
    plot_outline_id character varying(50) NOT NULL,
    point_type character varying(50) NOT NULL,
    position numeric(3,2) NOT NULL,
    title character varying(200) NOT NULL,
    description text NOT NULL,
    emotional_impact character varying(50),
    character_involvement jsonb DEFAULT '[]'::jsonb,
    plot_function character varying(50),
    foreshadowing jsonb DEFAULT '[]'::jsonb,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
);

-- 表: power_systems
CREATE TABLE IF NOT EXISTS power_systems (
    worldview_id character varying(50) NOT NULL,
    cultivation_realms jsonb NOT NULL DEFAULT '[]'::jsonb,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (worldview_id)
);

ALTER TABLE power_systems ADD CONSTRAINT power_systems_worldview_id_fkey FOREIGN KEY (worldview_id) REFERENCES worldviews(worldview_id);

-- 表: power_systems_backup
CREATE TABLE IF NOT EXISTS power_systems_backup (
    id integer,
    worldview_id character varying(255),
    cultivation_realms jsonb,
    energy_types jsonb,
    technique_categories jsonb,
    created_at timestamp with time zone,
    updated_at timestamp with time zone
);

-- 表: regions
CREATE TABLE IF NOT EXISTS regions (
    id character varying(36) NOT NULL,
    worldview_id character varying(36) NOT NULL,
    name character varying(100) NOT NULL,
    terrain_type character varying(50) NOT NULL,
    description text NOT NULL,
    x numeric(5,2) NOT NULL,
    y numeric(5,2) NOT NULL,
    width numeric(5,2) NOT NULL,
    height numeric(5,2) NOT NULL,
    importance character varying(20) NOT NULL,
    features jsonb DEFAULT '[]'::jsonb,
    climate character varying(50),
    resources jsonb DEFAULT '[]'::jsonb,
    connections jsonb DEFAULT '[]'::jsonb,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    metadata jsonb DEFAULT '{}'::jsonb,
    boundary_points jsonb DEFAULT '[]'::jsonb,
    PRIMARY KEY (id)
);

-- 表: scenes
CREATE TABLE IF NOT EXISTS scenes (
    id character varying(50) NOT NULL,
    chapter_outline_id character varying(50) NOT NULL,
    scene_number integer NOT NULL,
    title character varying(200),
    description text NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    scene_title character varying(200),
    scene_description text,
    PRIMARY KEY (id),
    UNIQUE (chapter_outline_id, scene_number)
);

-- 表: scoring_dimensions
CREATE TABLE IF NOT EXISTS scoring_dimensions (
    id character varying(100) NOT NULL,
    scoring_record_id character varying(100) NOT NULL,
    dimension_name character varying(50) NOT NULL,
    dimension_display_name character varying(100) NOT NULL,
    score numeric(5,2) NOT NULL,
    feedback text,
    weight numeric(3,2) DEFAULT 1.0,
    created_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone DEFAULT now(),
    PRIMARY KEY (id),
    UNIQUE (scoring_record_id, dimension_name)
);

ALTER TABLE scoring_dimensions ADD CONSTRAINT scoring_dimensions_scoring_record_id_fkey FOREIGN KEY (scoring_record_id) REFERENCES scoring_records(id);

-- 表: scoring_history
CREATE TABLE IF NOT EXISTS scoring_history (
    id character varying(50) NOT NULL,
    detailed_plot_id character varying(50) NOT NULL,
    scoring_type character varying(20) NOT NULL DEFAULT 'intelligent'::character varying,
    total_score numeric(5,2) NOT NULL,
    dimension_scores jsonb NOT NULL,
    detailed_feedback jsonb NOT NULL,
    overall_feedback text NOT NULL,
    improvement_suggestions jsonb NOT NULL,
    scored_by character varying(100) NOT NULL DEFAULT 'system'::character varying,
    scored_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
);

ALTER TABLE scoring_history ADD CONSTRAINT scoring_history_detailed_plot_id_fkey FOREIGN KEY (detailed_plot_id) REFERENCES detailed_plots(id);

-- 表: scoring_records
CREATE TABLE IF NOT EXISTS scoring_records (
    id character varying(100) NOT NULL,
    detailed_plot_id character varying(100) NOT NULL,
    scorer_id character varying(100) NOT NULL DEFAULT 'system'::character varying,
    scoring_type character varying(50) NOT NULL DEFAULT 'intelligent'::character varying,
    total_score numeric(5,2) NOT NULL,
    scoring_level character varying(20) NOT NULL,
    overall_feedback text,
    improvement_suggestions text[],
    created_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone DEFAULT now(),
    PRIMARY KEY (id)
);

ALTER TABLE scoring_records ADD CONSTRAINT fk_scoring_detailed_plot FOREIGN KEY (detailed_plot_id) REFERENCES detailed_plots(id);

-- 表: simple_events_table
CREATE TABLE IF NOT EXISTS simple_events_table (
    id character varying(50) NOT NULL,
    plot_outline_id character varying(50) NOT NULL,
    chapter_number integer,
    sequence_order integer DEFAULT 0,
    title character varying(200) NOT NULL,
    event_type character varying(50) NOT NULL,
    description text NOT NULL,
    outcome text NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
);

ALTER TABLE simple_events_table ADD CONSTRAINT fk_simple_events_plot_outline FOREIGN KEY (plot_outline_id) REFERENCES plot_outlines(id);

-- 表: societies
CREATE TABLE IF NOT EXISTS societies (
    id integer NOT NULL DEFAULT nextval('societies_id_seq'::regclass),
    worldview_id character varying(255) NOT NULL,
    organizations jsonb,
    social_hierarchy jsonb,
    cultural_norms jsonb,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE (worldview_id)
);

ALTER TABLE societies ADD CONSTRAINT societies_worldview_id_fkey FOREIGN KEY (worldview_id) REFERENCES worldviews(worldview_id);

-- 表: story_arc_points
CREATE TABLE IF NOT EXISTS story_arc_points (
    id character varying(50) NOT NULL,
    plot_outline_id character varying(50) NOT NULL,
    arc_type character varying(50) NOT NULL,
    position numeric(3,2) NOT NULL,
    title character varying(200) NOT NULL,
    description text NOT NULL,
    emotional_state character varying(50) NOT NULL,
    character_growth text,
    plot_advancement text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
);

-- 表: worldview_metadata
CREATE TABLE IF NOT EXISTS worldview_metadata (
    id integer NOT NULL DEFAULT nextval('worldview_metadata_id_seq'::regclass),
    worldview_id character varying(255) NOT NULL,
    metadata_key character varying(255) NOT NULL,
    metadata_value jsonb,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE (worldview_id, metadata_key)
);

-- 表: worldviews
CREATE TABLE IF NOT EXISTS worldviews (
    id integer NOT NULL DEFAULT nextval('worldviews_id_seq'::regclass),
    worldview_id character varying(255) NOT NULL,
    name character varying(500) NOT NULL,
    description text,
    core_concept text NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    created_by character varying(255),
    version integer DEFAULT 1,
    status character varying(50) DEFAULT 'active'::character varying,
    PRIMARY KEY (id),
    UNIQUE (worldview_id)
);

-- ============================================
-- 第四部分：视图
-- ============================================

-- 视图: detailed_plots_with_latest_version
CREATE OR REPLACE VIEW detailed_plots_with_latest_version AS  SELECT dp.id AS original_id,
    dp.chapter_outline_id,
    dp.plot_outline_id,
    dp.status,
    dp.logic_status,
    dp.logic_check_result,
    dp.scoring_status,
    dp.total_score,
    dp.scoring_result,
    dp.scoring_feedback,
    dp.scored_at,
    dp.scored_by,
    dp.created_at AS original_created_at,
    dp.updated_at AS original_updated_at,
    dp.title AS original_title,
    dp.content AS original_content,
    dp.word_count AS original_word_count,
    dpv.id AS current_version_id,
    dpv.version_type AS current_version_type,
    dpv.version_number AS current_version_number,
    dpv.title AS current_title,
    dpv.content AS current_content,
    dpv.word_count AS current_word_count,
    dpv.source_table AS current_source_table,
    dpv.source_record_id AS current_source_record_id,
    dpv.version_notes AS current_version_notes,
    dpv.created_by AS current_created_by,
    dpv.created_at AS current_created_at,
    dpv.updated_at AS current_updated_at,
        CASE
            WHEN (dpv.id IS NOT NULL) THEN true
            ELSE false
        END AS has_version_record
   FROM (detailed_plots dp
     LEFT JOIN ( SELECT DISTINCT ON (detailed_plot_versions.detailed_plot_id) detailed_plot_versions.id,
            detailed_plot_versions.detailed_plot_id,
            detailed_plot_versions.version_type,
            detailed_plot_versions.version_number,
            detailed_plot_versions.is_current_version,
            detailed_plot_versions.title,
            detailed_plot_versions.content,
            detailed_plot_versions.word_count,
            detailed_plot_versions.source_table,
            detailed_plot_versions.source_record_id,
            detailed_plot_versions.version_notes,
            detailed_plot_versions.created_by,
            detailed_plot_versions.created_at,
            detailed_plot_versions.updated_at
           FROM detailed_plot_versions
          ORDER BY detailed_plot_versions.detailed_plot_id, detailed_plot_versions.updated_at DESC, detailed_plot_versions.created_at DESC) dpv ON (((dp.id)::text = (dpv.detailed_plot_id)::text)));;

-- 视图: event_scoring_statistics
CREATE OR REPLACE VIEW event_scoring_statistics AS None;

-- 视图: events_with_latest_evolution
CREATE OR REPLACE VIEW events_with_latest_evolution AS None;


-- ============================================
-- 第五部分：索引
-- ============================================

CREATE UNIQUE INDEX acts_plot_outline_id_act_number_key ON public.acts USING btree (plot_outline_id, act_number);

CREATE INDEX IF NOT EXISTS idx_acts_act_number ON public.acts USING btree (act_number);

CREATE INDEX IF NOT EXISTS idx_acts_plot_id ON public.acts USING btree (plot_outline_id);

CREATE INDEX IF NOT EXISTS idx_acts_plot_outline_id ON public.acts USING btree (plot_outline_id);

CREATE UNIQUE INDEX chapter_outlines_plot_outline_id_chapter_number_key ON public.chapter_outlines USING btree (plot_outline_id, chapter_number);

CREATE INDEX IF NOT EXISTS idx_chapter_outlines_core_event ON public.chapter_outlines USING btree (core_event);

CREATE INDEX IF NOT EXISTS idx_chapter_outlines_narrative_structure ON public.chapter_outlines USING btree (narrative_structure);

CREATE INDEX IF NOT EXISTS idx_chapter_outlines_number ON public.chapter_outlines USING btree (plot_outline_id, chapter_number);

CREATE INDEX IF NOT EXISTS idx_chapter_outlines_plot_id ON public.chapter_outlines USING btree (plot_outline_id);

CREATE INDEX IF NOT EXISTS idx_chapter_outlines_status ON public.chapter_outlines USING btree (status);

CREATE INDEX IF NOT EXISTS idx_chapter_outlines_story_structure ON public.chapter_outlines USING btree (story_structure);

CREATE INDEX IF NOT EXISTS idx_chapter_outlines_story_tone ON public.chapter_outlines USING btree (story_tone);

CREATE INDEX IF NOT EXISTS idx_chapter_outlines_worldview_elements ON public.chapter_outlines USING gin (worldview_elements);

CREATE INDEX IF NOT EXISTS idx_chapter_templates_function ON public.chapter_templates USING btree (plot_function);

CREATE UNIQUE INDEX character_dialogues_dialogue_id_key ON public.character_dialogues USING btree (dialogue_id);

CREATE INDEX IF NOT EXISTS idx_character_dialogues_character_id ON public.character_dialogues USING btree (character_id);

CREATE UNIQUE INDEX character_groups_group_id_key ON public.character_groups USING btree (group_id);

CREATE INDEX IF NOT EXISTS idx_character_groups_worldview_id ON public.character_groups USING btree (worldview_id);

CREATE UNIQUE INDEX characters_character_id_key ON public.characters USING btree (character_id);

CREATE INDEX IF NOT EXISTS idx_characters_name ON public.characters USING btree (name);

CREATE INDEX IF NOT EXISTS idx_characters_role_type ON public.characters USING btree (role_type);

CREATE INDEX IF NOT EXISTS idx_characters_worldview_id ON public.characters USING btree (worldview_id);

CREATE INDEX IF NOT EXISTS idx_correction_history_corrected_at ON public.correction_history USING btree (corrected_at);

CREATE INDEX IF NOT EXISTS idx_correction_history_corrected_by ON public.correction_history USING btree (corrected_by);

CREATE INDEX IF NOT EXISTS idx_correction_history_detailed_plot_fk ON public.correction_history USING btree (detailed_plot_id);

CREATE INDEX IF NOT EXISTS idx_correction_history_detailed_plot_id ON public.correction_history USING btree (detailed_plot_id);

CREATE INDEX IF NOT EXISTS idx_detailed_plot_versions_current ON public.detailed_plot_versions USING btree (detailed_plot_id, is_current_version);

CREATE INDEX IF NOT EXISTS idx_detailed_plot_versions_detailed_plot_id ON public.detailed_plot_versions USING btree (detailed_plot_id);

CREATE UNIQUE INDEX idx_detailed_plot_versions_unique_current ON public.detailed_plot_versions USING btree (detailed_plot_id) WHERE (is_current_version = true);

CREATE INDEX IF NOT EXISTS idx_detailed_plot_versions_version_number ON public.detailed_plot_versions USING btree (detailed_plot_id, version_number);

CREATE INDEX IF NOT EXISTS idx_detailed_plot_versions_version_type ON public.detailed_plot_versions USING btree (detailed_plot_id, version_type);

CREATE INDEX IF NOT EXISTS idx_detailed_plots_chapter_outline_id ON public.detailed_plots USING btree (chapter_outline_id);

CREATE INDEX IF NOT EXISTS idx_detailed_plots_created_at ON public.detailed_plots USING btree (created_at);

CREATE INDEX IF NOT EXISTS idx_detailed_plots_logic_status ON public.detailed_plots USING btree (logic_status);

CREATE INDEX IF NOT EXISTS idx_detailed_plots_plot_outline_id ON public.detailed_plots USING btree (plot_outline_id);

CREATE INDEX IF NOT EXISTS idx_detailed_plots_scoring_status ON public.detailed_plots USING btree (scoring_status);

CREATE INDEX IF NOT EXISTS idx_detailed_plots_status ON public.detailed_plots USING btree (status);

CREATE INDEX IF NOT EXISTS idx_detailed_plots_total_score ON public.detailed_plots USING btree (total_score);

CREATE UNIQUE INDEX dimension_mappings_technical_name_key ON public.dimension_mappings USING btree (technical_name);

CREATE UNIQUE INDEX event_chapter_mappings_event_id_chapter_outline_id_key ON public.event_chapter_mappings USING btree (event_id, chapter_outline_id);

CREATE INDEX IF NOT EXISTS idx_event_chapter_mappings_chapter_id ON public.event_chapter_mappings USING btree (chapter_outline_id);

CREATE INDEX IF NOT EXISTS idx_event_chapter_mappings_event_id ON public.event_chapter_mappings USING btree (event_id);

CREATE INDEX IF NOT EXISTS idx_event_evolution_current ON public.event_evolution_history USING btree (original_event_id, is_current_version);

CREATE INDEX IF NOT EXISTS idx_event_evolution_original_id ON public.event_evolution_history USING btree (original_event_id);

CREATE INDEX IF NOT EXISTS idx_event_evolution_plot ON public.event_evolution_history USING btree (plot_outline_id);

CREATE INDEX IF NOT EXISTS idx_event_evolution_version ON public.event_evolution_history USING btree (original_event_id, version);

CREATE INDEX IF NOT EXISTS idx_event_scores_created_at ON public.event_scores USING btree (created_at);

CREATE INDEX IF NOT EXISTS idx_event_scores_event_id ON public.event_scores USING btree (event_id);

CREATE INDEX IF NOT EXISTS idx_event_scores_event_id_created_at ON public.event_scores USING btree (event_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_events_chapter_number ON public.events USING btree (chapter_number);

CREATE INDEX IF NOT EXISTS idx_events_created_at ON public.events USING btree (created_at);

CREATE INDEX IF NOT EXISTS idx_events_event_type ON public.events USING btree (event_type);

CREATE INDEX IF NOT EXISTS idx_events_plot_chapter_sequence ON public.events USING btree (plot_outline_id, chapter_number, sequence_order) WHERE (is_current_version = true);

CREATE INDEX IF NOT EXISTS idx_events_plot_current_version ON public.events USING btree (plot_outline_id, is_current_version) WHERE (is_current_version = true);

CREATE INDEX IF NOT EXISTS idx_events_plot_outline_id ON public.events USING btree (plot_outline_id);

CREATE INDEX IF NOT EXISTS idx_events_sequence_order ON public.events USING btree (plot_outline_id, sequence_order);

CREATE UNIQUE INDEX unique_current_version ON public.events USING btree (id) WHERE (is_current_version = true);

CREATE UNIQUE INDEX unique_event_version ON public.events USING btree (id, version);

CREATE INDEX IF NOT EXISTS idx_evolution_history_detailed_plot_id ON public.evolution_history USING btree (detailed_plot_id);

CREATE INDEX IF NOT EXISTS idx_evolution_history_evolution_type ON public.evolution_history USING btree (evolution_type);

CREATE INDEX IF NOT EXISTS idx_evolution_history_evolved_at ON public.evolution_history USING btree (evolved_at);

CREATE UNIQUE INDEX geographies_worldview_id_key ON public.geographies USING btree (worldview_id);

CREATE INDEX IF NOT EXISTS idx_geographies_regions ON public.geographies USING gin (regions);

CREATE UNIQUE INDEX historical_events_worldview_id_key ON public.historical_events USING btree (worldview_id);

CREATE UNIQUE INDEX history_cultures_worldview_id_key ON public.history_cultures USING btree (worldview_id);

CREATE INDEX IF NOT EXISTS idx_history_cultures_cultural_features ON public.history_cultures USING gin (cultural_features);

CREATE INDEX IF NOT EXISTS idx_history_cultures_current_conflicts ON public.history_cultures USING gin (current_conflicts);

CREATE INDEX IF NOT EXISTS idx_history_cultures_historical_events ON public.history_cultures USING gin (historical_events);

CREATE INDEX IF NOT EXISTS idx_history_cultures_worldview_id ON public.history_cultures USING btree (worldview_id);

CREATE INDEX IF NOT EXISTS idx_locations_coordinates ON public.locations USING btree (x, y);

CREATE INDEX IF NOT EXISTS idx_locations_importance ON public.locations USING btree (importance);

CREATE INDEX IF NOT EXISTS idx_locations_type ON public.locations USING btree (type);

CREATE INDEX IF NOT EXISTS idx_locations_worldview_id ON public.locations USING btree (worldview_id);

CREATE INDEX IF NOT EXISTS idx_logic_check_history_checked_at ON public.logic_check_history USING btree (checked_at);

CREATE INDEX IF NOT EXISTS idx_logic_check_history_plot_id ON public.logic_check_history USING btree (detailed_plot_id);

CREATE INDEX IF NOT EXISTS idx_logic_check_history_status ON public.logic_check_history USING btree (overall_status);

CREATE INDEX IF NOT EXISTS idx_plot_outlines_created_at ON public.plot_outlines USING btree (created_at);

CREATE INDEX IF NOT EXISTS idx_plot_outlines_status ON public.plot_outlines USING btree (status);

CREATE INDEX IF NOT EXISTS idx_plot_outlines_worldview_id ON public.plot_outlines USING btree (worldview_id);

CREATE INDEX IF NOT EXISTS idx_plot_points_plot_id ON public.plot_points USING btree (plot_outline_id);

CREATE INDEX IF NOT EXISTS idx_plot_points_position ON public.plot_points USING btree (plot_outline_id, "position");

CREATE INDEX IF NOT EXISTS idx_regions_coordinates ON public.regions USING btree (x, y);

CREATE INDEX IF NOT EXISTS idx_regions_importance ON public.regions USING btree (importance);

CREATE INDEX IF NOT EXISTS idx_regions_terrain_type ON public.regions USING btree (terrain_type);

CREATE INDEX IF NOT EXISTS idx_regions_worldview_id ON public.regions USING btree (worldview_id);

CREATE INDEX IF NOT EXISTS idx_scenes_chapter_id ON public.scenes USING btree (chapter_outline_id);

CREATE INDEX IF NOT EXISTS idx_scenes_number ON public.scenes USING btree (chapter_outline_id, scene_number);

CREATE UNIQUE INDEX scenes_chapter_outline_id_scene_number_key ON public.scenes USING btree (chapter_outline_id, scene_number);

CREATE INDEX IF NOT EXISTS idx_scoring_dimensions_dimension_name ON public.scoring_dimensions USING btree (dimension_name);

CREATE INDEX IF NOT EXISTS idx_scoring_dimensions_scoring_record_id ON public.scoring_dimensions USING btree (scoring_record_id);

CREATE UNIQUE INDEX scoring_dimensions_scoring_record_id_dimension_name_key ON public.scoring_dimensions USING btree (scoring_record_id, dimension_name);

CREATE INDEX IF NOT EXISTS idx_scoring_history_plot_id ON public.scoring_history USING btree (detailed_plot_id);

CREATE INDEX IF NOT EXISTS idx_scoring_history_scored_at ON public.scoring_history USING btree (scored_at);

CREATE INDEX IF NOT EXISTS idx_scoring_records_created_at ON public.scoring_records USING btree (created_at DESC);

CREATE INDEX IF NOT EXISTS idx_scoring_records_detailed_plot_id ON public.scoring_records USING btree (detailed_plot_id);

CREATE INDEX IF NOT EXISTS idx_simple_events_chapter_number ON public.simple_events_table USING btree (chapter_number);

CREATE INDEX IF NOT EXISTS idx_simple_events_created_at ON public.simple_events_table USING btree (created_at);

CREATE INDEX IF NOT EXISTS idx_simple_events_event_type ON public.simple_events_table USING btree (event_type);

CREATE INDEX IF NOT EXISTS idx_simple_events_plot_outline_id ON public.simple_events_table USING btree (plot_outline_id);

CREATE INDEX IF NOT EXISTS idx_simple_events_sequence_order ON public.simple_events_table USING btree (plot_outline_id, sequence_order);

CREATE UNIQUE INDEX societies_worldview_id_key ON public.societies USING btree (worldview_id);

CREATE INDEX IF NOT EXISTS idx_story_arc_points_plot_id ON public.story_arc_points USING btree (plot_outline_id);

CREATE INDEX IF NOT EXISTS idx_worldview_metadata_value ON public.worldview_metadata USING gin (metadata_value);

CREATE INDEX IF NOT EXISTS idx_worldview_metadata_worldview_id ON public.worldview_metadata USING btree (worldview_id);

CREATE UNIQUE INDEX worldview_metadata_worldview_id_metadata_key_key ON public.worldview_metadata USING btree (worldview_id, metadata_key);

CREATE UNIQUE INDEX worldviews_worldview_id_key ON public.worldviews USING btree (worldview_id);


-- ============================================
-- 第六部分：触发器
-- ============================================

CREATE TRIGGER trigger_update_chapter_outline_updated_at BEFORE UPDATE ON chapter_outlines FOR EACH ROW EXECUTE FUNCTION EXECUTE FUNCTION update_chapter_outline_updated_at();

CREATE TRIGGER update_character_groups_updated_at BEFORE UPDATE ON character_groups FOR EACH ROW EXECUTE FUNCTION EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_characters_updated_at BEFORE UPDATE ON characters FOR EACH ROW EXECUTE FUNCTION EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_update_version_number BEFORE INSERT ON detailed_plot_versions FOR EACH ROW EXECUTE FUNCTION EXECUTE FUNCTION update_version_number();

CREATE TRIGGER update_event_scores_updated_at BEFORE UPDATE ON event_scores FOR EACH ROW EXECUTE FUNCTION EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_update_events_updated_at BEFORE UPDATE ON events FOR EACH ROW EXECUTE FUNCTION EXECUTE FUNCTION update_events_updated_at();

CREATE TRIGGER update_geographies_updated_at BEFORE UPDATE ON geographies FOR EACH ROW EXECUTE FUNCTION EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_historical_events_updated_at BEFORE UPDATE ON historical_events FOR EACH ROW EXECUTE FUNCTION EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_history_cultures_updated_at BEFORE UPDATE ON history_cultures FOR EACH ROW EXECUTE FUNCTION EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_update_locations_updated_at BEFORE UPDATE ON locations FOR EACH ROW EXECUTE FUNCTION EXECUTE FUNCTION update_locations_updated_at();

CREATE TRIGGER trigger_sync_chapter_outline_fields AFTER UPDATE ON plot_outlines FOR EACH ROW EXECUTE FUNCTION EXECUTE FUNCTION sync_chapter_outline_fields();

CREATE TRIGGER trigger_update_plot_outline_updated_at BEFORE UPDATE ON plot_outlines FOR EACH ROW EXECUTE FUNCTION EXECUTE FUNCTION update_plot_outline_updated_at();

CREATE TRIGGER trigger_update_power_systems_updated_at BEFORE UPDATE ON power_systems FOR EACH ROW EXECUTE FUNCTION EXECUTE FUNCTION update_power_systems_updated_at();

CREATE TRIGGER trigger_update_regions_updated_at BEFORE UPDATE ON regions FOR EACH ROW EXECUTE FUNCTION EXECUTE FUNCTION update_regions_updated_at();

CREATE TRIGGER trigger_update_simple_events_updated_at BEFORE UPDATE ON simple_events_table FOR EACH ROW EXECUTE FUNCTION EXECUTE FUNCTION update_simple_events_updated_at();

CREATE TRIGGER update_societies_updated_at BEFORE UPDATE ON societies FOR EACH ROW EXECUTE FUNCTION EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_worldview_metadata_updated_at BEFORE UPDATE ON worldview_metadata FOR EACH ROW EXECUTE FUNCTION EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_worldviews_updated_at BEFORE UPDATE ON worldviews FOR EACH ROW EXECUTE FUNCTION EXECUTE FUNCTION update_updated_at_column();


-- ============================================
-- 第七部分：初始数据
-- ============================================

-- 插入标准化的维度映射数据
INSERT INTO dimension_mappings (id, technical_name, display_name, description, color_code, weight) VALUES
    ('dim_character_development', 'character_development', '角色发展性', '角色塑造是否生动深化', '#fa8c16', 0.20),
    ('dim_dramatic_conflict', 'dramatic_conflict', '戏剧冲突性', '冲突设置是否激烈有效', '#52c41a', 0.20),
    ('dim_dramatic_tension', 'dramatic_tension', '戏剧张力', '故事张力是否饱满', '#1890ff', 0.10),
    ('dim_emotional_impact', 'emotional_impact', '情感冲击', '情感表达是否深刻', '#52c41a', 0.10),
    ('dim_logic_consistency', 'logic_consistency', '逻辑自洽性', '故事逻辑是否严密合理', '#1890ff', 0.25),
    ('dim_originality_creativity', 'originality_creativity', '创新性', '内容是否新颖有创意', '#fa8c16', 0.10),
    ('dim_pacing_fluency', 'pacing_fluency', '节奏流畅度', '叙事节奏是否合理', '#eb2f96', 0.10),
    ('dim_thematic_depth', 'thematic_depth', '主题深度', '主题内涵是否深刻', '#722ed1', 0.10),
    ('dim_world_usage', 'world_usage', '世界观运用', '世界观设定运用是否到位', '#722ed1', 0.15),
    ('dim_writing_style', 'writing_style', '文笔风格', '语言文字表达是否优美', '#eb2f96', 0.20)
ON CONFLICT (technical_name) DO NOTHING;

-- ============================================
-- 完成提示
-- ============================================

SELECT 'Database initialization completed successfully!' as status;
