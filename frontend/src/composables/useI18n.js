import { ref } from "vue";
import router from "@/router";

const LOCALE_TAGS_FALLBACK = {
  ru: "ru-RU",
  en: "en-US",
  de: "de-DE",
  nl: "nl-NL",
};

const languages = ref([]);
const languageLabels = ref({});
const localeTags = ref({ ...LOCALE_TAGS_FALLBACK });
const defaultLanguage = ref("ru");
const languagesLoaded = ref(false);

function readLangFromUrl() {
  const params = new URLSearchParams(window.location.search);
  const queryLang = params.get("lang");
  const supported = languages.value.length ? languages.value : ["ru", "en", "de", "nl"];
  const fallback = defaultLanguage.value || "ru";

  if (queryLang && supported.includes(queryLang)) {
    localStorage.setItem("lang", queryLang);
    return queryLang;
  }

  const stored = localStorage.getItem("lang");
  if (stored && supported.includes(stored)) {
    return stored;
  }
  return fallback;
}

const lang = ref(readLangFromUrl());
const ui = ref(null);

function withLang(path) {
  const separator = path.includes("?") ? "&" : "?";
  return `${path}${separator}lang=${lang.value}`;
}

function format(key, vars = {}) {
  let text = ui.value?.[key] || key;
  for (const [name, value] of Object.entries(vars)) {
    text = text.replaceAll(`{${name}}`, String(value));
  }
  return text;
}

function formatPrice(amount) {
  const unit = ui.value?.currency_unit || "GRAM";
  const locale = localeTags.value[lang.value] || LOCALE_TAGS_FALLBACK[lang.value] || "ru-RU";
  return `${Number(amount).toLocaleString(locale)} ${unit}`;
}

function apiError(detail, fallback) {
  if (!detail) return fallback;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail.map((item) => item.msg || item.message || fallback).join("; ");
  }
  return fallback;
}

async function loadLanguages() {
  const response = await fetch("/languages");
  if (!response.ok) throw new Error("languages load failed");
  const data = await response.json();
  languages.value = data.languages;
  languageLabels.value = data.labels;
  localeTags.value = { ...LOCALE_TAGS_FALLBACK, ...data.locale_tags };
  defaultLanguage.value = data.default;
  languagesLoaded.value = true;

  if (!languages.value.includes(lang.value)) {
    lang.value = defaultLanguage.value;
    localStorage.setItem("lang", lang.value);
  }
}

async function loadUi() {
  if (!languagesLoaded.value) {
    await loadLanguages();
  }
  const response = await fetch(withLang(`/i18n/${lang.value}`));
  if (!response.ok) throw new Error("i18n load failed");
  ui.value = await response.json();
  return ui.value;
}

async function setLang(nextLang) {
  if (!languagesLoaded.value) {
    await loadLanguages();
  }
  if (!languages.value.includes(nextLang)) {
    return;
  }
  localStorage.setItem("lang", nextLang);
  lang.value = nextLang;
  ui.value = null;
  await loadUi();

  const current = router.currentRoute.value;
  await router.replace({
    path: current.path,
    query: { ...current.query, lang: nextLang },
  });
}

export function useI18n() {
  return {
    lang,
    ui,
    languages,
    languageLabels,
    localeTags,
    defaultLanguage,
    loadLanguages,
    loadUi,
    setLang,
    withLang,
    format,
    formatPrice,
    apiError,
  };
}
