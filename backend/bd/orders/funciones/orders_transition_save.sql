CREATE OR REPLACE FUNCTION beront_api.orders_transition_save(p jsonb)
RETURNS jsonb LANGUAGE plpgsql
SECURITY DEFINER SET search_path = pg_catalog, public, beront_api
AS $function$
DECLARE result jsonb;
BEGIN
 UPDATE public.order_transitions SET active=CASE WHEN p ? 'active' THEN COALESCE((p->>'active')::boolean,true) ELSE active END,version=version+1 WHERE id=(p->>'id')::uuid AND version=(p->>'version')::integer
 RETURNING to_jsonb(order_transitions) INTO result;
 IF result IS NULL THEN RAISE EXCEPTION USING MESSAGE='VERSION_CONFLICT'; END IF; RETURN result;
END;
$function$;
REVOKE ALL ON FUNCTION beront_api.orders_transition_save(jsonb) FROM PUBLIC;
