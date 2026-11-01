CREATE OR REPLACE FUNCTION beront_api.catalog_product_save(p jsonb)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, public, beront_api
AS $function$
DECLARE result jsonb;
BEGIN
 IF (p->>'published')::boolean AND NOT (p->>'archived')::boolean THEN
 PERFORM d.id FROM public.presentations d JOIN public.variants v ON v.kind=d.kind AND v.volume_ml=d.volume_ml
 WHERE v.product_id=(p->>'id')::uuid AND v.active FOR SHARE OF d;
 IF NOT EXISTS(SELECT 1 FROM public.variants v JOIN public.presentations d ON d.kind=v.kind AND d.volume_ml=v.volume_ml
 WHERE v.product_id=(p->>'id')::uuid AND v.active AND d.active)
 THEN RAISE EXCEPTION USING MESSAGE='PRODUCT_NOT_READY'; END IF;
 END IF;
 UPDATE public.products SET brand_id=(p->>'brand_id')::uuid,name=p->>'name',slug=p->>'slug',audience=p->>'audience',
 description_es=p->>'description_es',description_en=p->>'description_en',
 published=(p->>'published')::boolean,archived=(p->>'archived')::boolean,sold_out=(p->>'sold_out')::boolean,version=version+1
 WHERE id=(p->>'id')::uuid AND version=(p->>'version')::integer RETURNING to_jsonb(products) INTO result;
 IF result IS NULL THEN RAISE EXCEPTION USING MESSAGE='VERSION_CONFLICT'; END IF;
 RETURN result;
END;
$function$;
REVOKE ALL ON FUNCTION beront_api.catalog_product_save(jsonb) FROM PUBLIC;

