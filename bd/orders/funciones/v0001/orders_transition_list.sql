CREATE OR REPLACE FUNCTION beront_api.orders_transition_list(p jsonb)
RETURNS jsonb LANGUAGE sql
SECURITY DEFINER SET search_path = pg_catalog, public, beront_api
AS $function$
SELECT COALESCE(jsonb_agg(to_jsonb(d) ORDER BY d.id),'[]'::jsonb) FROM public.order_transitions d;
$function$;
REVOKE ALL ON FUNCTION beront_api.orders_transition_list(jsonb) FROM PUBLIC;
