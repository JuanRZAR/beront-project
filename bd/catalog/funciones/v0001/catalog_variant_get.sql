CREATE OR REPLACE FUNCTION beront_api.catalog_variant_get(p jsonb)
RETURNS jsonb
LANGUAGE sql
SECURITY DEFINER
SET search_path = pg_catalog, public, beront_api
AS $function$
SELECT to_jsonb(v) FROM public.variants v WHERE v.id=(p->>'id')::uuid;
$function$;
REVOKE ALL ON FUNCTION beront_api.catalog_variant_get(jsonb) FROM PUBLIC;

