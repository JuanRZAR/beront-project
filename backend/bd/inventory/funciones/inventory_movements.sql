CREATE OR REPLACE FUNCTION beront_api.inventory_movements(p jsonb)
RETURNS jsonb
LANGUAGE sql
SECURITY DEFINER
SET search_path = pg_catalog, public, beront_api
AS $function$
WITH labelled AS(
 SELECT m.*,pr.id AS product_id,pr.name AS product_name,b.name AS brand_name,v.volume_ml
 FROM public.stock_movements m
 LEFT JOIN public.variants v ON m.kind='full_bottle' AND v.id=m.target_id
 LEFT JOIN public.products pr ON pr.id=CASE m.kind WHEN 'decant' THEN m.target_id ELSE v.product_id END
 LEFT JOIN public.brands b ON b.id=pr.brand_id
), page AS(
 SELECT * FROM labelled ORDER BY created_at DESC,id
 OFFSET ((p->>'page')::integer-1)*(p->>'page_size')::integer LIMIT (p->>'page_size')::integer
)
SELECT jsonb_build_object('items',COALESCE((SELECT jsonb_agg(to_jsonb(page) ORDER BY created_at DESC,id) FROM page),'[]'::jsonb),
 'total',(SELECT count(*) FROM public.stock_movements));
$function$;
REVOKE ALL ON FUNCTION beront_api.inventory_movements(jsonb) FROM PUBLIC;
