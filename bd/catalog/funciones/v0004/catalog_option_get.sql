CREATE OR REPLACE FUNCTION beront_api.catalog_option_get(p jsonb)
RETURNS jsonb
LANGUAGE sql
SECURITY DEFINER
SET search_path = pg_catalog, public, beront_api
AS $function$
SELECT to_jsonb(d) FROM public.classification_options d WHERE d.id=(p->>'id')::uuid AND d.dimension=p->>'dimension';
$function$;
REVOKE ALL ON FUNCTION beront_api.catalog_option_get(jsonb) FROM PUBLIC;
