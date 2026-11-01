CREATE OR REPLACE FUNCTION beront_api.catalog_variant_get(p jsonb)
RETURNS jsonb
LANGUAGE sql
SECURITY DEFINER
SET search_path = pg_catalog, public, beront_api
AS $function$
SELECT to_jsonb(v)||jsonb_build_object('presentation_active',d.active) FROM public.variants v JOIN public.presentations d ON d.kind=v.kind AND d.volume_ml=v.volume_ml WHERE v.id=(p->>'id')::uuid;
$function$;
REVOKE ALL ON FUNCTION beront_api.catalog_variant_get(jsonb) FROM PUBLIC;
