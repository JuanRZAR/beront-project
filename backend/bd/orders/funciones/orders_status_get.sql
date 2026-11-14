CREATE OR REPLACE FUNCTION beront_api.orders_status_get(p jsonb)
RETURNS jsonb LANGUAGE sql
SECURITY DEFINER SET search_path = pg_catalog, public, beront_api
AS $function$
SELECT to_jsonb(d) FROM public.order_statuses d WHERE (d.id=(p->>'id')::uuid OR (p->>'purpose' IS NOT NULL AND d.purpose=p->>'purpose' AND d.active));
$function$;
REVOKE ALL ON FUNCTION beront_api.orders_status_get(jsonb) FROM PUBLIC;
