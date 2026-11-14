CREATE OR REPLACE FUNCTION beront_api.commerce_bank_save(p jsonb)
RETURNS jsonb LANGUAGE plpgsql
SECURITY DEFINER SET search_path = pg_catalog, public, beront_api
AS $function$
DECLARE result jsonb;
BEGIN
 UPDATE public.bank_accounts SET bank_name=p->>'bank_name',account_type=p->>'account_type',account_number=p->>'account_number',holder_name=p->>'holder_name',holder_identification=p->>'holder_identification',active=COALESCE((p->>'active')::boolean,true),version=version+1
 WHERE id=(p->>'id')::uuid AND version=(p->>'version')::integer RETURNING to_jsonb(bank_accounts) INTO result;
 IF result IS NULL THEN RAISE EXCEPTION USING MESSAGE='VERSION_CONFLICT'; END IF;
 RETURN result;
END;
$function$;
REVOKE ALL ON FUNCTION beront_api.commerce_bank_save(jsonb) FROM PUBLIC;
