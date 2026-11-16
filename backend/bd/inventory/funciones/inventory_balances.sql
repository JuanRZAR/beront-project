CREATE OR REPLACE FUNCTION beront_api.inventory_balances(p jsonb)
RETURNS jsonb
LANGUAGE sql
SECURITY DEFINER
SET search_path = pg_catalog, public, beront_api, pg_temp
AS $function$
WITH combined AS(
 SELECT 0 AS kind_order,d.id,pr.name AS product_name,b.name AS brand_name,0::numeric AS volume,
  to_jsonb(d)||jsonb_build_object('target_id',d.product_id,'kind','decant','product_id',pr.id,
   'product_name',pr.name,'brand_name',b.name,'volume_ml',NULL::numeric) AS item
 FROM public.decant_stock d JOIN public.products pr ON pr.id=d.product_id JOIN public.brands b ON b.id=pr.brand_id
 UNION ALL
 SELECT 1,s.id,pr.name,b.name,v.volume_ml,
  to_jsonb(s)||jsonb_build_object('target_id',v.id,'kind','full_bottle','product_id',pr.id,
   'product_name',pr.name,'brand_name',b.name,'volume_ml',v.volume_ml)
 FROM public.bottle_stock s JOIN public.variants v ON v.id=s.variant_id
 JOIN public.products pr ON pr.id=v.product_id JOIN public.brands b ON b.id=pr.brand_id
), filtered AS(
 SELECT * FROM combined
 WHERE (p->>'kind' IS NULL OR item->>'kind'=p->>'kind')
 AND (COALESCE(p->>'q','')='' OR strpos(lower(product_name),lower(p->>'q'))>0 OR strpos(lower(brand_name),lower(p->>'q'))>0)
), page AS(
 SELECT * FROM filtered ORDER BY kind_order,lower(product_name),lower(brand_name),volume,id
 OFFSET ((p->>'page')::integer-1)*(p->>'page_size')::integer LIMIT (p->>'page_size')::integer
)
SELECT jsonb_build_object('items',COALESCE((SELECT jsonb_agg(item ORDER BY kind_order,lower(product_name),lower(brand_name),volume,id) FROM page),'[]'::jsonb),
 'total',(SELECT count(*) FROM filtered));
$function$;
REVOKE ALL ON FUNCTION beront_api.inventory_balances(jsonb) FROM PUBLIC;
