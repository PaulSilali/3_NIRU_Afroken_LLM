"""
Database utilities and engine creation.

This module defines a global SQLModel engine and a simple `init_db` helper
that creates all tables declared on the `SQLModel` metadata.
"""

from sqlmodel import SQLModel, create_engine
from app.config import settings


# Create a synchronous SQLModel/SQLAlchemy engine using the configured DATABASE_URL.
# - `echo=False` keeps SQL logging quiet (set to True when debugging queries).
# - `future=True` enables SQLAlchemy 2.0 style behaviour.
engine = create_engine(settings.DATABASE_URL, echo=False, future=True)


def init_db() -> None:
    """
    Create all tables registered on `SQLModel.metadata` using the global engine.

    This should be called once on application startup to ensure the schema exists.
    """

    # Issue CREATE TABLE IF NOT EXISTS statements for all SQLModel models.
    SQLModel.metadata.create_all(bind=engine)

