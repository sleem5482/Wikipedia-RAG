"""
Application settings loaded from environment variables / .env file.
All secrets live here — never hard-code them elsewhere.
"""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ── API meta ──────────────────────────────────────────────────────────────
    app_name: str = "Wikipedia RAG API"
    app_version: str = "1.0.0"
    log_level: str = "INFO"

    # ── Security / CORS ───────────────────────────────────────────────────────
    # Comma-separated list of allowed frontend origins, e.g.
    # ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
    allowed_origins: str = "http://localhost:3000,http://localhost:5173,http://localhost:8080,http://localhost:8501"

    # ── LLM ───────────────────────────────────────────────────────────────────
    groq_api_key: str = ""
    groq_model: str = "openai/gpt-oss-120b"
    llm_temperature: float = 0.0

    # ── LangSmith (optional tracing) ──────────────────────────────────────────
    langsmith_api_key: str = ""
    langsmith_tracing: str = "false"
    langsmith_project: str = "wikipedia-rag"

    # ── Vector store ──────────────────────────────────────────────────────────
    vector_store_path: str = "./data/vector_store"
    collection_name: str = "wikipedia_rag"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    retriever_k: int = 3

    # ── Pydantic-settings config ───────────────────────────────────────────────
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Derived helpers ───────────────────────────────────────────────────────
    @property
    def allowed_origins_list(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]

    @property
    def vector_store_path_resolved(self) -> Path:
        return Path(self.vector_store_path).resolve()


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance (loaded once at startup)."""
    return Settings()
