CREATE OR REPLACE FUNCTION beront_api.catalog_image_save(p jsonb)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, public, beront_api
AS $function$
DECLARE result jsonb;
BEGIN
 UPDATE public.product_images SET position=(p->>'position')::integer,alt_es=p->>'alt_es',alt_en=p->>'alt_en',version=version+1
 WHERE id=(p->>'id')::uuid AND version=(p->>'version')::integer RETURNING to_jsonb(product_images) INTO result;
 IF result IS NULL THEN RAISE EXCEPTION USING MESSAGE='VERSION_CONFLICT'; END IF;
 RETURN result;
END;
$function$;
REVOKE ALL ON FUNCTION beront_api.catalog_image_save(jsonb) FROM PUBLIC;

