CREATE OR REPLACE FUNCTION beront_api.catalog_image_add(p jsonb)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, public, beront_api
AS $function$
BEGIN
 IF NOT EXISTS(SELECT 1 FROM public.media_assets WHERE id=(p->>'asset_id')::uuid AND kind='product') THEN RAISE EXCEPTION USING MESSAGE='INVALID_ASSET'; END IF;
 INSERT INTO public.product_images(id,product_id,asset_id,position,alt_es,alt_en,version)
 VALUES((p->>'id')::uuid,(p->>'product_id')::uuid,(p->>'asset_id')::uuid,COALESCE((p->>'position')::integer,0),COALESCE(p->>'alt_es',''),COALESCE(p->>'alt_en',''),1);
 RETURN '{}'::jsonb;
END;
$function$;
REVOKE ALL ON FUNCTION beront_api.catalog_image_add(jsonb) FROM PUBLIC;

