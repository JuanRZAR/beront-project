CREATE OR REPLACE FUNCTION beront_api.inventory_ensure_decants(p jsonb)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, public, beront_api
AS $function$
BEGIN
 INSERT INTO public.decant_stock(id,product_id,amount,version) VALUES(gen_random_uuid(),(p->>'product_id')::uuid,0,1)
 ON CONFLICT(product_id) DO NOTHING; RETURN '{}'::jsonb;
END;
$function$;
REVOKE ALL ON FUNCTION beront_api.inventory_ensure_decants(jsonb) FROM PUBLIC;

