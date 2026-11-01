CREATE OR REPLACE FUNCTION beront_api.orders_recovery_list(p jsonb)
RETURNS jsonb LANGUAGE sql
SECURITY DEFINER SET search_path = pg_catalog, public, beront_api
AS $function$
SELECT jsonb_build_object('items',COALESCE((SELECT jsonb_agg(to_jsonb(r)||jsonb_build_object('orders',
 COALESCE((SELECT jsonb_agg(jsonb_build_object('id',o.id,'code',o.code,'created_at',o.created_at,'first_name',o.first_name,'last_name',o.last_name,'phone',o.phone,'email',o.email)) FROM public.orders o WHERE o.cedula=r.cedula),'[]'::jsonb)))
 FROM(SELECT * FROM public.order_recoveries WHERE resolved_at IS NULL ORDER BY created_at,id
 OFFSET ((p->>'page')::integer-1)*(p->>'page_size')::integer LIMIT (p->>'page_size')::integer) r),'[]'::jsonb),
 'total',(SELECT count(*) FROM public.order_recoveries WHERE resolved_at IS NULL));
$function$;
REVOKE ALL ON FUNCTION beront_api.orders_recovery_list(jsonb) FROM PUBLIC;
