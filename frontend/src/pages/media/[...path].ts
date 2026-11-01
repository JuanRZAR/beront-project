import type { APIRoute } from "astro";
import { proxy } from "../../shared/http/proxy";
export const ALL: APIRoute = ({ request, params }) =>
  proxy(request, params.path ?? "", true);
