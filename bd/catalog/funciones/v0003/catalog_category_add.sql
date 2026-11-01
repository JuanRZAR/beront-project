CREATE OR REPLACE FUNCTION beront_api.catalog_category_add(p jsonb)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, public, beront_api
AS $function$
DECLARE result jsonb;
BEGIN
 INSERT INTO public.categories(id,name_es,name_en,active,version,slug) VALUES((p->>'id')::uuid,p->>'name_es',p->>'name_en',COALESCE((p->>'active')::boolean,true),1,p->>'slug') RETURNING to_jsonb(categories) INTO result;
 RETURN result;
END;
$function$;
REVOKE ALL ON FUNCTION beront_api.catalog_category_add(jsonb) FROM PUBLIC;
