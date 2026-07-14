from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Core
    SECRET_KEY: str = "dev-secret"
    ENVIRONMENT: str = "development"
    API_V1_PREFIX: str = "/api/v1"
    ACCESS_TOKEN_MINUTES: int = 30
    REFRESH_TOKEN_DAYS: int = 14

    # LLM
    LLM_PROVIDER: str = "openai"          # openai | local
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    LOCAL_LLM_BASE_URL: str = "http://localhost:11434/v1"
    LOCAL_LLM_MODEL: str = "llama3.1"

    # Embeddings / vectors
    EMBEDDINGS_PROVIDER: str = "sentence-transformers"
    EMBEDDINGS_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    VECTOR_BACKEND: str = "faiss"         # faiss | milvus
    VECTOR_DIR: str = "/data/vectors"
    MILVUS_URI: str = "http://localhost:19530"

    # Infra
    DATABASE_URL: str = "postgresql+asyncpg://aibos:aibos@localhost:5432/aibos"
    SYNC_DATABASE_URL: str = "postgresql+psycopg://aibos:aibos@localhost:5432/aibos"
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    UPLOAD_DIR: str = "/data/uploads"
    MAX_UPLOAD_MB: int = 50

    # Speech / OCR / push
    WHISPER_MODEL: str = "base"
    OCR_LANGS: str = "eng"
    FCM_CREDENTIALS_JSON: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
