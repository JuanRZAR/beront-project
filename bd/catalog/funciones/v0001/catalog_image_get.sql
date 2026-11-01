CREATE OR REPLACE FUNCTION beront_api.catalog_image_get(p jsonb)
RETURNS jsonb
LANGUAGE sql
SECURITY DEFINER
SET search_path = pg_catalog, public, beront_api
AS $function$
SELECT to_jsonb(i) FROM public.product_images i WHERE i.id=(p->>'id')::uuid;
$function$;
REVOKE ALL ON FUNCTION beront_api.catalog_image_get(jsonb) FROM PUBLIC;

