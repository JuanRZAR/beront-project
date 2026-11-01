CREATE OR REPLACE FUNCTION beront_api.orders_save(p jsonb)
RETURNS jsonb LANGUAGE plpgsql
SECURITY DEFINER SET search_path = pg_catalog, public, beront_api
AS $function$
DECLARE result jsonb;
BEGIN
 UPDATE public.orders SET status_id=(p->>'status_id')::uuid,payment_state=p->>'payment_state',
 payment_verified_at=(p->>'payment_verified_at')::timestamptz,paid_at=(p->>'paid_at')::timestamptz,approved_by=(p->>'approved_by')::uuid,
 guide_number=p->>'guide_number',tracking_number=p->>'tracking_number',version=version+1
 WHERE id=(p->>'id')::uuid AND version=(p->>'version')::integer RETURNING to_jsonb(orders) INTO result;
 IF result IS NULL THEN RAISE EXCEPTION USING MESSAGE='VERSION_CONFLICT'; END IF;
 RETURN result;
END;
$function$;
REVOKE ALL ON FUNCTION beront_api.orders_save(jsonb) FROM PUBLIC;
