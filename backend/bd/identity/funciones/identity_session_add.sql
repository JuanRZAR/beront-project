CREATE OR REPLACE FUNCTION beront_api.identity_session_add(p jsonb)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, public, beront_api
AS $function$
BEGIN
 INSERT INTO public.admin_sessions(id,admin_id,token_hash,created_at,last_seen_at,expires_at,revoked_at)
 VALUES((p->>'id')::uuid,(p->>'admin_id')::uuid,p->>'token_hash',(p->>'created_at')::timestamptz,
 (p->>'last_seen_at')::timestamptz,(p->>'expires_at')::timestamptz,(p->>'revoked_at')::timestamptz);
 RETURN '{}'::jsonb;
END;
$function$;
REVOKE ALL ON FUNCTION beront_api.identity_session_add(jsonb) FROM PUBLIC;

