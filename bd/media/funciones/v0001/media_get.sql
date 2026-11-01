CREATE OR REPLACE FUNCTION beront_api.media_get(p jsonb)
RETURNS jsonb
LANGUAGE sql
SECURITY DEFINER
SET search_path = pg_catalog, public, beront_api
AS $function$
SELECT to_jsonb(a) FROM public.media_assets a
 WHERE ((p->>'id') IS NOT NULL AND a.id=(p->>'id')::uuid)
 OR ((p->>'filename') IS NOT NULL AND a.filename=p->>'filename')
 OR ((p->>'checksum') IS NOT NULL AND a.checksum=p->>'checksum' AND a.kind=p->>'kind')
 LIMIT 1;
$function$;
REVOKE ALL ON FUNCTION beront_api.media_get(jsonb) FROM PUBLIC;

