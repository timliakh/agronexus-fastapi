import { describe, expect, it } from "vitest";
import {
  buildCatalogUrl,
  buildPageUrl,
  escapeHtml,
  productImageUrl,
} from "@/utils/site.js";

describe("site utils", () => {
  it("escapes HTML", () => {
    expect(escapeHtml(`<script>"x"</script>`)).toBe(
      "&lt;script&gt;&quot;x&quot;&lt;/script&gt;",
    );
  });

  it("returns placeholder for missing image", () => {
    expect(productImageUrl({})).toBe("/static/images/placeholder.svg");
    expect(productImageUrl({ image_url: "/uploads/products/1.png" })).toBe(
      "/uploads/products/1.png",
    );
  });

  it("builds catalog URL with filters", () => {
    const url = buildCatalogUrl("en", { category: "tractors", q: "LiDAR" });
    expect(url).toBe("/?lang=en&category=tractors&q=LiDAR");
  });

  it("builds page URL with lang", () => {
    expect(buildPageUrl("de", "/about")).toBe("/about?lang=de");
  });
});
