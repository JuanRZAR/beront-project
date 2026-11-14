CREATE OR REPLACE FUNCTION beront_api.commerce_bank_add(p jsonb)
RETURNS jsonb LANGUAGE plpgsql
SECURITY DEFINER SET search_path = pg_catalog, public, beront_api
AS $function$
DECLARE result jsonb;
BEGIN
 INSERT INTO public.bank_accounts(id,bank_name,account_type,account_number,holder_name,holder_identification,active,version) VALUES((p->>'id')::uuid,p->>'bank_name',p->>'account_type',p->>'account_number',p->>'holder_name',p->>'holder_identification',COALESCE((p->>'active')::boolean,true),1) RETURNING to_jsonb(bank_accounts) INTO result;
 RETURN result;
END;
$function$;
REVOKE ALL ON FUNCTION beront_api.commerce_bank_add(jsonb) FROM PUBLIC;
