CREATE OR REPLACE FUNCTION beront_api.commerce_city_list(p jsonb)
RETURNS jsonb LANGUAGE sql
SECURITY DEFINER SET search_path = pg_catalog, public, beront_api
AS $function$
SELECT COALESCE(jsonb_agg(to_jsonb(d) ORDER BY lower(d.name),d.id),'[]'::jsonb) FROM public.cities d WHERE COALESCE((p->>'private')::boolean,false) OR (d.active AND d.shipping_fee IS NOT NULL AND EXISTS(SELECT 1 FROM public.provinces pr WHERE pr.id=d.province_id AND pr.active AND pr.mainland));
$function$;
REVOKE ALL ON FUNCTION beront_api.commerce_city_list(jsonb) FROM PUBLIC;
