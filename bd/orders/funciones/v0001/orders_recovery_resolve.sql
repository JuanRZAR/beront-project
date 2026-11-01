CREATE OR REPLACE FUNCTION beront_api.orders_recovery_resolve(p jsonb)
RETURNS jsonb LANGUAGE plpgsql
SECURITY DEFINER SET search_path = pg_catalog, public, beront_api
AS $function$
DECLARE result jsonb;
BEGIN
 UPDATE public.order_recoveries SET resolved_at=COALESCE(resolved_at,CURRENT_TIMESTAMP),resolved_by=COALESCE(resolved_by,(p->>'actor_id')::uuid)
 WHERE id=(p->>'id')::uuid RETURNING to_jsonb(order_recoveries) INTO result;
 IF result IS NULL THEN RAISE EXCEPTION USING MESSAGE='NOT_FOUND'; END IF; RETURN result;
END;
$function$;
REVOKE ALL ON FUNCTION beront_api.orders_recovery_resolve(jsonb) FROM PUBLIC;
