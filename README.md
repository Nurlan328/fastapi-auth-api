# Auth API — a FastAPI learning project

Registration, login, JWT tokens, and protected endpoints.

## Structure (by layers)

```
FastAPIProject/
├── main.py                 # entry point, wiring the routers together
├── config.py               # typed settings (pydantic-settings)
├── database.py             # SQLAlchemy engine + sessions
├── redis_client.py         # async Redis client
├── broker.py               # publishing tasks to RabbitMQ (producer)
├── worker.py               # queue consumer (separate process)
├── security.py             # password hashing + JWT
├── rate_limit.py           # request rate limiting (Redis)
├── dependencies.py         # get_current_user / get_current_admin
├── models.py               # SQLAlchemy ORM models — DB tables
├── schemas.py              # Pydantic schemas — validation and response shapes
├── repositories/           # data access (DB queries)
│   └── user_repository.py
├── services/               # business logic
│   ├── auth_service.py
│   └── user_service.py
├── routers/                # HTTP endpoints
│   ├── auth.py             # /auth/register, /auth/login
│   ├── users.py            # /users/me
│   └── admin.py            # /admin/users, /admin/stats
├── tests/                  # pytest
├── alembic/                # DB migrations (versions/)
├── alembic.ini             # Alembic config
├── docker-compose.yml      # postgres + redis + rabbitmq
└── requirements.txt
```

Request flow: **router → service → repository → DB**. The router contains no
SQL or business logic; the repository knows nothing about HTTP.

## Running

1. Install dependencies (inside the activated .venv):

   ```bash
   pip install -r requirements.txt
   ```

2. Start the databases/brokers and apply migrations:

   ```bash
   docker compose up -d        # postgres + redis + rabbitmq
   alembic upgrade head        # create/update the DB schema (instead of create_all)
   ```

3. Start the server:

   ```bash
   fastapi dev main.py
   ```

4. Open the docs: http://127.0.0.1:8000/docs

> Changed a model? Create a new migration:
> `alembic revision --autogenerate -m "description"` → then `alembic upgrade head`.

## How to try it (in Swagger /docs)

1. **POST /auth/register** — create a user (username, email, password).
2. **POST /auth/login** — log in (or click the green **Authorize** button at the
   top and enter username/password). You get a token.
3. **GET /users/me** — now works: returns your data.
   Without a token it returns `401 Unauthorized`.

## Background email worker

Registration publishes a "welcome email" task to RabbitMQ. A separate process
consumes it:

```bash
python worker.py
```

Register a user and watch the worker print the "sent" email.

## Tests

```bash
pytest -v
```

The suite uses in-memory SQLite and fakeredis, so it needs no Docker or external
services.

## Stack

Python 3.14 · FastAPI · SQLAlchemy · Alembic · PostgreSQL · Redis · RabbitMQ ·
JWT · bcrypt · Docker · pytest

## Ideas for further development

- Refresh tokens.
- A fully async DB layer (async SQLAlchemy + asyncpg).
- CI/CD (GitLab CI / GitHub Actions): run tests and a linter.
- Monitoring and logs (Prometheus, Grafana Loki, OpenTelemetry).
- The same API on Django + DRF — to compare approaches.
