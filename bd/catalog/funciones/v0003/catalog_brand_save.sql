CREATE OR REPLACE FUNCTION beront_api.catalog_brand_save(p jsonb)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, public, beront_api
AS $function$
DECLARE result jsonb;
BEGIN
 UPDATE public.brands SET name=p->>'name',normalized_name=p->>'normalized_name',category_id=(p->>'category_id')::uuid,active=(p->>'active')::boolean,version=version+1
 WHERE id=(p->>'id')::uuid AND version=(p->>'version')::integer RETURNING to_jsonb(brands) INTO result;
 IF result IS NULL THEN RAISE EXCEPTION USING MESSAGE='VERSION_CONFLICT'; END IF;
 RETURN result;
END;
$function$;
REVOKE ALL ON FUNCTION beront_api.catalog_brand_save(jsonb) FROM PUBLIC;

