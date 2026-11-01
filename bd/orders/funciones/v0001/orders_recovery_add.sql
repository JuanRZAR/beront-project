CREATE OR REPLACE FUNCTION beront_api.orders_recovery_add(p jsonb)
RETURNS jsonb LANGUAGE plpgsql
SECURITY DEFINER SET search_path = pg_catalog, public, beront_api
AS $function$
BEGIN
 INSERT INTO public.order_recoveries(id,cedula,created_at) VALUES(gen_random_uuid(),p->>'cedula',CURRENT_TIMESTAMP)
 ON CONFLICT(cedula) WHERE resolved_at IS NULL DO NOTHING;
 RETURN '{}'::jsonb;
END;
$function$;
REVOKE ALL ON FUNCTION beront_api.orders_recovery_add(jsonb) FROM PUBLIC;
