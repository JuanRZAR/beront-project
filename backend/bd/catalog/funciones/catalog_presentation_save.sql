CREATE OR REPLACE FUNCTION beront_api.catalog_presentation_save(p jsonb)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, public, beront_api
AS $function$
DECLARE result jsonb;
BEGIN
 PERFORM 1 FROM public.presentations WHERE id=(p->>'id')::uuid FOR UPDATE;
 IF NOT (p->>'active')::boolean AND EXISTS(
 SELECT 1 FROM public.variants v JOIN public.products pr ON pr.id=v.product_id
 JOIN public.presentations d ON d.kind=v.kind AND d.volume_ml=v.volume_ml
 WHERE d.id=(p->>'id')::uuid AND v.active AND pr.published AND NOT pr.archived
 ) THEN RAISE EXCEPTION USING MESSAGE='DEFINITION_IN_USE'; END IF;
 UPDATE public.presentations SET name_es=p->>'name_es',name_en=p->>'name_en',active=(p->>'active')::boolean,version=version+1
 WHERE id=(p->>'id')::uuid AND version=(p->>'version')::integer RETURNING to_jsonb(presentations) INTO result;
 IF result IS NULL THEN RAISE EXCEPTION USING MESSAGE='VERSION_CONFLICT'; END IF;
 RETURN result;
END;
$function$;
REVOKE ALL ON FUNCTION beront_api.catalog_presentation_save(jsonb) FROM PUBLIC;
