
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    APP_NAME: str = "Tailr"
    APP_ENV: str = "development"
    DEBUG: bool = True

    API_PREFIX: str = "/api/v1"

    DATABASE_URL: str
    REDIS_URL: str = "redis://localhost:6379/0"

    GEMINI_API_KEY: str
    GEMINI_MODEL: str = "gemini-2.5-flash"

    LLAMA_CLOUD_API_KEY: str = ""
    LLAMA_CLOUD_PIPELINE_NAME: str = "tailr-resumes"

    QDRANT_URL: str = ""
    QDRANT_API_KEY: str = ""
    QDRANT_COLLECTION: str = "tailr-documents"

    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
