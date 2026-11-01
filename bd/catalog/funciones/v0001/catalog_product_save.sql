CREATE OR REPLACE FUNCTION beront_api.catalog_product_save(p jsonb)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, public, beront_api
AS $function$
DECLARE result jsonb;
BEGIN
 UPDATE public.products SET brand_id=(p->>'brand_id')::uuid,name=p->>'name',slug=p->>'slug',audience=p->>'audience',
 classifications=ARRAY(SELECT jsonb_array_elements_text(p->'classifications'))::varchar[],
 description_es=p->>'description_es',description_en=p->>'description_en',
 published=(p->>'published')::boolean,archived=(p->>'archived')::boolean,sold_out=(p->>'sold_out')::boolean,version=version+1
 WHERE id=(p->>'id')::uuid AND version=(p->>'version')::integer RETURNING to_jsonb(products) INTO result;
 IF result IS NULL THEN RAISE EXCEPTION USING MESSAGE='VERSION_CONFLICT'; END IF;
 RETURN result;
END;
$function$;
REVOKE ALL ON FUNCTION beront_api.catalog_product_save(jsonb) FROM PUBLIC;

