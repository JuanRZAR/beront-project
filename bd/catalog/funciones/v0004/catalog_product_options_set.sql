CREATE OR REPLACE FUNCTION beront_api.catalog_product_options_set(p jsonb)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, public, beront_api
AS $function$
DECLARE wanted integer;
BEGIN
 SELECT count(DISTINCT value) INTO wanted FROM jsonb_array_elements_text(COALESCE(p->'slugs','[]'::jsonb));
 IF (SELECT count(*) FROM public.classification_options o
 WHERE o.dimension=p->>'dimension' AND o.active AND o.slug IN(SELECT jsonb_array_elements_text(COALESCE(p->'slugs','[]'::jsonb)))) <> wanted
 THEN RAISE EXCEPTION USING MESSAGE='INVALID_OPTION'; END IF;
 DELETE FROM public.product_classifications pc USING public.classification_options o
 WHERE pc.option_id=o.id AND o.dimension=p->>'dimension' AND pc.product_id=(p->>'product_id')::uuid;
 INSERT INTO public.product_classifications(product_id,option_id)
 SELECT (p->>'product_id')::uuid,o.id FROM public.classification_options o
 WHERE o.dimension=p->>'dimension' AND o.slug IN(SELECT jsonb_array_elements_text(COALESCE(p->'slugs','[]'::jsonb)));
 RETURN '{}'::jsonb;
END;
$function$;
REVOKE ALL ON FUNCTION beront_api.catalog_product_options_set(jsonb) FROM PUBLIC;
