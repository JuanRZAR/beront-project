CREATE OR REPLACE FUNCTION beront_api.catalog_product_add(p jsonb)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, public, beront_api
AS $function$
BEGIN
 INSERT INTO public.products(id,brand_id,name,slug,audience,classifications,description_es,description_en,published,archived,sold_out,version)
 VALUES((p->>'id')::uuid,(p->>'brand_id')::uuid,p->>'name',p->>'slug',p->>'audience',
 ARRAY(SELECT jsonb_array_elements_text(COALESCE(p->'classifications','[]'::jsonb)))::varchar[],
 COALESCE(p->>'description_es',''),COALESCE(p->>'description_en',''),
 COALESCE((p->>'published')::boolean,false),COALESCE((p->>'archived')::boolean,false),COALESCE((p->>'sold_out')::boolean,false),1);
 RETURN '{}'::jsonb;
END;
$function$;
REVOKE ALL ON FUNCTION beront_api.catalog_product_add(jsonb) FROM PUBLIC;

