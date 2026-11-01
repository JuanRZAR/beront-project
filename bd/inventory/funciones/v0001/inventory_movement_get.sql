CREATE OR REPLACE FUNCTION beront_api.inventory_movement_get(p jsonb)
RETURNS jsonb
LANGUAGE sql
SECURITY DEFINER
SET search_path = pg_catalog, public, beront_api
AS $function$
SELECT to_jsonb(m) FROM public.stock_movements m WHERE operation_id=(p->>'operation_id')::uuid;
$function$;
REVOKE ALL ON FUNCTION beront_api.inventory_movement_get(jsonb) FROM PUBLIC;

