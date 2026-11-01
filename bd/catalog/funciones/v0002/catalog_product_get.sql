CREATE OR REPLACE FUNCTION beront_api.catalog_product_get(p jsonb)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, public, beront_api
AS $function$
DECLARE result jsonb;
BEGIN
 IF COALESCE((p->>'lock')::boolean,false) THEN PERFORM 1 FROM public.products WHERE id=(p->>'id')::uuid FOR UPDATE; END IF;
 SELECT to_jsonb(pr)||jsonb_build_object('brand_name',b.name,'brand_active',b.active,
 'variants',COALESCE((SELECT jsonb_agg(to_jsonb(v) ORDER BY v.volume_ml,v.id) FROM public.variants v WHERE v.product_id=pr.id),'[]'::jsonb),
 'images',COALESCE((SELECT jsonb_agg(to_jsonb(i)||jsonb_build_object('filename',a.filename,'url',a.url) ORDER BY i.position,i.id)
 FROM public.product_images i JOIN public.media_assets a ON a.id=i.asset_id WHERE i.product_id=pr.id),'[]'::jsonb))
 INTO result FROM public.products pr JOIN public.brands b ON b.id=pr.brand_id WHERE pr.id=(p->>'id')::uuid;
 RETURN result;
END;
$function$;
REVOKE ALL ON FUNCTION beront_api.catalog_product_get(jsonb) FROM PUBLIC;

