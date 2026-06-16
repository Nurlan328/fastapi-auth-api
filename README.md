# Auth API — учебный проект на FastAPI

Регистрация, логин, JWT-токены и защищённые эндпоинты.

## Структура (по слоям)

```
FastAPIProject/
├── main.py                 # точка входа, подключение роутеров
├── config.py               # типизированные настройки (pydantic-settings)
├── database.py             # engine + сессии SQLAlchemy
├── redis_client.py         # async-клиент Redis
├── broker.py               # публикация задач в RabbitMQ (продюсер)
├── worker.py               # консьюмер очереди (отдельный процесс)
├── security.py             # хеширование паролей + JWT
├── rate_limit.py           # ограничение частоты запросов (Redis)
├── dependencies.py         # get_current_user / get_current_admin
├── models.py               # ORM-модели SQLAlchemy — таблицы БД
├── schemas.py              # Pydantic-схемы — валидация и форма ответов
├── repositories/           # доступ к данным (запросы к БД)
│   └── user_repository.py
├── services/               # бизнес-логика
│   ├── auth_service.py
│   └── user_service.py
├── routers/                # HTTP-эндпоинты
│   ├── auth.py             # /auth/register, /auth/login
│   ├── users.py            # /users/me
│   └── admin.py            # /admin/users, /admin/stats
├── tests/                  # pytest
├── alembic/                # миграции БД (versions/)
├── alembic.ini             # конфиг Alembic
├── docker-compose.yml      # postgres + redis + rabbitmq
└── requirements.txt
```

Поток запроса: **router → service → repository → БД**. Роутер не содержит
SQL и бизнес-логики, репозиторий не знает про HTTP.

## Запуск

1. Установить зависимости (в активированном .venv):

   ```bash
   pip install -r requirements.txt
   ```

2. Поднять БД/брокеры и применить миграции:

   ```bash
   docker compose up -d        # postgres + redis + rabbitmq
   alembic upgrade head        # создать/обновить схему БД (вместо create_all)
   ```

3. Запустить сервер:

   ```bash
   fastapi dev main.py
   ```

4. Открыть документацию: http://127.0.0.1:8000/docs

> Изменил модель? Создай новую миграцию:
> `alembic revision --autogenerate -m "описание"` → затем `alembic upgrade head`.

## Как проверить (в Swagger /docs)

1. **POST /auth/register** — создай пользователя (username, email, password).
2. **POST /auth/login** — войди (или нажми зелёную кнопку **Authorize** сверху,
   введи username/password). Получишь токен.
3. **GET /users/me** — теперь работает: возвращает твои данные.
   Без токена вернёт `401 Unauthorized`.

## Что дальше (идеи для развития)

- Добавить refresh-токены.
- Полностью асинхронный слой БД (async SQLAlchemy + asyncpg).
- CI/CD (GitLab CI / GitHub Actions): прогон тестов и линтера.
- Мониторинг и логи (Prometheus, Grafana Loki, OpenTelemetry).
- Тот же API на Django + DRF — для сравнения подходов.
```
