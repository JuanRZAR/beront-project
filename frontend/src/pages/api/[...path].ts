import type { APIRoute } from "astro";
import { proxy } from "../../shared/http/proxy";
import { clientIp } from "../../shared/http/server";
export const ALL: APIRoute = ({ request, params, clientAddress }) => {
  let address = "";
  try {
    address = clientAddress;
  } catch {
    address = "";
  }
  return proxy(request, params.path ?? "", false, clientIp(request, address));
};
