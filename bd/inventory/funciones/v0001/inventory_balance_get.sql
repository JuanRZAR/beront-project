CREATE OR REPLACE FUNCTION beront_api.inventory_balance_get(p jsonb)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, public, beront_api
AS $function$
DECLARE d public.decant_stock%ROWTYPE; b public.bottle_stock%ROWTYPE;
BEGIN
 IF p->>'kind'='decant' THEN
  IF COALESCE((p->>'lock')::boolean,false) THEN SELECT * INTO d FROM public.decant_stock WHERE product_id=(p->>'target_id')::uuid FOR UPDATE;
  ELSE SELECT * INTO d FROM public.decant_stock WHERE product_id=(p->>'target_id')::uuid; END IF;
  IF NOT FOUND THEN RETURN NULL; END IF;
  RETURN to_jsonb(d)||jsonb_build_object('target_id',d.product_id,'kind','decant');
 ELSIF p->>'kind'='full_bottle' THEN
  IF COALESCE((p->>'lock')::boolean,false) THEN SELECT * INTO b FROM public.bottle_stock WHERE variant_id=(p->>'target_id')::uuid FOR UPDATE;
  ELSE SELECT * INTO b FROM public.bottle_stock WHERE variant_id=(p->>'target_id')::uuid; END IF;
  IF NOT FOUND THEN RETURN NULL; END IF;
  RETURN to_jsonb(b)||jsonb_build_object('target_id',b.variant_id,'kind','full_bottle');
 END IF;
 RETURN NULL;
END;
$function$;
REVOKE ALL ON FUNCTION beront_api.inventory_balance_get(jsonb) FROM PUBLIC;

