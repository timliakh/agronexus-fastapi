import { useI18n } from "@/composables/useI18n";

export function productImageUrl(product) {
  return product?.image_url || "/static/images/placeholder.svg";
}

export function escapeHtml(text) {
  return String(text)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

export function buildCatalogUrl(lang, params = {}) {
  const url = new URL("/", "http://localhost");
  url.searchParams.set("lang", lang);
  if (params.category) url.searchParams.set("category", params.category);
  if (params.brand) url.searchParams.set("brand", params.brand);
  if (params.q) url.searchParams.set("q", params.q);
  return `${url.pathname}${url.search}`;
}

export function buildPageUrl(lang, path, params = {}) {
  const url = new URL(path, "http://localhost");
  url.searchParams.set("lang", lang);
  for (const [key, value] of Object.entries(params)) {
    if (value) url.searchParams.set(key, value);
  }
  return `${url.pathname}${url.search}`;
}

export function catalogUrl(params = {}) {
  const { lang } = useI18n();
  return buildCatalogUrl(lang.value, params);
}

export function pageUrl(path, params = {}) {
  const { lang } = useI18n();
  return buildPageUrl(lang.value, path, params);
}

export async function loadBrands() {
  const { withLang } = useI18n();
  const response = await fetch(withLang("/products/brands"));
  if (!response.ok) return [];
  return response.json();
}
