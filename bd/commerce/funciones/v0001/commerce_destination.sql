CREATE OR REPLACE FUNCTION beront_api.commerce_destination(p jsonb)
RETURNS jsonb LANGUAGE sql
SECURITY DEFINER SET search_path = pg_catalog, public, beront_api
AS $function$
SELECT to_jsonb(c)||jsonb_build_object('province_name',pr.name,'province_code',pr.code)
FROM public.cities c JOIN public.provinces pr ON pr.id=c.province_id
WHERE c.id=(p->>'id')::uuid AND c.active AND c.shipping_fee IS NOT NULL AND pr.active AND pr.mainland;
$function$;
REVOKE ALL ON FUNCTION beront_api.commerce_destination(jsonb) FROM PUBLIC;
