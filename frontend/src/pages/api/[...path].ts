import type { APIRoute } from "astro";
import { proxy } from "../../shared/http/proxy";
export const ALL: APIRoute = ({ request, params, clientAddress }) => {
  let address = "";
  try {
    address = clientAddress;
  } catch {
    address = "";
  }
  return proxy(request, params.path ?? "", false, address);
};
