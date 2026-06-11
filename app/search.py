import re
import unicodedata

from app.db_models import ProductRecord

MIN_TOKEN_LEN = 2


def normalize(text: str) -> str:
    lowered = unicodedata.normalize("NFKD", text.lower())
    return lowered.encode("ascii", "ignore").decode("ascii")


def tokenize(query: str) -> list[str]:
    tokens = [
        normalize(part)
        for part in re.split(r"\s+", query.strip())
        if len(normalize(part)) >= MIN_TOKEN_LEN
    ]
    return tokens


def score_product(
    record: ProductRecord,
    query: str,
    *,
    translation: dict | None = None,
    category_label: str | None = None,
) -> int:
    tokens = tokenize(query)
    if not tokens:
        return 0

    fields: list[tuple[str, int]] = [
        (record.name, 12),
        (record.description, 6),
        (record.manufacturer, 10),
        (record.slug.replace("-", " "), 8),
        (record.category, 5),
        (" ".join(record.configurations), 7),
    ]
    if translation:
        fields.append((translation.get("name", ""), 12))
        fields.append((translation.get("description", ""), 6))
    if category_label:
        fields.append((category_label, 6))

    total = 0
    for token in tokens:
        token_score = 0
        for text, weight in fields:
            norm = normalize(text)
            if not norm:
                continue
            if norm == token:
                token_score = max(token_score, weight * 4)
            elif norm.startswith(token):
                token_score = max(token_score, weight * 3)
            elif token in norm.split():
                token_score = max(token_score, weight * 2)
            elif token in norm:
                token_score = max(token_score, weight)
        if token_score == 0:
            return 0
        total += token_score

    if len(tokens) > 1:
        full_query = normalize(query)
        combined = normalize(
            " ".join(
                [
                    record.name,
                    record.description,
                    record.manufacturer,
                    record.slug.replace("-", " "),
                ]
            )
        )
        if full_query in combined:
            total += 15

    return total
