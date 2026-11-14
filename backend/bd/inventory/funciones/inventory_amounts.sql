CREATE OR REPLACE FUNCTION beront_api.inventory_amounts(p jsonb)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, public, beront_api
AS $function$
BEGIN
 IF p->>'kind'='decant' THEN
 RETURN (SELECT COALESCE(jsonb_object_agg(product_id::text,amount),'{}'::jsonb) FROM public.decant_stock WHERE product_id IN(SELECT value::uuid FROM jsonb_array_elements_text(p->'target_ids')));
 ELSIF p->>'kind'='full_bottle' THEN
 RETURN (SELECT COALESCE(jsonb_object_agg(variant_id::text,amount),'{}'::jsonb) FROM public.bottle_stock WHERE variant_id IN(SELECT value::uuid FROM jsonb_array_elements_text(p->'target_ids')));
 END IF;
 RAISE EXCEPTION USING MESSAGE='NOT_FOUND';
END;
$function$;
REVOKE ALL ON FUNCTION beront_api.inventory_amounts(jsonb) FROM PUBLIC;

