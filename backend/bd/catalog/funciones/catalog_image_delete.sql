CREATE OR REPLACE FUNCTION beront_api.catalog_image_delete(p jsonb)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, public, beront_api
AS $function$
BEGIN
 DELETE FROM public.product_images WHERE id=(p->>'id')::uuid AND version=(p->>'version')::integer;
 IF NOT FOUND THEN RAISE EXCEPTION USING MESSAGE='VERSION_CONFLICT'; END IF;
 RETURN '{}'::jsonb;
END;
$function$;
REVOKE ALL ON FUNCTION beront_api.catalog_image_delete(jsonb) FROM PUBLIC;

