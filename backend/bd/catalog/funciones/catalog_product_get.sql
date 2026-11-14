CREATE OR REPLACE FUNCTION beront_api.catalog_product_get(p jsonb)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, public, beront_api
AS $function$
DECLARE result jsonb;
BEGIN
 IF COALESCE((p->>'lock')::boolean,false) THEN PERFORM 1 FROM public.products WHERE id=(p->>'id')::uuid FOR UPDATE; END IF;
 SELECT to_jsonb(pr)||jsonb_build_object('brand_name',b.name,'brand_active',b.active AND c.active AND au.active,'classifications',jsonb_build_array(c.slug),
 'accords',COALESCE((SELECT jsonb_agg(o.slug ORDER BY o.slug) FROM public.product_classifications pc JOIN public.classification_options o ON o.id=pc.option_id WHERE pc.product_id=pr.id AND o.dimension='accord' AND o.active),'[]'::jsonb),
 'usages',COALESCE((SELECT jsonb_agg(o.slug ORDER BY o.slug) FROM public.product_classifications pc JOIN public.classification_options o ON o.id=pc.option_id WHERE pc.product_id=pr.id AND o.dimension='usage' AND o.active),'[]'::jsonb),
 'profiles',COALESCE((SELECT jsonb_agg(o.slug ORDER BY o.slug) FROM public.product_classifications pc JOIN public.classification_options o ON o.id=pc.option_id WHERE pc.product_id=pr.id AND o.dimension='profile' AND o.active),'[]'::jsonb),
 'variants',COALESCE((SELECT jsonb_agg(to_jsonb(v)||jsonb_build_object('presentation_active',d.active) ORDER BY v.volume_ml,v.id) FROM public.variants v JOIN public.presentations d ON d.kind=v.kind AND d.volume_ml=v.volume_ml WHERE v.product_id=pr.id),'[]'::jsonb),
 'images',COALESCE((SELECT jsonb_agg(to_jsonb(i)||jsonb_build_object('filename',a.filename,'url',a.url) ORDER BY i.position,i.id)
 FROM public.product_images i JOIN public.media_assets a ON a.id=i.asset_id WHERE i.product_id=pr.id),'[]'::jsonb))
 INTO result FROM public.products pr JOIN public.brands b ON b.id=pr.brand_id JOIN public.categories c ON c.id=b.category_id JOIN public.audiences au ON au.slug=pr.audience WHERE pr.id=(p->>'id')::uuid;
 RETURN result;
END;
$function$;
REVOKE ALL ON FUNCTION beront_api.catalog_product_get(jsonb) FROM PUBLIC;

