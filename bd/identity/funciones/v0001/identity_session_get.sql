CREATE OR REPLACE FUNCTION beront_api.identity_session_get(p jsonb)
RETURNS jsonb
LANGUAGE sql
SECURITY DEFINER
SET search_path = pg_catalog, public, beront_api
AS $function$
SELECT to_jsonb(s) FROM public.admin_sessions s WHERE s.token_hash=p->>'token_hash';
$function$;
REVOKE ALL ON FUNCTION beront_api.identity_session_get(jsonb) FROM PUBLIC;

