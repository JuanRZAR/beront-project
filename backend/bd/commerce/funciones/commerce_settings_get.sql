CREATE OR REPLACE FUNCTION beront_api.commerce_settings_get(p jsonb)
RETURNS jsonb LANGUAGE sql
SECURITY DEFINER SET search_path = pg_catalog, public, beront_api
AS $function$
SELECT to_jsonb(s) FROM public.store_settings s WHERE id=1;
$function$;
REVOKE ALL ON FUNCTION beront_api.commerce_settings_get(jsonb) FROM PUBLIC;
