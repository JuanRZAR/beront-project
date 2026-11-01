CREATE OR REPLACE FUNCTION beront_api.inventory_movement_add(p jsonb)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, public, beront_api
AS $function$
BEGIN
 INSERT INTO public.stock_movements(id,decant_stock_id,bottle_stock_id,target_id,kind,delta,balance_after,version_after,reason,actor_id,operation_id,fingerprint,created_at)
 VALUES((p->>'id')::uuid,
 CASE WHEN p->>'kind'='decant' THEN (p->>'balance_id')::uuid ELSE NULL END,
 CASE WHEN p->>'kind'='full_bottle' THEN (p->>'balance_id')::uuid ELSE NULL END,
 (p->>'target_id')::uuid,p->>'kind',(p->>'delta')::numeric,(p->>'balance_after')::numeric,
 (p->>'version_after')::integer,p->>'reason',(p->>'actor_id')::uuid,(p->>'operation_id')::uuid,p->>'fingerprint',(p->>'created_at')::timestamptz);
 RETURN '{}'::jsonb;
END;
$function$;
REVOKE ALL ON FUNCTION beront_api.inventory_movement_add(jsonb) FROM PUBLIC;

