CREATE OR REPLACE FUNCTION beront_api.catalog_image_get(p jsonb)
RETURNS jsonb
LANGUAGE sql
SECURITY DEFINER
SET search_path = pg_catalog, public, beront_api
AS $function$
SELECT to_jsonb(i)||jsonb_build_object('filename',a.filename,'url',a.url)
 FROM public.product_images i JOIN public.media_assets a ON a.id=i.asset_id WHERE i.id=(p->>'id')::uuid;
$function$;
REVOKE ALL ON FUNCTION beront_api.catalog_image_get(jsonb) FROM PUBLIC;

