from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=None, extra="ignore")

    app_name: str = "Advertisements Service"
    debug: bool = False

    # либо DATABASE_URL напрямую, либо собираем из POSTGRES_*
    database_url: str

    @property
    def is_debug(self) -> bool:
        return bool(self.debug)


@lru_cache
def get_settings() -> Settings:
    return Settings()


# ВАЖНО: оставляем ради совместимости со строками вида:
# from app.config import settings
settings = get_settings()
