"""Конфигурация приложения через pydantic-settings.

Все настройки — в одном типизированном месте. Значения берутся по приоритету:
  1) переменные окружения,
  2) файл .env,
  3) значения по умолчанию ниже.

pydantic заодно валидирует типы: например, ACCESS_TOKEN_EXPIRE_MINUTES обязан
быть int — если в .env положить туда текст, приложение упадёт сразу на старте,
а не где-то в рантайме.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # --- базы данных и брокеры ---
    DATABASE_URL: str = "sqlite:///./app.db"
    REDIS_URL: str = "redis://localhost:6379/0"
    RABBITMQ_URL: str = "amqp://guest:guest@localhost:5672/"

    # --- безопасность / JWT ---
    SECRET_KEY: str = "ЗАМЕНИ_МЕНЯ_на_длинный_случайный_секрет"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30


# Единый экземпляр настроек на всё приложение (импортируется везде, где нужно).
settings = Settings()
