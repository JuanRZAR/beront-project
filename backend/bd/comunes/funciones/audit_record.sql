CREATE OR REPLACE FUNCTION beront_api.audit_record(p jsonb)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, public, beront_api
AS $function$
BEGIN
 INSERT INTO public.audit_events(id,actor_id,action,resource_id,request_id,created_at)
 VALUES(gen_random_uuid(),(p->>'actor_id')::uuid,p->>'action',p->>'resource_id',p->>'request_id',CURRENT_TIMESTAMP);
 RETURN '{}'::jsonb;
END;
$function$;
REVOKE ALL ON FUNCTION beront_api.audit_record(jsonb) FROM PUBLIC;

