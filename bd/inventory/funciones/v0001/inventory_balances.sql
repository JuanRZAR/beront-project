CREATE OR REPLACE FUNCTION beront_api.inventory_balances(p jsonb)
RETURNS jsonb
LANGUAGE sql
SECURITY DEFINER
SET search_path = pg_catalog, public, beront_api
AS $function$
WITH combined AS(
 SELECT 0 AS kind_order,d.id,to_jsonb(d)||jsonb_build_object('target_id',d.product_id,'kind','decant') AS item FROM public.decant_stock d
 UNION ALL SELECT 1,b.id,to_jsonb(b)||jsonb_build_object('target_id',b.variant_id,'kind','full_bottle') FROM public.bottle_stock b
), page AS(SELECT * FROM combined ORDER BY kind_order,id OFFSET ((p->>'page')::integer-1)*(p->>'page_size')::integer LIMIT (p->>'page_size')::integer)
SELECT jsonb_build_object('items',COALESCE((SELECT jsonb_agg(item ORDER BY kind_order,id) FROM page),'[]'::jsonb),'total',(SELECT count(*) FROM combined));
$function$;
REVOKE ALL ON FUNCTION beront_api.inventory_balances(jsonb) FROM PUBLIC;

