from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "China University Application Agent"
    app_env: str = "development"
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    database_url: str = "sqlite:///./data/app.db"
    log_level: str = "INFO"
    data_dir: str = "./data"
    upload_dir: str = "./data/uploads"
    screenshot_dir: str = "./data/screenshots"
    dry_run: bool = True
    playwright_headless: bool = False
    automation_timeout_ms: int = 15000

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    def ensure_dirs(self) -> None:
        for path in [self.data_dir, self.upload_dir, self.screenshot_dir, f"{self.data_dir}/logs"]:
            Path(path).mkdir(parents=True, exist_ok=True)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    settings = Settings()
    settings.ensure_dirs()
    return settings
