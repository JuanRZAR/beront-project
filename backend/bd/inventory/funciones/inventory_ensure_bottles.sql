CREATE OR REPLACE FUNCTION beront_api.inventory_ensure_bottles(p jsonb)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, public, beront_api
AS $function$
BEGIN
 INSERT INTO public.bottle_stock(id,variant_id,amount,version) VALUES(gen_random_uuid(),(p->>'variant_id')::uuid,0,1)
 ON CONFLICT(variant_id) DO NOTHING; RETURN '{}'::jsonb;
END;
$function$;
REVOKE ALL ON FUNCTION beront_api.inventory_ensure_bottles(jsonb) FROM PUBLIC;

