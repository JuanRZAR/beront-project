CREATE OR REPLACE FUNCTION beront_api.catalog_category_list(p jsonb)
RETURNS jsonb
LANGUAGE sql
SECURITY DEFINER
SET search_path = pg_catalog, public, beront_api
AS $function$
SELECT COALESCE(jsonb_agg(to_jsonb(d) ORDER BY lower(d.name_es),d.id),'[]'::jsonb) FROM public.categories d WHERE COALESCE((p->>'private')::boolean,false) OR d.active;
$function$;
REVOKE ALL ON FUNCTION beront_api.catalog_category_list(jsonb) FROM PUBLIC;
