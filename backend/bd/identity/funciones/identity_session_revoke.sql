CREATE OR REPLACE FUNCTION beront_api.identity_session_revoke(p jsonb)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, public, beront_api
AS $function$
BEGIN UPDATE public.admin_sessions SET revoked_at=(p->>'now')::timestamptz WHERE id=(p->>'id')::uuid; RETURN '{}'::jsonb; END;
$function$;
REVOKE ALL ON FUNCTION beront_api.identity_session_revoke(jsonb) FROM PUBLIC;

