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
# - For local development, defaults to SQLite if DATABASE_URL not set or points to unavailable DB
engine = create_engine(settings.DATABASE_URL, echo=False, future=True)

# Global flag to track if database is available
_db_available = None

def is_db_available() -> bool:
    """
    Check if database connection is available.
    Caches the result to avoid repeated connection attempts.
    """
    global _db_available
    if _db_available is not None:
        return _db_available
    
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        _db_available = True
        return True
    except Exception:
        _db_available = False
        return False


def reset_db_cache():
    """Reset database availability cache (useful after fixing connection)."""
    global _db_available
    _db_available = None


def init_db() -> None:
    """
    Create all tables registered on `SQLModel.metadata` using the global engine.

    This should be called once on application startup to ensure the schema exists.
    
    For local development without a database, this will gracefully skip if connection fails.
    """
    global _db_available
    try:
        # Test connection first (SQLAlchemy 2.0 style)
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        # Issue CREATE TABLE IF NOT EXISTS statements for all SQLModel models.
        SQLModel.metadata.create_all(bind=engine)
        _db_available = True
        print("✓ Database initialized")
    except Exception as e:
        # In local development, database might not be available
        # This is OK for RAG-only mode - chat will work without database
        _db_available = False
        error_msg = str(e)
        if "postgres" in error_msg.lower() or "could not translate host" in error_msg.lower():
            print("⚠ Database not available (RAG-only mode)")
            print("  Chat functionality will work without database")
            print("  To use full features, start PostgreSQL or set DATABASE_URL=sqlite:///./afroken_local.db")
        else:
            print(f"⚠ Database initialization skipped: {e}")

