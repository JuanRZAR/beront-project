CREATE OR REPLACE FUNCTION beront_api.commerce_message_get(p jsonb)
RETURNS jsonb LANGUAGE sql SECURITY DEFINER
SET search_path = pg_catalog, public, beront_api
AS $function$
SELECT to_jsonb(m) || jsonb_build_object(
 'images', COALESCE((SELECT jsonb_agg(jsonb_build_object('id',a.id,'url',a.url,'name',a.name) ORDER BY i.position)
  FROM public.featured_message_images i JOIN public.media_assets a ON a.id=i.asset_id WHERE i.message_id=m.id),'[]'::jsonb),
 'image_ids', COALESCE((SELECT jsonb_agg(i.asset_id ORDER BY i.position) FROM public.featured_message_images i WHERE i.message_id=m.id),'[]'::jsonb))
FROM public.featured_messages m WHERE m.id=(p->>'id')::uuid;
$function$;
REVOKE ALL ON FUNCTION beront_api.commerce_message_get(jsonb) FROM PUBLIC;
