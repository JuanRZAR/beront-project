CREATE OR REPLACE FUNCTION beront_api.commerce_city_add(p jsonb)
RETURNS jsonb LANGUAGE plpgsql
SECURITY DEFINER SET search_path = pg_catalog, public, beront_api
AS $function$
DECLARE result jsonb;
BEGIN
 INSERT INTO public.cities(id,province_id,name,shipping_fee,active,version) VALUES((p->>'id')::uuid,(p->>'province_id')::uuid,p->>'name',(p->>'shipping_fee')::numeric,COALESCE((p->>'active')::boolean,true),1) RETURNING to_jsonb(cities) INTO result;
 RETURN result;
END;
$function$;
REVOKE ALL ON FUNCTION beront_api.commerce_city_add(jsonb) FROM PUBLIC;
