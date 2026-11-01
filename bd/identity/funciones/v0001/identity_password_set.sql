CREATE OR REPLACE FUNCTION beront_api.identity_password_set(p jsonb)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, public, beront_api
AS $function$
BEGIN
 UPDATE public.administrators SET password_hash=p->>'password_hash' WHERE id=(p->>'id')::uuid;
 IF NOT FOUND THEN RAISE EXCEPTION USING MESSAGE='NOT_FOUND'; END IF;
 RETURN '{}'::jsonb;
END;
$function$;
REVOKE ALL ON FUNCTION beront_api.identity_password_set(jsonb) FROM PUBLIC;

