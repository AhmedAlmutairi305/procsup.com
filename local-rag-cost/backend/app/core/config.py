from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    anthropic_api_key: str | None = None
    openai_api_key: str | None = None
    google_api_key: str | None = None
    ollama_base_url: str = "http://localhost:11434"
    llamacpp_base_url: str = "http://localhost:8001/v1"
    data_dir: Path = Path("data")

    @property
    def observability_db(self) -> Path:
        return self.data_dir / "observability.duckdb"

    @property
    def pricing_config(self) -> Path:
        return Path("configs/pricing.yaml")


settings = Settings()
