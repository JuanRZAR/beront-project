CREATE OR REPLACE FUNCTION beront_api.commerce_message_list(p jsonb)
RETURNS jsonb LANGUAGE sql SECURITY DEFINER
SET search_path = pg_catalog, public, beront_api
AS $function$
SELECT COALESCE(jsonb_agg(beront_api.commerce_message_get(jsonb_build_object('id',m.id)) ORDER BY m.position,m.id),'[]'::jsonb)
FROM public.featured_messages m
WHERE COALESCE((p->>'private')::boolean,false) OR
 (m.active AND (m.starts_at IS NULL OR m.starts_at<=CURRENT_TIMESTAMP) AND (m.ends_at IS NULL OR m.ends_at>CURRENT_TIMESTAMP));
$function$;
REVOKE ALL ON FUNCTION beront_api.commerce_message_list(jsonb) FROM PUBLIC;
