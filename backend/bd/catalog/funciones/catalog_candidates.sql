CREATE OR REPLACE FUNCTION beront_api.catalog_candidates(p jsonb)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, public, beront_api
AS $function$
DECLARE
 f jsonb := COALESCE(p->'filters','{}'::jsonb);
 private boolean := COALESCE((p->>'private')::boolean,false);
 result jsonb := '[]'::jsonb;
 row record;
 has_variant boolean;
BEGIN
 has_variant := jsonb_array_length(COALESCE(f->'kind','[]'::jsonb))>0
 OR jsonb_array_length(COALESCE(f->'volume_ml','[]'::jsonb))>0
 OR f->>'min_price' IS NOT NULL OR f->>'max_price' IS NOT NULL;
 FOR row IN
 WITH matching AS (
  SELECT v.product_id,min(v.price) AS minimum FROM public.variants v JOIN public.presentations d ON d.kind=v.kind AND d.volume_ml=v.volume_ml
  WHERE (private OR (v.active AND d.active))
  AND (jsonb_array_length(COALESCE(f->'kind','[]'::jsonb))=0 OR v.kind IN(SELECT jsonb_array_elements_text(f->'kind')))
  AND (jsonb_array_length(COALESCE(f->'volume_ml','[]'::jsonb))=0 OR v.volume_ml IN(SELECT value::numeric FROM jsonb_array_elements_text(f->'volume_ml')))
  AND (f->>'min_price' IS NULL OR v.price>=(f->>'min_price')::numeric)
  AND (f->>'max_price' IS NULL OR v.price<=(f->>'max_price')::numeric)
  GROUP BY v.product_id
 )
 SELECT pr.id FROM public.products pr JOIN public.brands b ON b.id=pr.brand_id JOIN public.categories c ON c.id=b.category_id JOIN public.audiences au ON au.slug=pr.audience
 LEFT JOIN matching m ON m.product_id=pr.id
 WHERE (private OR (pr.published AND NOT pr.archived AND b.active AND c.active AND au.active))
 AND (COALESCE(f->>'q','')='' OR strpos(lower(pr.name),lower(f->>'q'))>0 OR strpos(lower(b.name),lower(f->>'q'))>0)
 AND (jsonb_array_length(COALESCE(f->'brand_id','[]'::jsonb))=0 OR pr.brand_id IN(SELECT value::uuid FROM jsonb_array_elements_text(f->'brand_id')))
 AND (jsonb_array_length(COALESCE(f->'audience','[]'::jsonb))=0 OR pr.audience IN(SELECT jsonb_array_elements_text(f->'audience')))
 AND (jsonb_array_length(COALESCE(f->'classification','[]'::jsonb))=0 OR c.slug IN(SELECT jsonb_array_elements_text(f->'classification')))
 AND (jsonb_array_length(COALESCE(f->'accord','[]'::jsonb))=0 OR EXISTS(SELECT 1 FROM public.product_classifications pc JOIN public.classification_options o ON o.id=pc.option_id WHERE pc.product_id=pr.id AND o.dimension='accord' AND o.active AND o.slug IN(SELECT jsonb_array_elements_text(f->'accord'))))
 AND (jsonb_array_length(COALESCE(f->'usage','[]'::jsonb))=0 OR EXISTS(SELECT 1 FROM public.product_classifications pc JOIN public.classification_options o ON o.id=pc.option_id WHERE pc.product_id=pr.id AND o.dimension='usage' AND o.active AND o.slug IN(SELECT jsonb_array_elements_text(f->'usage'))))
 AND (jsonb_array_length(COALESCE(f->'profile','[]'::jsonb))=0 OR EXISTS(SELECT 1 FROM public.product_classifications pc JOIN public.classification_options o ON o.id=pc.option_id WHERE pc.product_id=pr.id AND o.dimension='profile' AND o.active AND o.slug IN(SELECT jsonb_array_elements_text(f->'profile'))))
 AND ((private AND NOT has_variant) OR m.product_id IS NOT NULL)
 ORDER BY CASE WHEN f->>'sort'='price_asc' THEN m.minimum END ASC NULLS LAST,
 CASE WHEN f->>'sort'='price_desc' THEN m.minimum END DESC NULLS LAST,
 lower(pr.name),pr.id OFFSET COALESCE((p->>'offset')::integer,0) LIMIT COALESCE((p->>'limit')::integer,100)
 LOOP
  result := result || jsonb_build_array(beront_api.catalog_product_get(jsonb_build_object('id',row.id)));
 END LOOP;
 RETURN result;
END;
$function$;
REVOKE ALL ON FUNCTION beront_api.catalog_candidates(jsonb) FROM PUBLIC;
