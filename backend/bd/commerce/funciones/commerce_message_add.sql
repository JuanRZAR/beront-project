CREATE OR REPLACE FUNCTION beront_api.commerce_message_add(p jsonb)
RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER
SET search_path = pg_catalog, public, beront_api
AS $function$
BEGIN
 IF EXISTS(SELECT 1 FROM jsonb_array_elements_text(p->'image_ids') v
  LEFT JOIN public.media_assets a ON a.id=v.value::uuid WHERE a.id IS NULL OR a.kind<>'product')
 THEN RAISE EXCEPTION USING MESSAGE='INVALID_ASSET'; END IF;
 INSERT INTO public.featured_messages(id,slug,content,primary_path,secondary_path,icon,stats_kind,position,active,starts_at,ends_at,version)
 VALUES((p->>'id')::uuid,p->>'slug',p->'content',p->>'primary_path',p->>'secondary_path',p->>'icon',p->>'stats_kind',
 (p->>'position')::integer,(p->>'active')::boolean,(p->>'starts_at')::timestamptz,(p->>'ends_at')::timestamptz,1);
 INSERT INTO public.featured_message_images(message_id,position,asset_id)
 SELECT (p->>'id')::uuid,ordinality-1,value::uuid FROM jsonb_array_elements_text(p->'image_ids') WITH ORDINALITY;
 RETURN beront_api.commerce_message_get(p);
END;
$function$;
REVOKE ALL ON FUNCTION beront_api.commerce_message_add(jsonb) FROM PUBLIC;
