CREATE OR REPLACE FUNCTION beront_api.catalog_audience_get(p jsonb)
RETURNS jsonb
LANGUAGE sql
SECURITY DEFINER
SET search_path = pg_catalog, public, beront_api
AS $function$
SELECT to_jsonb(d) FROM public.audiences d WHERE d.id=(p->>'id')::uuid;
$function$;
REVOKE ALL ON FUNCTION beront_api.catalog_audience_get(jsonb) FROM PUBLIC;
