CREATE OR REPLACE FUNCTION beront_api.identity_sessions_revoke_all(p jsonb)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, public, beront_api
AS $function$
BEGIN UPDATE public.admin_sessions SET revoked_at=(p->>'now')::timestamptz WHERE admin_id=(p->>'admin_id')::uuid AND revoked_at IS NULL; RETURN '{}'::jsonb; END;
$function$;
REVOKE ALL ON FUNCTION beront_api.identity_sessions_revoke_all(jsonb) FROM PUBLIC;

