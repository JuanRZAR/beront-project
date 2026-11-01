CREATE OR REPLACE FUNCTION beront_api.catalog_brand_get(p jsonb)
RETURNS jsonb
LANGUAGE sql
SECURITY DEFINER
SET search_path = pg_catalog, public, beront_api
AS $function$
SELECT to_jsonb(b) FROM public.brands b WHERE b.id=(p->>'id')::uuid;
$function$;
REVOKE ALL ON FUNCTION beront_api.catalog_brand_get(jsonb) FROM PUBLIC;

