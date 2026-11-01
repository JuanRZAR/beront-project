CREATE OR REPLACE FUNCTION beront_api.orders_transition_get(p jsonb)
RETURNS jsonb LANGUAGE sql
SECURITY DEFINER SET search_path = pg_catalog, public, beront_api
AS $function$
SELECT to_jsonb(d) FROM public.order_transitions d WHERE (d.id=(p->>'id')::uuid OR (d.from_status_id=(p->>'from_status_id')::uuid AND d.to_status_id=(p->>'to_status_id')::uuid AND d.active));
$function$;
REVOKE ALL ON FUNCTION beront_api.orders_transition_get(jsonb) FROM PUBLIC;
