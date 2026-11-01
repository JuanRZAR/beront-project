CREATE OR REPLACE FUNCTION beront_api.media_list(p jsonb)
RETURNS jsonb
LANGUAGE sql
SECURITY DEFINER
SET search_path = pg_catalog, public, beront_api
AS $function$
WITH selected AS(
 SELECT * FROM public.media_assets WHERE kind='product'
 AND (COALESCE(p->>'q','')='' OR strpos(lower(name),lower(p->>'q'))>0)
), page AS(SELECT * FROM selected ORDER BY created_at DESC,id
 OFFSET ((p->>'page')::integer-1)*(p->>'page_size')::integer LIMIT (p->>'page_size')::integer)
SELECT jsonb_build_object('items',COALESCE((SELECT jsonb_agg(to_jsonb(page) ORDER BY created_at DESC,id) FROM page),'[]'::jsonb),
 'total',(SELECT count(*) FROM selected));
$function$;
REVOKE ALL ON FUNCTION beront_api.media_list(jsonb) FROM PUBLIC;

