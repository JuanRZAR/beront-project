CREATE OR REPLACE FUNCTION beront_api.orders_get(p jsonb)
RETURNS jsonb LANGUAGE plpgsql
SECURITY DEFINER SET search_path = pg_catalog, public, beront_api
AS $function$
DECLARE result jsonb;
BEGIN
 IF COALESCE((p->>'lock')::boolean,false) THEN PERFORM 1 FROM public.orders WHERE id=(p->>'id')::uuid FOR UPDATE; END IF;
 SELECT to_jsonb(o)||jsonb_build_object('status',to_jsonb(s),
 'items',COALESCE((SELECT jsonb_agg(to_jsonb(l) ORDER BY l.variant_id) FROM public.order_lines l WHERE l.order_id=o.id),'[]'::jsonb),
 'history',COALESCE((SELECT jsonb_agg(to_jsonb(h) ORDER BY h.created_at,h.id) FROM public.order_history h WHERE h.order_id=o.id),'[]'::jsonb),
 'receipts',COALESCE((SELECT jsonb_agg(to_jsonb(r)||jsonb_build_object('url',a.url) ORDER BY r.created_at,r.id) FROM public.order_receipts r JOIN public.media_assets a ON a.id=r.asset_id WHERE r.order_id=o.id),'[]'::jsonb))
 INTO result FROM public.orders o JOIN public.order_statuses s ON s.id=o.status_id
 WHERE o.id=(p->>'id')::uuid OR o.operation_id=(p->>'operation_id')::uuid OR o.code_hash=p->>'code_hash';
 RETURN result;
END;
$function$;
REVOKE ALL ON FUNCTION beront_api.orders_get(jsonb) FROM PUBLIC;
