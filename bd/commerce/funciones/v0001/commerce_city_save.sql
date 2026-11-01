CREATE OR REPLACE FUNCTION beront_api.commerce_city_save(p jsonb)
RETURNS jsonb LANGUAGE plpgsql
SECURITY DEFINER SET search_path = pg_catalog, public, beront_api
AS $function$
DECLARE result jsonb;
BEGIN
 UPDATE public.cities SET name=p->>'name',shipping_fee=(p->>'shipping_fee')::numeric,active=COALESCE((p->>'active')::boolean,true),version=version+1
 WHERE id=(p->>'id')::uuid AND version=(p->>'version')::integer RETURNING to_jsonb(cities) INTO result;
 IF result IS NULL THEN RAISE EXCEPTION USING MESSAGE='VERSION_CONFLICT'; END IF;
 RETURN result;
END;
$function$;
REVOKE ALL ON FUNCTION beront_api.commerce_city_save(jsonb) FROM PUBLIC;
