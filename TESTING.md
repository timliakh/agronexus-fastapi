# Test Strategy — AgroNexus

Документ описывает подход к автоматизации тестирования demo-проекта AgroNexus (портфолио SDET / full-stack).

## Test pyramid

```
        ┌─────────────┐
        │ Integration │  pytest + TestClient — основной слой
        ├─────────────┤
        │    Unit     │  Vitest (frontend), services/search (planned)
        └─────────────┘
```

| Уровень | Инструмент | Что проверяем |
|---------|------------|---------------|
| API integration | pytest, httpx2 | REST endpoints, validation, auth, i18n |
| Frontend unit | Vitest, happy-dom | composables, utils |

## Scope

### Покрыто

- Каталог: список, slug/id, фильтры, поиск, бренды, локализация
- Заказы: создание, 404, неверная комплектация, out-of-stock
- Feedback: отправка, forbidden words, телефон, premium flag
- Admin: login, stats, CRUD товаров, upload image, feedback list/delete
- Meta: health, languages, store, i18n UI
- Pages: SPA shell, 301 redirect numeric id → slug

### Сознательно не покрыто (demo scope)

- Load / performance testing
- Cross-browser matrix
- Production PostgreSQL parity (тесты на SQLite in-memory)
- Browser E2E (Playwright и т.п.)

## Test environment

Переменные задаются в `tests/conftest.py` **до** импорта приложения:

| Variable | Test value | Назначение |
|----------|------------|------------|
| `DATABASE_URL` | `sqlite://` | In-memory БД, изоляция от dev/prod |
| `SECRET_KEY` | `test-secret-key` | HMAC admin-токенов |
| `ADMIN_PASSWORD` | `test-admin-pass` | Admin login в тестах |

Каждый тест с fixture `client` сбрасывает схему БД и прогоняет lifespan (Alembic + seed).

## Test data

- **Seed:** 6 demo-товаров при пустой БД (`app/seed.py`)
- **Factories:** `tests/factories.py` — builders для order, feedback, product payloads
- **Fixtures:** `client`, `admin_token`, `admin_headers` в `conftest.py`

## Pytest markers

| Marker | Назначение | Пример запуска |
|--------|------------|----------------|
| `smoke` | Критичные быстрые проверки | `pytest -m smoke` |
| `regression` | Полный API regression | `pytest -m regression` |
| `admin` | Admin API | `pytest -m admin` |

## Запуск локально

```bash
# Backend (coverage)
pip install -r requirements-dev.txt
pytest --cov=app --cov-report=term-missing

# Только smoke
pytest -m smoke

# Frontend
cd frontend && npm ci && npm test
```

## CI

GitHub Actions (`.github/workflows/ci.yml`):

1. `npm ci` → `npm run build` → `npm test`
2. `pytest --cov=app --cov-fail-under=65`

Coverage gate не даёт мёрджить PR при падении покрытия ниже порога.

## Структура тестов

```
tests/
├── conftest.py       # env, client, admin fixtures, frontend build
├── factories.py      # test data builders
├── test_products.py
├── test_orders.py
├── test_feedback.py
├── test_admin.py
├── test_meta.py
└── test_pages.py

frontend/src/
├── composables/useI18n.test.js
└── utils/site.test.js
```

## Roadmap (SDET portfolio)

- [ ] Unit-тесты: `search.py`, `validators.py`
- [ ] Schemathesis (OpenAPI contract / fuzz)
- [ ] Allure или HTML report в CI artifacts
- [ ] Multi-job CI: lint → unit → api
