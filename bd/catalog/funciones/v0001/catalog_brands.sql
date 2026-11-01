CREATE OR REPLACE FUNCTION beront_api.catalog_brands(p jsonb)
RETURNS jsonb
LANGUAGE sql
SECURITY DEFINER
SET search_path = pg_catalog, public, beront_api
AS $function$
SELECT COALESCE(jsonb_agg(to_jsonb(b) ORDER BY lower(b.name),b.id),'[]'::jsonb) FROM public.brands b WHERE COALESCE((p->>'private')::boolean,false) OR b.active;
$function$;
REVOKE ALL ON FUNCTION beront_api.catalog_brands(jsonb) FROM PUBLIC;

