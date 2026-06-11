import json
from pathlib import Path

LOCALES_DIR = Path(__file__).resolve().parent / "locales"
SUPPORTED_LANGUAGES = ("ru", "en", "de", "nl")
DEFAULT_LANGUAGE = "ru"

LANGUAGE_LABELS = {
    "ru": "Русский",
    "en": "English",
    "de": "Deutsch",
    "nl": "Nederlands",
}

LOCALE_TAGS = {
    "ru": "ru-RU",
    "en": "en-US",
    "de": "de-DE",
    "nl": "nl-NL",
}

_UI_CACHE: dict[str, dict] = {}
_PRODUCTS_CACHE: dict | None = None


def normalize_lang(lang: str | None) -> str:
    if lang and lang.lower() in SUPPORTED_LANGUAGES:
        return lang.lower()
    return DEFAULT_LANGUAGE


def _load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as file:
        return json.load(file)


def get_ui(lang: str | None) -> dict:
    code = normalize_lang(lang)
    if code not in _UI_CACHE:
        _UI_CACHE[code] = _load_json(LOCALES_DIR / f"{code}.json")
    return _UI_CACHE[code]


def get_product_translation(product_id: int, lang: str | None) -> dict | None:
    global _PRODUCTS_CACHE
    code = normalize_lang(lang)
    if code == DEFAULT_LANGUAGE:
        return None

    if _PRODUCTS_CACHE is None:
        _PRODUCTS_CACHE = _load_json(LOCALES_DIR / "products.json")

    product_data = _PRODUCTS_CACHE.get(str(product_id), {})
    return product_data.get(code)


def get_language_config() -> dict:
    return {
        "languages": list(SUPPORTED_LANGUAGES),
        "labels": dict(LANGUAGE_LABELS),
        "default": DEFAULT_LANGUAGE,
        "locale_tags": dict(LOCALE_TAGS),
    }


def translate(key: str, lang: str | None, **kwargs: str) -> str:
    ui = get_ui(lang)
    parts = key.split(".")
    value: object = ui
    for part in parts:
        if not isinstance(value, dict):
            return key
        value = value.get(part, key)
    if not isinstance(value, str):
        return key
    return value.format(**kwargs) if kwargs else value
