CREATE OR REPLACE FUNCTION beront_api.orders_status_add(p jsonb)
RETURNS jsonb LANGUAGE plpgsql
SECURITY DEFINER SET search_path = pg_catalog, public, beront_api
AS $function$
DECLARE result jsonb;
BEGIN
 INSERT INTO public.order_statuses(id,slug,name_es,name_en,phase,purpose,active,version) VALUES((p->>'id')::uuid,(p->>'slug')::text,(p->>'name_es')::text,(p->>'name_en')::text,(p->>'phase')::text,(p->>'purpose')::text,COALESCE((p->>'active')::boolean,true),1)
 RETURNING to_jsonb(order_statuses) INTO result; RETURN result;
END;
$function$;
REVOKE ALL ON FUNCTION beront_api.orders_status_add(jsonb) FROM PUBLIC;
