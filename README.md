# WB Parsing & Analytics — краткий README

> Один репозиторий — один `.env`. Ниже **две готовые секции** для этого файла: скопируйте нужную в `.env` перед запуском.

---

## 1 . Быстрый старт (локальная разработка)

1. **Python & Node**

   ```bash
   python -m venv .venv && source .venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   cd wb-frontend && npm install
   ```
2. **PostgreSQL** — создаём БД и пользователя (один раз):

   ```bash
   sudo -u postgres psql <<'SQL'
   CREATE USER wb WITH PASSWORD 'wb';
   CREATE DATABASE wb OWNER wb;
   SQL
   ```
3. **.env** — скопируйте блок *DEV* (ниже) в корень проекта.
4. Миграции и парсинг:

   ```bash
   python manage.py migrate
   python manage.py fetch_wb --query="кроссовки" --pages=3
   ```
5. Запуск:

   ```bash
   python manage.py runserver        # http://127.0.0.1:8000/
   cd wb-frontend && npm run dev     # http://localhost:5173/
   ```

   Фронт проксирует `/api/*` на порт 8000.

---

## 2 . Полный стек в Docker

```bash
docker compose up -d        # nginx → http://localhost:8080/
```

При первом запуске:

* Postgres‑контейнер создаст пользователя/БД `wb`.
* Django выполнит миграции.
* Nginx отдаёт статический React + прокси `/api/*`.

---

## 3 . Шаблон `.env`

```dotenv
# ================== DEV (runserver + vite dev) ==================
# Скопируйте этот блок, если запускаете без Docker
POSTGRES_DB=wb
POSTGRES_USER=wb
POSTGRES_PASSWORD=wb
DB_HOST=localhost
DB_PORT=5432
DATABASE_URL=postgres://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${DB_HOST}:${DB_PORT}/${POSTGRES_DB}

SECRET_KEY=dev-secret
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,localhost:5173
CSRF_TRUSTED_ORIGINS=http://localhost:5173

# ================== DOCKER (compose) ==================
# Скопируйте этот блок вместо предыдущего, если запускаете через `docker compose`
POSTGRES_DB=wb
POSTGRES_USER=wb
POSTGRES_PASSWORD=wb
DB_HOST=db
DB_PORT=5432
DATABASE_URL=postgres://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${DB_HOST}:${DB_PORT}/${POSTGRES_DB}

SECRET_KEY=prod-secret-change-me
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,localhost:8080
CSRF_TRUSTED_ORIGINS=http://localhost:8080
```

> **Важно:** используйте **один** блок за раз. Поменяли способ запуска → перезапишите `.env` и перезапустите сервисы.

---

## 4 . Полезные команды

| Операция                         | Команда                                                 |
| -------------------------------- | ------------------------------------------------------- |
| Ручной парсинг новой категории   | `python manage.py fetch_wb --query="ноутбук" --pages=2` |
| Логи контейнера backend          | `docker compose logs -f backend`                        |
| Логи контейнера frontend (nginx) | `docker compose logs -f frontend`                       |

---
