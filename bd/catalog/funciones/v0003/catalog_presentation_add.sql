CREATE OR REPLACE FUNCTION beront_api.catalog_presentation_add(p jsonb)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, public, beront_api
AS $function$
DECLARE result jsonb;
BEGIN
 INSERT INTO public.presentations(id,name_es,name_en,active,version,kind,volume_ml) VALUES((p->>'id')::uuid,p->>'name_es',p->>'name_en',COALESCE((p->>'active')::boolean,true),1,p->>'kind',(p->>'volume_ml')::numeric) RETURNING to_jsonb(presentations) INTO result;
 RETURN result;
END;
$function$;
REVOKE ALL ON FUNCTION beront_api.catalog_presentation_add(jsonb) FROM PUBLIC;
