CREATE OR REPLACE FUNCTION beront_api.orders_list(p jsonb)
RETURNS jsonb LANGUAGE plpgsql
SECURITY DEFINER SET search_path = pg_catalog, public, beront_api
AS $function$
DECLARE total integer; items jsonb:='[]'::jsonb; row record;
BEGIN
 SELECT count(*) INTO total FROM public.orders o WHERE (COALESCE(p->>'q','')='' OR strpos(lower(o.code),lower(p->>'q'))>0 OR o.cedula=p->>'q') AND (p->>'status_id' IS NULL OR o.status_id=(p->>'status_id')::uuid);
 FOR row IN SELECT o.id FROM public.orders o WHERE (COALESCE(p->>'q','')='' OR strpos(lower(o.code),lower(p->>'q'))>0 OR o.cedula=p->>'q') AND (p->>'status_id' IS NULL OR o.status_id=(p->>'status_id')::uuid) ORDER BY o.created_at DESC,o.id
 OFFSET ((p->>'page')::integer-1)*(p->>'page_size')::integer LIMIT (p->>'page_size')::integer
 LOOP items:=items||jsonb_build_array(beront_api.orders_get(jsonb_build_object('id',row.id))); END LOOP;
 RETURN jsonb_build_object('items',items,'total',total);
END;
$function$;
REVOKE ALL ON FUNCTION beront_api.orders_list(jsonb) FROM PUBLIC;
