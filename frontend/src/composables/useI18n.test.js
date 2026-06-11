import { describe, expect, it, vi, beforeEach } from "vitest";

const mockReplace = vi.fn();

vi.mock("@/router", () => ({
  default: {
    currentRoute: { value: { path: "/", query: { lang: "ru" } } },
    replace: (...args) => mockReplace(...args),
  },
}));

describe("useI18n", () => {
  beforeEach(() => {
    vi.resetModules();
    mockReplace.mockClear();
    vi.stubGlobal("fetch", vi.fn());
    vi.stubGlobal("localStorage", {
      getItem: vi.fn(() => "ru"),
      setItem: vi.fn(),
    });
  });

  it("loads languages from API", async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        languages: ["ru", "en"],
        labels: { ru: "Русский", en: "English" },
        default: "ru",
        locale_tags: { ru: "ru-RU", en: "en-US" },
      }),
    });

    const { useI18n } = await import("@/composables/useI18n.js");
    const { loadLanguages, languages, languageLabels } = useI18n();
    await loadLanguages();

    expect(languages.value).toEqual(["ru", "en"]);
    expect(languageLabels.value.en).toBe("English");
  });

  it("formats prices using locale tags", async () => {
    fetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          languages: ["en"],
          labels: { en: "English" },
          default: "en",
          locale_tags: { en: "en-US" },
        }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ currency_unit: "GRAM" }),
      });

    const { useI18n } = await import("@/composables/useI18n.js");
    const i18n = useI18n();
    i18n.lang.value = "en";
    await i18n.loadUi();

    expect(i18n.formatPrice(12500)).toContain("GRAM");
  });

  it("switches language with router.replace", async () => {
    fetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          languages: ["ru", "en"],
          labels: { ru: "Русский", en: "English" },
          default: "ru",
          locale_tags: {},
        }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ store_name: "AgroNexus" }),
      });

    const { useI18n } = await import("@/composables/useI18n.js");
    const { setLang, lang } = useI18n();
    await setLang("en");

    expect(lang.value).toBe("en");
    expect(mockReplace).toHaveBeenCalled();
  });
});
