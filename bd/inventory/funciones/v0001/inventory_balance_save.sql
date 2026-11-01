CREATE OR REPLACE FUNCTION beront_api.inventory_balance_save(p jsonb)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, public, beront_api
AS $function$
DECLARE next_version integer;
BEGIN
 IF p->>'kind'='decant' THEN
 UPDATE public.decant_stock SET amount=(p->>'amount')::numeric,version=version+1 WHERE id=(p->>'id')::uuid AND version=(p->>'version')::integer RETURNING version INTO next_version;
 ELSIF p->>'kind'='full_bottle' THEN
 IF (p->>'amount')::numeric <> trunc((p->>'amount')::numeric) THEN RAISE EXCEPTION USING MESSAGE='INVALID_ADJUSTMENT'; END IF;
 UPDATE public.bottle_stock SET amount=((p->>'amount')::numeric)::integer,version=version+1 WHERE id=(p->>'id')::uuid AND version=(p->>'version')::integer RETURNING version INTO next_version;
 END IF;
 IF next_version IS NULL THEN RAISE EXCEPTION USING MESSAGE='VERSION_CONFLICT'; END IF;
 RETURN jsonb_build_object('version',next_version);
END;
$function$;
REVOKE ALL ON FUNCTION beront_api.inventory_balance_save(jsonb) FROM PUBLIC;

