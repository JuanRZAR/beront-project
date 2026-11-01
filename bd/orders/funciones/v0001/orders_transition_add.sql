CREATE OR REPLACE FUNCTION beront_api.orders_transition_add(p jsonb)
RETURNS jsonb LANGUAGE plpgsql
SECURITY DEFINER SET search_path = pg_catalog, public, beront_api
AS $function$
DECLARE result jsonb;
BEGIN
 INSERT INTO public.order_transitions(id,from_status_id,to_status_id,active,version) VALUES((p->>'id')::uuid,(p->>'from_status_id')::uuid,(p->>'to_status_id')::uuid,COALESCE((p->>'active')::boolean,true),1)
 RETURNING to_jsonb(order_transitions) INTO result; RETURN result;
END;
$function$;
REVOKE ALL ON FUNCTION beront_api.orders_transition_add(jsonb) FROM PUBLIC;
