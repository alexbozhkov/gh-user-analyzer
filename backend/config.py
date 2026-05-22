import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DEPLOY_ENV: str = "prod"
    LOG_LEVEL: str = "INFO"

    # Redis
    REDIS_URL: str = "redis://redis:6379/0"
    CACHE_TTL: int = 3600

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class TestSettings(Settings):
    DEPLOY_TENANT: str = "testing"


if os.getenv("DEPLOY_ENV") == "testing":
    settings = TestSettings()
else:
    settings = Settings()
