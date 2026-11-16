CREATE OR REPLACE FUNCTION beront_api.commerce_message_save(p jsonb)
RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER
SET search_path = pg_catalog, public, beront_api, pg_temp
AS $function$
BEGIN
 IF NOT EXISTS(SELECT 1 FROM public.featured_messages WHERE id=(p->>'id')::uuid)
 THEN RAISE EXCEPTION USING MESSAGE='NOT_FOUND'; END IF;
 UPDATE public.featured_messages SET slug=p->>'slug',content=p->'content',primary_path=p->>'primary_path',
 secondary_path=p->>'secondary_path',icon=p->>'icon',stats_kind=p->>'stats_kind',position=(p->>'position')::integer,
 active=(p->>'active')::boolean,starts_at=(p->>'starts_at')::timestamptz,ends_at=(p->>'ends_at')::timestamptz,version=version+1
 WHERE id=(p->>'id')::uuid AND version=(p->>'version')::integer;
 IF NOT FOUND THEN RAISE EXCEPTION USING MESSAGE='VERSION_CONFLICT'; END IF;
 IF EXISTS(SELECT 1 FROM jsonb_array_elements_text(p->'image_ids') v
  LEFT JOIN public.media_assets a ON a.id=v.value::uuid WHERE a.id IS NULL OR a.kind<>'product')
 THEN RAISE EXCEPTION USING MESSAGE='INVALID_ASSET'; END IF;
 DELETE FROM public.featured_message_images WHERE message_id=(p->>'id')::uuid;
 INSERT INTO public.featured_message_images(message_id,position,asset_id)
 SELECT (p->>'id')::uuid,ordinality-1,value::uuid FROM jsonb_array_elements_text(p->'image_ids') WITH ORDINALITY;
 RETURN beront_api.commerce_message_get(p);
END;
$function$;
REVOKE ALL ON FUNCTION beront_api.commerce_message_save(jsonb) FROM PUBLIC;
