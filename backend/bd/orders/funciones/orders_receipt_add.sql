CREATE OR REPLACE FUNCTION beront_api.orders_receipt_add(p jsonb)
RETURNS jsonb LANGUAGE plpgsql
SECURITY DEFINER SET search_path = pg_catalog, public, beront_api
AS $function$
BEGIN
 IF NOT EXISTS(SELECT 1 FROM public.media_assets WHERE id=(p->>'asset_id')::uuid AND kind='receipt') THEN RAISE EXCEPTION USING MESSAGE='INVALID_ASSET'; END IF;
 INSERT INTO public.order_receipts(id,order_id,asset_id,uploaded_by,created_at)
 VALUES(gen_random_uuid(),(p->>'order_id')::uuid,(p->>'asset_id')::uuid,(p->>'actor_id')::uuid,CURRENT_TIMESTAMP);
 RETURN '{}'::jsonb;
END;
$function$;
REVOKE ALL ON FUNCTION beront_api.orders_receipt_add(jsonb) FROM PUBLIC;
