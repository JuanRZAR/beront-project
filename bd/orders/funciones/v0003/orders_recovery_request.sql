CREATE OR REPLACE FUNCTION beront_api.orders_recovery_request(p jsonb)
RETURNS jsonb LANGUAGE plpgsql
SECURITY DEFINER SET search_path = pg_catalog, public, beront_api
AS $function$
DECLARE
 wait interval := make_interval(secs => (p->>'cooldown_seconds')::integer);
 latest timestamptz;
BEGIN
 PERFORM pg_advisory_xact_lock(hashtextextended('recovery-cedula:' || (p->>'cedula'), 0));
 PERFORM pg_advisory_xact_lock(hashtextextended('recovery-ip:' || (p->>'ip_hash'), 0));
 SELECT max(created_at) INTO latest FROM public.order_recovery_attempts
 WHERE (cedula = p->>'cedula' OR ip_hash = p->>'ip_hash') AND created_at > CURRENT_TIMESTAMP - wait;
 IF latest IS NOT NULL THEN
  RETURN jsonb_build_object('allowed', false,
   'retry_after', GREATEST(1, ceil(extract(epoch FROM (latest + wait - CURRENT_TIMESTAMP)))::integer),
   'orders', '[]'::jsonb);
 END IF;
 DELETE FROM public.order_recovery_attempts WHERE created_at < CURRENT_TIMESTAMP - interval '1 day';
 INSERT INTO public.order_recovery_attempts(id, cedula, ip_hash, created_at)
 VALUES(gen_random_uuid(), p->>'cedula', p->>'ip_hash', CURRENT_TIMESTAMP);
 RETURN jsonb_build_object('allowed', true, 'retry_after', 0,
  'orders', COALESCE((SELECT jsonb_agg(jsonb_build_object('code', r.code, 'email', r.email,
   'first_name', r.first_name, 'locale', r.locale, 'created_at', r.created_at, 'total', r.total) ORDER BY r.created_at DESC, r.id)
   FROM (SELECT * FROM public.orders o WHERE o.cedula = p->>'cedula' ORDER BY o.created_at DESC, o.id LIMIT 10) r), '[]'::jsonb));
END;
$function$;
REVOKE ALL ON FUNCTION beront_api.orders_recovery_request(jsonb) FROM PUBLIC;
