"""
Application configuration using Pydantic settings.

Each attribute on the `Settings` class maps to an environment variable.
When the app starts, `settings = Settings()` reads from the OS env (and `.env` file)
and makes these values available as `settings.DATABASE_URL`, `settings.REDIS_URL`, etc.
"""

from pydantic import BaseSettings, Field
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
    DATABASE_URL: str = Field(..., env="DATABASE_URL")

    # Redis connection URL used for Celery broker & backend, caching, etc.
    REDIS_URL: str = Field(..., env="REDIS_URL")

    # MinIO/S3-compatible object storage endpoint (host:port or full URL).
    MINIO_ENDPOINT: str = Field(..., env="MINIO_ENDPOINT")
    # Access key (akin to a username) for MinIO.
    MINIO_ACCESS_KEY: str = Field(..., env="MINIO_ACCESS_KEY")
    # Secret key (akin to a password) for MinIO.
    MINIO_SECRET_KEY: str = Field(..., env="MINIO_SECRET_KEY")
    # Whether to connect to MinIO using HTTPS (`True`) or HTTP (`False` by default).
    MINIO_SECURE: bool = Field(False, env="MINIO_SECURE")

    # Secret key used to sign JWT tokens. Keep this safe and never commit the real value.
    JWT_SECRET: str = Field(..., env="JWT_SECRET")
    # Algorithm used by `python-jose` to sign/verify JWTs (HS256 symmetric by default).
    JWT_ALGORITHM: str = Field("HS256", env="JWT_ALGORITHM")
    # Default access token lifetime in minutes if a custom `expires_delta` is not provided.
    ACCESS_TOKEN_EXPIRES_MIN: int = Field(60, env="ACCESS_TOKEN_EXPIRES_MIN")

    # Optional HTTP endpoint for a hosted LLM that will power AfroKen's answers.
    LLM_ENDPOINT: Optional[str] = Field(None, env="LLM_ENDPOINT")
    # Optional HTTP endpoint providing embeddings (if not set, we fall back to a demo embedding).
    EMBEDDING_ENDPOINT: Optional[str] = Field(None, env="EMBEDDING_ENDPOINT")
    # Dimensionality of embedding vectors expected by the database / vector index.
    EMBEDDING_DIM: int = Field(384, env="EMBEDDING_DIM")

    # Environment name, used to toggle behaviours like CORS (e.g. "development", "production").
    ENV: str = Field("development", env="ENV")

    class Config:
        """
        Extra configuration for Pydantic `BaseSettings`:
        - `env_file` tells Pydantic to also read values from a `.env` file if present.
        """

        # Name of the file containing key=value pairs, loaded in addition to OS env vars.
        env_file = ".env"


# Instantiate a global settings object that will be imported and reused across the app.
settings = Settings()
