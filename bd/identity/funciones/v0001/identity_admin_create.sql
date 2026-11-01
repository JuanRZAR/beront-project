CREATE OR REPLACE FUNCTION beront_api.identity_admin_create(p jsonb)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, public, beront_api
AS $function$
BEGIN
 IF EXISTS(SELECT 1 FROM public.administrators) THEN RAISE EXCEPTION USING MESSAGE='ADMIN_ALREADY_EXISTS'; END IF;
 INSERT INTO public.administrators(id,username,password_hash,active,singleton_slot)
 VALUES((p->>'id')::uuid,p->>'username',p->>'password_hash',COALESCE((p->>'active')::boolean,true),1);
 RETURN '{}'::jsonb;
END;
$function$;
REVOKE ALL ON FUNCTION beront_api.identity_admin_create(jsonb) FROM PUBLIC;

