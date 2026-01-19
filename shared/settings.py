from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True)

    bot_token: str
    database_url: str
    webhook_host: str = ""
    webhook_path: str = "/tg/webhook"
    webhook_secret_token: str
    admin_telegram_ids: str = ""
    app_env: str = "dev"
    ngrok_authtoken: str = ""

    @property
    def admin_ids(self) -> set[int]:
        if not self.admin_telegram_ids.strip():
            return set()
        return {int(x.strip()) for x in self.admin_telegram_ids.split(",") if x.strip()}


@lru_cache
def get_settings() -> Settings:
    return Settings()
