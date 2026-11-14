CREATE OR REPLACE FUNCTION beront_api.commerce_bank_list(p jsonb)
RETURNS jsonb LANGUAGE sql
SECURITY DEFINER SET search_path = pg_catalog, public, beront_api
AS $function$
SELECT COALESCE(jsonb_agg(to_jsonb(d) ORDER BY lower(d.bank_name),d.id),'[]'::jsonb) FROM public.bank_accounts d WHERE COALESCE((p->>'private')::boolean,false) OR (d.active);
$function$;
REVOKE ALL ON FUNCTION beront_api.commerce_bank_list(jsonb) FROM PUBLIC;
