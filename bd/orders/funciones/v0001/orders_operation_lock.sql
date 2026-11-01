CREATE OR REPLACE FUNCTION beront_api.orders_operation_lock(p jsonb)
RETURNS jsonb LANGUAGE plpgsql
SECURITY DEFINER SET search_path = pg_catalog, public, beront_api
AS $function$
BEGIN PERFORM pg_advisory_xact_lock(hashtextextended(p->>'operation_id',42)); RETURN '{}'::jsonb; END;
$function$;
REVOKE ALL ON FUNCTION beront_api.orders_operation_lock(jsonb) FROM PUBLIC;
