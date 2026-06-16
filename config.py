"""Application configuration via pydantic-settings.

All settings live in one typed place. Values are resolved by priority:
  1) environment variables,
  2) the .env file,
  3) the defaults below.

pydantic also validates types: e.g. ACCESS_TOKEN_EXPIRE_MINUTES must be an int —
put text there in .env and the app fails on startup, not somewhere at runtime.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # --- databases and brokers ---
    DATABASE_URL: str = "sqlite:///./app.db"
    REDIS_URL: str = "redis://localhost:6379/0"
    RABBITMQ_URL: str = "amqp://guest:guest@localhost:5672/"

    # --- security / JWT ---
    SECRET_KEY: str = "CHANGE_ME_to_a_long_random_secret"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30


# A single settings instance for the whole application.
settings = Settings()
