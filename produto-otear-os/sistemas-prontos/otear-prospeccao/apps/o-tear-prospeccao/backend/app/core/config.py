from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Supabase
    supabase_url: str
    supabase_anon_key: str
    supabase_service_role_key: str
    supabase_db_url: str

    # Backend
    api_secret_key: str = "dev-secret"
    cors_origins: str = "http://localhost:5173"

    # Webhook de Disparo
    dispatch_webhook_url: str = ""
    dispatch_webhook_secret: str = ""

    # Webhook de Retorno
    inbound_webhook_secret: str = ""

    # App
    timezone: str = "America/Sao_Paulo"
    default_language: str = "pt-BR"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",")]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
