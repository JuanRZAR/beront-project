CREATE OR REPLACE FUNCTION beront_api.media_delete(p jsonb)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, public, beront_api
AS $function$
DECLARE asset public.media_assets%ROWTYPE;
BEGIN
 SELECT * INTO asset FROM public.media_assets WHERE id=(p->>'id')::uuid AND kind='product' FOR UPDATE;
 IF NOT FOUND THEN RAISE EXCEPTION USING MESSAGE='NOT_FOUND'; END IF;
 IF asset.version<>(p->>'version')::integer THEN RAISE EXCEPTION USING MESSAGE='VERSION_CONFLICT'; END IF;
 IF EXISTS(SELECT 1 FROM public.product_images WHERE asset_id=asset.id) THEN RAISE EXCEPTION USING MESSAGE='ASSET_IN_USE'; END IF;
 DELETE FROM public.media_assets WHERE id=asset.id;
 RETURN to_jsonb(asset);
END;
$function$;
REVOKE ALL ON FUNCTION beront_api.media_delete(jsonb) FROM PUBLIC;

