CREATE OR REPLACE FUNCTION beront_api.commerce_province_add(p jsonb)
RETURNS jsonb LANGUAGE plpgsql
SECURITY DEFINER SET search_path = pg_catalog, public, beront_api
AS $function$
DECLARE result jsonb;
BEGIN
 INSERT INTO public.provinces(id,code,name,mainland,active,version) VALUES((p->>'id')::uuid,p->>'code',p->>'name',(p->>'mainland')::boolean,COALESCE((p->>'active')::boolean,true),1) RETURNING to_jsonb(provinces) INTO result;
 RETURN result;
END;
$function$;
REVOKE ALL ON FUNCTION beront_api.commerce_province_add(jsonb) FROM PUBLIC;
