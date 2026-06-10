from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_DIR = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    gemini_api_key: str | None = None
    model_provider: str = "gemini"
    model_name: str | None = None
    gemini_model: str | None = None
    model_timeout_seconds: int | None = None
    mock_model_when_missing_key: bool | None = None
    gemma_model: str = "gemini-1.5-flash"
    gemma_fallback_models: str = "gemini-1.5-flash"
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
    def configured_model(self) -> str:
        for model in (self.model_name, self.gemini_model, self.gemma_model):
            if model and model.strip():
                return model.strip()
        return "gemini-1.5-flash"

    @property
    def configured_timeout_seconds(self) -> int:
        return self.model_timeout_seconds or self.gemma_timeout_seconds

    @property
    def mock_when_missing_key(self) -> bool:
        if self.mock_model_when_missing_key is not None:
            return self.mock_model_when_missing_key
        return self.mock_gemma_when_missing_key

    @property
    def fallback_model_list(self) -> list[str]:
        seen = {self.configured_model}
        models: list[str] = []
        for model in self.gemma_fallback_models.split(","):
            cleaned = model.strip()
            if cleaned and cleaned not in seen:
                models.append(cleaned)
                seen.add(cleaned)
        return models

    @property
    def live_model_candidates(self) -> list[str]:
        return [self.configured_model, *self.fallback_model_list]


@lru_cache
def get_settings() -> Settings:
    return Settings()
