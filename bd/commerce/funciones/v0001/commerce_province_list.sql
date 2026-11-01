CREATE OR REPLACE FUNCTION beront_api.commerce_province_list(p jsonb)
RETURNS jsonb LANGUAGE sql
SECURITY DEFINER SET search_path = pg_catalog, public, beront_api
AS $function$
SELECT COALESCE(jsonb_agg(to_jsonb(d) ORDER BY lower(d.name),d.id),'[]'::jsonb) FROM public.provinces d WHERE COALESCE((p->>'private')::boolean,false) OR (d.active AND d.mainland);
$function$;
REVOKE ALL ON FUNCTION beront_api.commerce_province_list(jsonb) FROM PUBLIC;
