CREATE OR REPLACE FUNCTION beront_api.identity_admin_get(p jsonb)
RETURNS jsonb
LANGUAGE sql
SECURITY DEFINER
SET search_path = pg_catalog, public, beront_api
AS $function$
SELECT to_jsonb(a) - 'singleton_slot' FROM public.administrators a
 WHERE ((p->>'id') IS NOT NULL AND a.id=(p->>'id')::uuid)
 OR ((p->>'username') IS NOT NULL AND a.username=p->>'username')
 OR COALESCE((p->>'single')::boolean,false)
 LIMIT 1;
$function$;
REVOKE ALL ON FUNCTION beront_api.identity_admin_get(jsonb) FROM PUBLIC;

