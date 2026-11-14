CREATE OR REPLACE FUNCTION beront_api.catalog_variant_save(p jsonb)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, public, beront_api
AS $function$
DECLARE result jsonb; product uuid;
BEGIN
 SELECT product_id INTO product FROM public.variants WHERE id=(p->>'id')::uuid;
 PERFORM 1 FROM public.products WHERE id=product FOR UPDATE;
 IF (p->>'active')::boolean=false
 AND EXISTS(SELECT 1 FROM public.products WHERE id=product AND published AND NOT archived)
 AND NOT EXISTS(SELECT 1 FROM public.variants v JOIN public.presentations d ON d.kind=v.kind AND d.volume_ml=v.volume_ml WHERE v.product_id=product AND v.active AND d.active AND v.id<>(p->>'id')::uuid)
 THEN RAISE EXCEPTION USING MESSAGE='PRODUCT_NOT_READY'; END IF;
 UPDATE public.variants SET price=(p->>'price')::numeric,active=(p->>'active')::boolean,sold_out=(p->>'sold_out')::boolean,version=version+1
 WHERE id=(p->>'id')::uuid AND version=(p->>'version')::integer RETURNING to_jsonb(variants) INTO result;
 IF result IS NULL THEN RAISE EXCEPTION USING MESSAGE='VERSION_CONFLICT'; END IF;
 RETURN result;
END;
$function$;
REVOKE ALL ON FUNCTION beront_api.catalog_variant_save(jsonb) FROM PUBLIC;

