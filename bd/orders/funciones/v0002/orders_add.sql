CREATE OR REPLACE FUNCTION beront_api.orders_add(p jsonb)
RETURNS jsonb LANGUAGE plpgsql
SECURITY DEFINER SET search_path = pg_catalog, public, beront_api
AS $function$
DECLARE item jsonb; current_price numeric; current_amount numeric; needed record;
BEGIN
 PERFORM 1 FROM public.order_statuses WHERE id=(p->>'status_id')::uuid AND active AND purpose=p->>'payment_method' AND phase='awaiting_payment' FOR SHARE;
 IF NOT FOUND THEN RAISE EXCEPTION USING MESSAGE='CHECKOUT_NOT_CONFIGURED'; END IF;
 PERFORM 1 FROM public.cities c JOIN public.provinces pr ON pr.id=c.province_id WHERE c.id=(p->>'city_id')::uuid
 AND pr.mainland AND (p->>'payment_method'='bank_transfer' OR (c.active AND pr.active AND c.shipping_fee=(p->>'shipping_fee')::numeric)) FOR SHARE OF c,pr;
 IF NOT FOUND THEN RAISE EXCEPTION USING MESSAGE='QUOTE_CHANGED'; END IF;
 IF p->>'payment_method'='whatsapp' THEN
 PERFORM 1 FROM public.store_settings WHERE id=1 AND version=(p->'terms_snapshot'->>'version')::integer FOR SHARE;
 IF NOT FOUND THEN RAISE EXCEPTION USING MESSAGE='QUOTE_CHANGED'; END IF;
 FOR item IN SELECT value FROM jsonb_array_elements(p->'items') ORDER BY value->>'product_id',value->>'variant_id'
 LOOP
 SELECT v.price INTO current_price FROM public.variants v JOIN public.products pr ON pr.id=v.product_id
 JOIN public.presentations d ON d.kind=v.kind AND d.volume_ml=v.volume_ml
 JOIN public.brands b ON b.id=pr.brand_id JOIN public.categories c ON c.id=b.category_id JOIN public.audiences au ON au.slug=pr.audience
 WHERE v.id=(item->>'variant_id')::uuid AND pr.id=(item->>'product_id')::uuid AND v.active AND d.active AND NOT v.sold_out
 AND pr.published AND NOT pr.archived AND NOT pr.sold_out AND b.active AND c.active AND au.active FOR SHARE OF v,pr;
 IF NOT FOUND OR current_price<>(item->>'unit_price')::numeric THEN RAISE EXCEPTION USING MESSAGE='QUOTE_CHANGED'; END IF;
 END LOOP;
 FOR needed IN SELECT value->>'kind' AS kind,CASE WHEN value->>'kind'='decant' THEN value->>'product_id' ELSE value->>'variant_id' END AS target,
 sum((value->>'quantity')::numeric*CASE WHEN value->>'kind'='decant' THEN (value->>'volume_ml')::numeric ELSE 1 END) AS amount
 FROM jsonb_array_elements(p->'items') GROUP BY 1,2 ORDER BY 1,2
 LOOP
 IF needed.kind='decant' THEN SELECT amount INTO current_amount FROM public.decant_stock WHERE product_id=needed.target::uuid FOR SHARE;
 ELSE SELECT amount INTO current_amount FROM public.bottle_stock WHERE variant_id=needed.target::uuid FOR SHARE; END IF;
 IF current_amount IS NULL OR current_amount<needed.amount THEN RAISE EXCEPTION USING MESSAGE='INSUFFICIENT_STOCK'; END IF;
 END LOOP;
 END IF;
 INSERT INTO public.orders(id,code,code_hash,operation_id,request_hash,locale,cedula,first_name,last_name,phone,email,city_id,city_name,province_name,address,subtotal,shipping_fee,total,payment_method,bank_snapshot,terms_snapshot,status_id,created_at,payment_state,guide_number,tracking_number,version)
 VALUES((p->>'id')::uuid,(p->>'code')::text,(p->>'code_hash')::text,(p->>'operation_id')::uuid,(p->>'request_hash')::text,(p->>'locale')::text,(p->>'cedula')::text,(p->>'first_name')::text,(p->>'last_name')::text,(p->>'phone')::text,(p->>'email')::text,(p->>'city_id')::uuid,(p->>'city_name')::text,(p->>'province_name')::text,(p->>'address')::text,(p->>'subtotal')::numeric,(p->>'shipping_fee')::numeric,(p->>'total')::numeric,(p->>'payment_method')::text,p->'bank_snapshot',p->'terms_snapshot',(p->>'status_id')::uuid,(p->>'created_at')::timestamptz,'pending','','',1);
 FOR item IN SELECT value FROM jsonb_array_elements(p->'items') LOOP
 INSERT INTO public.order_lines(id,order_id,variant_id,product_id,product_name,brand_name,kind,volume_ml,quantity,unit_price,line_total) VALUES(gen_random_uuid(),(p->>'id')::uuid,(item->>'variant_id')::uuid,(item->>'product_id')::uuid,(item->>'product_name')::text,(item->>'brand_name')::text,(item->>'kind')::text,(item->>'volume_ml')::numeric,(item->>'quantity')::integer,(item->>'unit_price')::numeric,(item->>'line_total')::numeric);
 END LOOP;
 RETURN '{}'::jsonb;
END;
$function$;
REVOKE ALL ON FUNCTION beront_api.orders_add(jsonb) FROM PUBLIC;
