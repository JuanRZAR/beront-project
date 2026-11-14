import { serverGet } from "../../shared/http/server";
import type { OptionRow } from "../../shared/http/contracts";

const active = async (resource: string, cookie: string) =>
  (
    await serverGet<OptionRow[]>(
      "/api/v1/admin/catalog-options/" + resource,
      cookie,
    )
  ).data.filter((row) => row.active);

export async function loadOptions(cookie: string) {
  const [categories, audiences, accords, usages, profiles, presentations] =
    await Promise.all(
      [
        "categories",
        "audiences",
        "accords",
        "usages",
        "profiles",
        "presentations",
      ].map((resource) => active(resource, cookie)),
    );
  return {
    categories: categories!,
    audiences: audiences!,
    accords: accords!,
    usages: usages!,
    profiles: profiles!,
    presentations: presentations!,
  };
}
