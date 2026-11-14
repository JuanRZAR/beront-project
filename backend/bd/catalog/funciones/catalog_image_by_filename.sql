CREATE OR REPLACE FUNCTION beront_api.catalog_image_by_filename(p jsonb)
RETURNS jsonb
LANGUAGE sql
SECURITY DEFINER
SET search_path = pg_catalog, public, beront_api
AS $function$
SELECT to_jsonb(i)||jsonb_build_object('filename',a.filename,'url',a.url)
 FROM public.product_images i JOIN public.media_assets a ON a.id=i.asset_id WHERE a.filename=p->>'filename' ORDER BY i.id LIMIT 1;
$function$;
REVOKE ALL ON FUNCTION beront_api.catalog_image_by_filename(jsonb) FROM PUBLIC;

