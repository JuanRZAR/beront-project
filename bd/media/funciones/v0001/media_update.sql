CREATE OR REPLACE FUNCTION beront_api.media_update(p jsonb)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, public, beront_api
AS $function$
DECLARE result jsonb;
BEGIN
 UPDATE public.media_assets SET name=p->>'name',version=version+1
 WHERE id=(p->>'id')::uuid AND kind='product' AND version=(p->>'version')::integer RETURNING to_jsonb(media_assets) INTO result;
 IF result IS NULL THEN RAISE EXCEPTION USING MESSAGE='VERSION_CONFLICT'; END IF;
 RETURN result;
END;
$function$;
REVOKE ALL ON FUNCTION beront_api.media_update(jsonb) FROM PUBLIC;

