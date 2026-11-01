CREATE OR REPLACE FUNCTION beront_api.catalog_option_add(p jsonb)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, public, beront_api
AS $function$
DECLARE result jsonb;
BEGIN
 INSERT INTO public.classification_options(id,dimension,slug,name_es,name_en,active,version)
 VALUES((p->>'id')::uuid,p->>'dimension',p->>'slug',p->>'name_es',p->>'name_en',COALESCE((p->>'active')::boolean,true),1)
 RETURNING to_jsonb(classification_options) INTO result;
 RETURN result;
END;
$function$;
REVOKE ALL ON FUNCTION beront_api.catalog_option_add(jsonb) FROM PUBLIC;
