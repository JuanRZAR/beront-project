CREATE OR REPLACE FUNCTION beront_api.catalog_variant_add(p jsonb)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, public, beront_api
AS $function$
BEGIN
 PERFORM 1 FROM public.presentations WHERE kind=p->>'kind' AND volume_ml=(p->>'volume_ml')::numeric AND active FOR SHARE;
 IF NOT FOUND THEN RAISE EXCEPTION USING MESSAGE='INVALID_PRESENTATION'; END IF;
 INSERT INTO public.variants(id,product_id,kind,volume_ml,price,active,sold_out,version)
 VALUES((p->>'id')::uuid,(p->>'product_id')::uuid,p->>'kind',(p->>'volume_ml')::numeric,(p->>'price')::numeric,
 COALESCE((p->>'active')::boolean,true),COALESCE((p->>'sold_out')::boolean,false),1);
 RETURN '{}'::jsonb;
END;
$function$;
REVOKE ALL ON FUNCTION beront_api.catalog_variant_add(jsonb) FROM PUBLIC;

