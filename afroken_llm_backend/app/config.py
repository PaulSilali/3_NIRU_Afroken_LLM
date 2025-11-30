"""
Application configuration using Pydantic settings.

Each attribute on the `Settings` class maps to an environment variable.
When the app starts, `settings = Settings()` reads from the OS env (and `.env` file)
and makes these values available as `settings.DATABASE_URL`, `settings.REDIS_URL`, etc.
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """
    Central configuration object for the backend.

    - The `Field(..., env="VAR_NAME")` pattern means:
      * Read the value from the environment variable `VAR_NAME`.
      * If `...` is used as the default, it's required and must be provided.
      * Otherwise, the value after the comma is the default if the env var is missing.
    """

    # Full SQLAlchemy / SQLModel database connection string, e.g.
    # "postgresql+psycopg2://user:pass@host:port/dbname"
    # For local development without DB, defaults to SQLite in-memory
    DATABASE_URL: Optional[str] = Field(
        "sqlite:///./afroken_local.db", 
        env="DATABASE_URL"
    )

    # Redis connection URL used for Celery broker & backend, caching, etc.
    # Optional for local RAG-only mode
    REDIS_URL: Optional[str] = Field(None, env="REDIS_URL")

    # MinIO/S3-compatible object storage endpoint (host:port or full URL).
    # Optional for local RAG-only mode
    MINIO_ENDPOINT: Optional[str] = Field(None, env="MINIO_ENDPOINT")
    # Access key (akin to a username) for MinIO.
    MINIO_ACCESS_KEY: Optional[str] = Field(None, env="MINIO_ACCESS_KEY")
    # Secret key (akin to a password) for MinIO.
    MINIO_SECRET_KEY: Optional[str] = Field(None, env="MINIO_SECRET_KEY")
    # Whether to connect to MinIO using HTTPS (`True`) or HTTP (`False` by default).
    MINIO_SECURE: bool = Field(False, env="MINIO_SECURE")

    # Secret key used to sign JWT tokens. Keep this safe and never commit the real value.
    # Optional for local RAG-only mode (uses a default dev key)
    JWT_SECRET: str = Field("dev-secret-key-change-in-production", env="JWT_SECRET")
    # Algorithm used by `python-jose` to sign/verify JWTs (HS256 symmetric by default).
    JWT_ALGORITHM: str = Field("HS256", env="JWT_ALGORITHM")
    # Default access token lifetime in minutes if a custom `expires_delta` is not provided.
    ACCESS_TOKEN_EXPIRES_MIN: int = Field(60, env="ACCESS_TOKEN_EXPIRES_MIN")

    # Optional HTTP endpoint for a hosted LLM that will power AfroKen's answers.
    LLM_ENDPOINT: Optional[str] = Field(None, env="LLM_ENDPOINT")
    # Optional HTTP endpoint for fine-tuned Mistral/LLaMA-3 model.
    FINE_TUNED_LLM_ENDPOINT: Optional[str] = Field(None, env="FINE_TUNED_LLM_ENDPOINT")
    # Optional HTTP endpoint providing embeddings (if not set, we fall back to a demo embedding).
    EMBEDDING_ENDPOINT: Optional[str] = Field(None, env="EMBEDDING_ENDPOINT")
    # Dimensionality of embedding vectors expected by the database / vector index.
    EMBEDDING_DIM: int = Field(384, env="EMBEDDING_DIM")

    # Environment name, used to toggle behaviours like CORS (e.g. "development", "production").
    ENV: str = Field("development", env="ENV")

    model_config = SettingsConfigDict(
        # Name of the file containing key=value pairs, loaded in addition to OS env vars.
        env_file=".env",
        # Ignore extra environment variables that aren't defined in the model
        extra="ignore"
    )


# Instantiate a global settings object that will be imported and reused across the app.
settings = Settings()
