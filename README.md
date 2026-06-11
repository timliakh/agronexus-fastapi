# AgroNexus

Интернет-магазин автономной агротехники: каталог с фильтрами и поиском, оформление заказа, админ-панель, мультиязычность (ru / en / de / nl).

Стек: **FastAPI**, **PostgreSQL**, **SQLAlchemy**, **Vue 3** (Vite).

## Быстрый старт (Docker)

```bash
cp .env.example .env
# задайте SECRET_KEY в .env
docker compose up -d --build
```

| URL | Описание |
|-----|----------|
| http://localhost:8000 | Каталог |
| http://localhost:8000/catalog/agribot-x1 | Страница товара (SEO-slug) |
| http://localhost:8000/about | О нас |
| http://localhost:8000/contact | Контакты |
| http://localhost:8000/admin | Админ-панель |
| http://localhost:8000/docs | Swagger API |

Пароль админки — в `.env` (`ADMIN_PASSWORD`, по умолчанию `admin123`).

Остановка:

```bash
docker compose down
```

Логи API:

```bash
docker compose logs api --tail 50
```

Перезапуск только API:

```bash
docker compose up -d --force-recreate api
```

## Локальная разработка без Docker

1. Установите PostgreSQL и создайте БД `agrostore`.
2. Скопируйте и настройте окружение:

```bash
cp .env.example .env
python -m venv .venv
# .venv\Scripts\activate          # Windows
# source .venv/bin/activate   # Linux / macOS
pip install -r requirements.txt
```

3. Соберите фронтенд:

```bash
cd frontend
npm install
npm run build
cd ..
```

4. Запустите сервер:

```bash
uvicorn app.main:app --reload --port 8000
```

При первом запуске создаются таблицы, выполняются миграции и seed (6 демо-товаров).

## Переменные окружения

| Переменная | Обязательна | Описание |
|------------|-------------|----------|
| `SECRET_KEY` | да | Ключ HMAC для admin-токенов |
| `ADMIN_PASSWORD` | нет | Пароль админки (default: `admin123`) |
| `DATABASE_URL` | да | URL PostgreSQL |
| `POSTGRES_*` | для Docker | Учётные данные контейнера postgres |

В Docker `DATABASE_URL` для API переопределяется в `docker-compose.yml` на хост `postgres`.

Шаблон: [.env.example](.env.example)

## Структура проекта

```
app/                        # Backend (FastAPI)
├── main.py                 # точка входа FastAPI
├── config.py               # конфигурация из .env
├── dependencies.py         # сборка сервисов (DI)
├── routers/                # JSON API + SPA shell routes
├── services/               # бизнес-логика
├── repositories/           # доступ к БД
├── protocols/              # интерфейсы (SOLID / DIP)
├── storage/                # загрузка изображений
├── search.py               # ранжирование поиска
├── locales/                # переводы UI и товаров
└── seed.py                 # начальные данные

frontend/                   # Vue 3 SPA (Vite)
├── src/views/              # каталог, товар, заказ, админка
├── src/components/         # SiteHeader, SiteFooter, FilterBar
└── package.json

static/
├── style.css               # стили
├── dist/                   # сборка Vue (npm run build)
└── images/
uploads/products/           # фото товаров (volume в Docker)
```

## Frontend (Vue 3)

Сборка перед запуском backend или Docker:

```bash
cd frontend
npm install
npm run build
```

Dev-режим с hot reload (прокси API на `:8000`):

```bash
# терминал 1
uvicorn app.main:app --reload --port 8000

# терминал 2
cd frontend && npm run dev
```

Открыть http://localhost:5173

## Возможности витрины

- SEO-slug в URL товаров (`/catalog/harvestai-9000`)
- Фильтры по категории и бренду из шапки
- Поиск с подсказками (название, описание, бренд, комплектации, переводы)
- Общие компоненты шапки и футера на всех страницах

Примеры фильтров:

```
/?category=tractors&lang=ru
/?brand=neurofield-robotics&lang=ru
/?q=LiDAR&lang=ru
```

## API (основное)

| Метод | Путь | Назначение |
|-------|------|------------|
| GET | `/products` | Список товаров (`category`, `brand`, `q`) |
| GET | `/products/suggest` | Подсказки поиска |
| GET | `/products/brands` | Список брендов |
| GET | `/products/{slug}` | Товар по slug или id |
| POST | `/orders` | Создать заказ |
| GET | `/orders/{id}` | Получить заказ |
| GET | `/health` | Healthcheck |
| POST | `/admin/api/login` | Вход в админку |

Загрузка фото: `POST /admin/api/products/{id}/image` (требуется admin-токен).

## Языки

Список языков: `GET /languages` (labels, default, locale_tags). Переводы UI — `GET /i18n/{lang}` из `app/locales/*.json`. На клиенте composable `useI18n` загружает оба endpoint.

## Миграции (Alembic)

```bash
pip install -r requirements.txt
alembic upgrade head          # применить миграции
alembic revision --autogenerate -m "описание"  # новая миграция
```

При старте приложения миграции применяются автоматически. Seed выполняется **только при пустой БД**.

## Полезные команды

```bash
# Пересобрать и перезапустить API
docker compose up -d --build --force-recreate api

# Сбросить БД (удалит volume postgres)
docker compose down -v
```

## Разработка

В `requirements.txt` — runtime-зависимости, в `requirements-dev.txt` — тестовые (`pytest`, `httpx2`).

### Тесты

Стратегия и scope: [TESTING.md](TESTING.md)

```bash
cd frontend && npm install && npm test && npm run build
cd ..
pip install -r requirements-dev.txt
pytest --cov=app --cov-report=term-missing
pytest -m smoke          # быстрый subset
```

- **API:** pytest + SQLite (Alembic + seed), coverage gate в CI
- **Frontend:** Vitest (`frontend/src/**/*.test.js`)
- **CI:** GitHub Actions (`.github/workflows/ci.yml`)
