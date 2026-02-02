# «Создание REST API на FastApi» — часть 1 (Сервис объявлений)

## 1) Описание проекта

Сервис объявлений купли/продажи на **FastAPI** с хранением данных в **PostgreSQL** и миграциями **Alembic**.  
Проект полностью **докеризирован** и содержит **автотесты** (pytest + httpx).

**Поля объявления:**
- заголовок (`title`)
- описание (`description`)
- цена (`price`)
- автор (`author`)
- дата создания (`created_at`, выставляется автоматически)

**Реализованные методы:**
- Создание: `POST /advertisement`
- Обновление: `PATCH /advertisement/{advertisement_id}`
- Удаление: `DELETE /advertisement/{advertisement_id}`
- Получение по id: `GET /advertisement/{advertisement_id}`
- Поиск по полям: `GET /advertisement?{query_string}`

> Авторизация/аутентификация по заданию **не требуется**.

---

## 2) Стек

- Python 3.11
- FastAPI + Uvicorn
- SQLAlchemy (async) + asyncpg
- Alembic (миграции)
- PostgreSQL 16
- Pytest + httpx (ASGITransport)
- Docker / Docker Compose

---

## 3) Структура проекта

```
.
├── .env
├── .env.example
├── .env.test
├── .env.test.example
├── alembic.ini
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── test_requests.http
├── alembic
│   ├── env.py
│   └── versions
│       └── 0001_create_advertisements.py
├── app
│   ├── __init__.py
│   ├── config.py
│   ├── crud.py
│   ├── db.py
│   ├── main.py
│   ├── models.py
│   └── schemas.py
└── tests
    ├── conftest.py
    ├── test_crud.py
    └── test_search.py
```

Ключевые файлы:
- `app/main.py` — FastAPI-приложение (роуты)
- `app/models.py` — SQLAlchemy-модель `Advertisement`
- `app/schemas.py` — Pydantic-схемы входа/выхода
- `app/db.py` — создание AsyncEngine/Session и зависимость `get_db`
- `app/crud.py` — CRUD/поиск через SQLAlchemy
- `alembic/env.py` — Alembic (async) и подтягивание `DATABASE_URL`
- `tests/*` — автотесты

---

## 4) Переменные окружения

Проект использует переменные окружения через `.env` / `.env.test`.

### 4.1 `.env.example` (для DEV)

Создайте файл `.env` на основе `.env.example`.

Пример (адаптируйте под себя):
```env
APP_NAME=Advertisements API
DEBUG=1

POSTGRES_DB=ads_db
POSTGRES_USER=ads_user
POSTGRES_PASSWORD=ads_pass

DATABASE_URL=postgresql+asyncpg://ads_user:ads_pass@postgres:5432/ads_db
```

### 4.2 `.env.test.example` (для TEST)

Создайте файл `.env.test` на основе `.env.test.example`.

Пример:
```env
APP_NAME=Advertisements API (tests)
DEBUG=0

DATABASE_URL=postgresql+asyncpg://ads_user:ads_pass@postgres_test:5432/ads_test_db
```

> Важно: в тестах `DATABASE_URL` должен указывать на **postgres_test** (имя сервиса в docker-compose).

---

## 5) Запуск проекта в Docker (DEV профиль)

### 5.1 Сборка и запуск

```bash
docker compose --profile dev up --build
```

Что происходит:
- запускается PostgreSQL (`postgres`)
- выполняются миграции `alembic upgrade head`
- поднимается API на `http://localhost:8000`

### 5.2 Swagger (проверка вручную)

- Swagger UI: **http://localhost:8000/docs**

Остановка:
```bash
docker compose --profile dev down
```

---

## 6) Миграции Alembic

Миграции выполняются автоматически при старте контейнера `api` (в профиле dev) и перед запуском тестов (в профиле test).

Если нужно запустить миграции вручную внутри контейнера:
```bash
docker compose --profile dev exec api alembic upgrade head
```

---

## 7) Эндпоинты API

### 7.1 Создание объявления
`POST /advertisement`

### 7.2 Обновление объявления
`PATCH /advertisement/{advertisement_id}`

### 7.3 Удаление объявления
`DELETE /advertisement/{advertisement_id}`

### 7.4 Получение по ID
`GET /advertisement/{advertisement_id}`

### 7.5 Поиск и фильтрация
`GET /advertisement?{query_string}`

Поддерживаемые query-параметры:
- `q` — общий поиск по `title/description/author`
- `title`, `description`, `author` — фильтры по отдельным полям
- `price_from`, `price_to` — фильтр по цене
- `created_from`, `created_to` — фильтр по дате (ISO-формат)
- `limit` (1..200), `offset` (>=0) — пагинация

