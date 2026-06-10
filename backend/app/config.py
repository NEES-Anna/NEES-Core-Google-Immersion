from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_DIR = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    gemini_api_key: str | None = None
    gemma_model: str = "gemma-4-26b-a4b-it"
    gemma_fallback_models: str = "gemma-4-31b-it"
    gemma_timeout_seconds: int = 30
    cors_origins: str = "http://localhost:5173"
    mock_gemma_when_missing_key: bool = True

    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def fallback_model_list(self) -> list[str]:
        seen = {self.gemma_model}
        models: list[str] = []
        for model in self.gemma_fallback_models.split(","):
            cleaned = model.strip()
            if cleaned and cleaned not in seen:
                models.append(cleaned)
                seen.add(cleaned)
        return models

    @property
    def live_model_candidates(self) -> list[str]:
        return [self.gemma_model, *self.fallback_model_list]


@lru_cache
def get_settings() -> Settings:
    return Settings()
