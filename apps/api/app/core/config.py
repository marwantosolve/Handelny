"""Application settings, loaded from environment variables / .env."""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    environment: str = "development"

    # Postgres
    database_url: str = "postgresql+asyncpg://handelny:handelny@localhost:5432/handelny"

    # Redis (reserved for v2 Celery migration; unused by v1's BackgroundTasks ingestion)
    redis_url: str = "redis://localhost:6379/0"

    # Qdrant
    qdrant_url: str = "http://localhost:6333"

    # MinIO / S3-compatible storage
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket: str = "handelny-documents"
    minio_secure: bool = False

    # Auth
    jwt_secret: str = "change-me"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440

    # CORS
    cors_origins: str = "http://localhost:3000"

    # LLM (Google AI Studio / Gemini API)
    google_ai_studio_api_key: str = ""
    google_ai_model: str = "gemini-2.0-flash"

    # RAG pipeline
    embedding_model: str = "intfloat/multilingual-e5-large"
    chunk_size_tokens: int = 512
    chunk_overlap_tokens: int = 64
    retrieval_top_k: int = 5

    # Uploads
    max_upload_mb: int = 25
    allowed_file_types: tuple[str, ...] = ("pdf", "txt", "md")

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