---

## 8) HTTP-запросы для проверки (test_requests.http)

В корне проекта есть файл `test_requests.http` — его удобно запускать из **PyCharm / IntelliJ / VS Code (REST Client)**.

Содержимое (уже готово в файле проекта):

```http
@baseUrl = http://localhost:8000
@json = application/json

###
# Health (если у тебя есть /docs — можно просто открыть Swagger)
GET {{baseUrl}}/docs

###
# 1) CREATE: POST /advertisement
POST {{baseUrl}}/advertisement
Content-Type: {{json}}

{
  "title": "Продам RTX 4090",
  "description": "Новая, в коробке. Самовывоз.",
  "price": "2500.00",
  "author": "Voldemar"
}

###
# 2) GET by id: GET /advertisement/{id}
@adId = 1
GET {{baseUrl}}/advertisement/{{adId}}

###
# 3) PATCH: PATCH /advertisement/{id}
PATCH {{baseUrl}}/advertisement/{{adId}}
Content-Type: {{json}}

{
  "price": "2399.99",
  "description": "Срочно. Возможен торг."
}

###
# 4) SEARCH: GET /advertisement?{query_string}
GET {{baseUrl}}/advertisement?q=rtx
GET {{baseUrl}}/advertisement?author=Voldemar
GET {{baseUrl}}/advertisement?title=Продам
GET {{baseUrl}}/advertisement?description=торг
GET {{baseUrl}}/advertisement?price_from=1000&price_to=3000
GET {{baseUrl}}/advertisement?limit=10&offset=0
GET {{baseUrl}}/advertisement?q=rtx&author=Voldemar&price_from=2000&price_to=2600&limit=20&offset=0

###
# 5) DELETE: DELETE /advertisement/{id}
DELETE {{baseUrl}}/advertisement/{{adId}}

###
# 6) NEGATIVE CASES
GET {{baseUrl}}/advertisement/9999999

PATCH {{baseUrl}}/advertisement/9999999
Content-Type: {{json}}

{
  "price": "123.45"
}

DELETE {{baseUrl}}/advertisement/9999999

POST {{baseUrl}}/advertisement
Content-Type: {{json}}

{
  "title": "Неверная цена",
  "description": "Должно упасть с 422",
  "price": "0",
  "author": "Tester"
}
```

---

## 9) Тесты

Тесты находятся в папке `tests/`:
- `test_crud.py` — CRUD сценарий (создание → получение → обновление → удаление)
- `test_search.py` — проверка фильтров поиска

Технически тесты запускают приложение **внутри процесса** через `httpx.ASGITransport`, то есть **без поднятия отдельного uvicorn**.

---

## 10) Запуск тестов в Docker (TEST профиль)

```bash
docker compose --profile test up --build --abort-on-container-exit --exit-code-from tests
```

Ожидаемый результат:
- `2 passed`
- контейнер `tests` завершается с кодом `0`
- `postgres_test` останавливается вместе со всем compose (из-за `--abort-on-container-exit`)

---

## 11) Полезные команды Docker

Остановить и удалить контейнеры/сеть:
```bash
docker compose --profile dev down
docker compose --profile test down
```

Удалить volume базы (осторожно — удалит данные):
```bash
docker volume rm ex1_pgdata ex1_pgdata_test
```

---

## 12) Частые проблемы и решения

### 12.1 Ошибка `DATABASE_URL must be set for tests`
Проверьте:
- есть файл `.env.test`
- переменная `DATABASE_URL` в нём присутствует
- в docker-compose у `tests` указан `env_file: .env.test`

### 12.2 Ошибки event loop / httpx AsyncClient(app=...)
В новых версиях httpx **нельзя** передавать `app=...` напрямую.  
Должен использоваться `httpx.ASGITransport(app=fastapi_app)` — это уже учтено в проекте.

### 12.3 Postgres долго стартует
Мы используем `healthcheck` + `depends_on: condition: service_healthy`.  
Если на слабом железе — можно увеличить `retries/start_period` в `docker-compose.yml`.

---

## 13) Требования по заданию

✅ FastAPI + Docker  
✅ Поля: title/description/price/author/created_at  
✅ Методы: POST/PATCH/DELETE/GET by id/GET search  
✅ Без auth

---

## 14) Команды для проверки

### Запуск API (DEV)
```bash
docker compose --profile dev up --build
```

Проверка:
- Swagger UI: http://localhost:8000/docs

---

### Запуск тестов (TEST)
```bash
docker compose --profile test up --build --abort-on-container-exit --exit-code-from tests
```

Ожидаемый результат:
- `2 passed`

---
