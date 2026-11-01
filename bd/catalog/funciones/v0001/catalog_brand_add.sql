CREATE OR REPLACE FUNCTION beront_api.catalog_brand_add(p jsonb)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, public, beront_api
AS $function$
BEGIN
 INSERT INTO public.brands(id,name,normalized_name,active,version)
 VALUES((p->>'id')::uuid,p->>'name',p->>'normalized_name',COALESCE((p->>'active')::boolean,true),1);
 RETURN '{}'::jsonb;
END;
$function$;
REVOKE ALL ON FUNCTION beront_api.catalog_brand_add(jsonb) FROM PUBLIC;

