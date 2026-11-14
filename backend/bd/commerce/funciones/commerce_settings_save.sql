CREATE OR REPLACE FUNCTION beront_api.commerce_settings_save(p jsonb)
RETURNS jsonb LANGUAGE plpgsql
SECURITY DEFINER SET search_path = pg_catalog, public, beront_api
AS $function$
DECLARE result jsonb;
BEGIN
 IF (p->>'version')::integer=0 THEN
 INSERT INTO public.store_settings(id,whatsapp_number,terms_es,terms_en,version)
 VALUES(1,p->>'whatsapp_number',p->>'terms_es',p->>'terms_en',1) RETURNING to_jsonb(store_settings) INTO result;
 ELSE
 UPDATE public.store_settings SET whatsapp_number=p->>'whatsapp_number',terms_es=p->>'terms_es',terms_en=p->>'terms_en',version=version+1
 WHERE id=1 AND version=(p->>'version')::integer RETURNING to_jsonb(store_settings) INTO result;
 END IF;
 IF result IS NULL THEN RAISE EXCEPTION USING MESSAGE='VERSION_CONFLICT'; END IF;
 RETURN result;
END;
$function$;
REVOKE ALL ON FUNCTION beront_api.commerce_settings_save(jsonb) FROM PUBLIC;
