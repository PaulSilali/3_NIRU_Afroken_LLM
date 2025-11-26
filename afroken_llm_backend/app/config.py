from pydantic import BaseSettings, Field
from typing import Optional


class Settings(BaseSettings):
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    REDIS_URL: str = Field(..., env="REDIS_URL")
    MINIO_ENDPOINT: str = Field(..., env="MINIO_ENDPOINT")
    MINIO_ACCESS_KEY: str = Field(..., env="MINIO_ACCESS_KEY")
    MINIO_SECRET_KEY: str = Field(..., env="MINIO_SECRET_KEY")
    MINIO_SECURE: bool = Field(False, env="MINIO_SECURE")

    JWT_SECRET: str = Field(..., env="JWT_SECRET")
    JWT_ALGORITHM: str = Field("HS256", env="JWT_ALGORITHM")
    ACCESS_TOKEN_EXPIRES_MIN: int = Field(60, env="ACCESS_TOKEN_EXPIRES_MIN")

    LLM_ENDPOINT: Optional[str] = Field(None, env="LLM_ENDPOINT")
    EMBEDDING_ENDPOINT: Optional[str] = Field(None, env="EMBEDDING_ENDPOINT")
    EMBEDDING_DIM: int = Field(384, env="EMBEDDING_DIM")

    ENV: str = Field("development", env="ENV")

    class Config:
        env_file = ".env"


settings = Settings()


