"""Точка входа в приложение."""
from fastapi import FastAPI

from routers import admin, auth, users

# Таблицы больше НЕ создаём здесь через create_all.
# Схемой управляет Alembic: перед запуском приложения выполни `alembic upgrade head`.

app = FastAPI(
    title="Auth API",
    description="Учебный проект: регистрация, логин, JWT, защищённые эндпоинты",
    version="1.0.0",
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(admin.router)


@app.get("/")
def root():
    return {"message": "Auth API работает. Открой /docs"}
