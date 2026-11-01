CREATE OR REPLACE FUNCTION beront_api.catalog_audience_save(p jsonb)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, public, beront_api
AS $function$
DECLARE result jsonb;
BEGIN
 
 UPDATE public.audiences SET name_es=p->>'name_es',name_en=p->>'name_en',active=(p->>'active')::boolean,version=version+1
 WHERE id=(p->>'id')::uuid AND version=(p->>'version')::integer RETURNING to_jsonb(audiences) INTO result;
 IF result IS NULL THEN RAISE EXCEPTION USING MESSAGE='VERSION_CONFLICT'; END IF;
 RETURN result;
END;
$function$;
REVOKE ALL ON FUNCTION beront_api.catalog_audience_save(jsonb) FROM PUBLIC;
