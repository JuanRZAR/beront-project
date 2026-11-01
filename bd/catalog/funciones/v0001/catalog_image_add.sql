CREATE OR REPLACE FUNCTION beront_api.catalog_image_add(p jsonb)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, public, beront_api
AS $function$
BEGIN
 INSERT INTO public.product_images(id,product_id,filename,position,alt_es,alt_en,version)
 VALUES((p->>'id')::uuid,(p->>'product_id')::uuid,p->>'filename',COALESCE((p->>'position')::integer,0),COALESCE(p->>'alt_es',''),COALESCE(p->>'alt_en',''),1);
 RETURN '{}'::jsonb;
END;
$function$;
REVOKE ALL ON FUNCTION beront_api.catalog_image_add(jsonb) FROM PUBLIC;

