CREATE OR REPLACE FUNCTION beront_api.catalog_product_by_slug(p jsonb)
RETURNS jsonb
LANGUAGE sql
SECURITY DEFINER
SET search_path = pg_catalog, public, beront_api
AS $function$
SELECT beront_api.catalog_product_get(jsonb_build_object('id',pr.id)) FROM public.products pr WHERE pr.slug=p->>'slug';
$function$;
REVOKE ALL ON FUNCTION beront_api.catalog_product_by_slug(jsonb) FROM PUBLIC;

