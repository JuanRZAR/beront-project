CREATE OR REPLACE FUNCTION beront_api.orders_history_add(p jsonb)
RETURNS jsonb LANGUAGE plpgsql
SECURITY DEFINER SET search_path = pg_catalog, public, beront_api
AS $function$
BEGIN
 INSERT INTO public.order_history(id,order_id,status_id,name_es,name_en,actor_id,created_at)
 SELECT gen_random_uuid(),(p->>'order_id')::uuid,id,name_es,name_en,(p->>'actor_id')::uuid,CURRENT_TIMESTAMP
 FROM public.order_statuses WHERE id=(p->>'status_id')::uuid;
 RETURN '{}'::jsonb;
END;
$function$;
REVOKE ALL ON FUNCTION beront_api.orders_history_add(jsonb) FROM PUBLIC;
