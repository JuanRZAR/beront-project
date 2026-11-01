CREATE OR REPLACE FUNCTION beront_api.inventory_movements(p jsonb)
RETURNS jsonb
LANGUAGE sql
SECURITY DEFINER
SET search_path = pg_catalog, public, beront_api
AS $function$
WITH page AS(SELECT * FROM public.stock_movements ORDER BY created_at DESC,id
 OFFSET ((p->>'page')::integer-1)*(p->>'page_size')::integer LIMIT (p->>'page_size')::integer)
 SELECT jsonb_build_object('items',COALESCE((SELECT jsonb_agg(to_jsonb(page) ORDER BY created_at DESC,id) FROM page),'[]'::jsonb),'total',(SELECT count(*) FROM public.stock_movements));
$function$;
REVOKE ALL ON FUNCTION beront_api.inventory_movements(jsonb) FROM PUBLIC;

