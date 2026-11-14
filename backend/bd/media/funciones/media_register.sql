CREATE OR REPLACE FUNCTION beront_api.media_register(p jsonb)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, public, beront_api
AS $function$
DECLARE result jsonb; category text:=COALESCE(p->>'kind','product');
BEGIN
 PERFORM pg_advisory_xact_lock(hashtextextended(category||(p->>'checksum'),0));
 SELECT to_jsonb(a) INTO result FROM public.media_assets a WHERE checksum=p->>'checksum' AND kind=category;
 IF result IS NOT NULL THEN RETURN jsonb_build_object('asset',result,'created',false); END IF;
 INSERT INTO public.media_assets(id,filename,url,name,kind,checksum,width,height,size_bytes,uploaded_by,created_at,version)
 VALUES(COALESCE((p->>'id')::uuid,gen_random_uuid()),p->>'filename','/media/'||(p->>'filename'),COALESCE(p->>'name',''),category,p->>'checksum',
 (p->>'width')::integer,(p->>'height')::integer,(p->>'size_bytes')::integer,(p->>'uploaded_by')::uuid,CURRENT_TIMESTAMP,1)
 RETURNING to_jsonb(media_assets) INTO result;
 RETURN jsonb_build_object('asset',result,'created',true);
END;
$function$;
REVOKE ALL ON FUNCTION beront_api.media_register(jsonb) FROM PUBLIC;

