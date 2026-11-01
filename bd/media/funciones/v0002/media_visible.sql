CREATE OR REPLACE FUNCTION beront_api.media_visible(p jsonb)
RETURNS jsonb
LANGUAGE sql
SECURITY DEFINER
SET search_path = pg_catalog, public, beront_api
AS $function$
SELECT to_jsonb(a) FROM public.media_assets a WHERE a.filename=p->>'filename'
 AND (COALESCE((p->>'private')::boolean,false) OR (a.kind='product' AND EXISTS(
 SELECT 1 FROM public.product_images i JOIN public.products pr ON pr.id=i.product_id JOIN public.brands b ON b.id=pr.brand_id JOIN public.categories c ON c.id=b.category_id JOIN public.audiences au ON au.slug=pr.audience
 WHERE i.asset_id=a.id AND pr.published AND NOT pr.archived AND b.active AND c.active AND au.active)));
$function$;
REVOKE ALL ON FUNCTION beront_api.media_visible(jsonb) FROM PUBLIC;

