from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import computed_field
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="../.env", env_file_encoding="utf-8", extra="ignore"
    )

    # Database Config
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: int = 5432
    POSTGRES_HOST: str = "localhost"

    # Valkey cache/configuration
    VALKEY_PORT: int = 6379
    VALKEY_HOST: str = "localhost"

    # Security & Tokens
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    ENVIRONMENT: str = "development"
    PROJECT_NAME: str = "Automated Personal Finance & Expense Forecaster"

    @computed_field
    @property
    def async_database_url(self) -> str:
        """Constructs the asynchronous PostgreSQL connection URI."""
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @computed_field
    @property
    def valkey_url(self) -> str:
        """Generates the standard connection URI for Celery and Valkey/Redis."""
        return f"redis://{self.VALKEY_HOST}:{self.VALKEY_PORT}/0"


@lru_cache
def get_settings() -> Settings:
    """Caches settings so the .env file is only parsed once during runtime."""
    return Settings()


settings = get_settings()
