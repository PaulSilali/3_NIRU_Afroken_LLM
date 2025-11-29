"""
One-off script to initialize the Postgres database for vector search.

It:
- Connects to Postgres using asyncpg.
- Ensures the `vector` extension (pgvector) is installed.
- Creates a `documents` table suitable for RAG.
- Adds an IVFFLAT index on the embedding column.
"""

import os
import asyncio
import asyncpg


# Build the Postgres connection string from the environment or fall back to a
# local development default.
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://afroken:afroken_pass@localhost:5432/afroken_db",
)


async def init() -> None:
    """
    Connect to Postgres and ensure the required extension, table, and index exist.
    """

    # Open an async connection to the configured Postgres instance.
    conn = await asyncpg.connect(DATABASE_URL)

    # Enable the pgvector extension to support `vector` column types and operators.
    await conn.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    # Create the `documents` table with an embedding column for vector search.
    await conn.execute(
        """
    CREATE TABLE IF NOT EXISTS documents (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        title TEXT,
        content TEXT,
        source_url TEXT,
        document_type TEXT,
        category TEXT,
        embedding vector(384),
        metadata JSONB DEFAULT '{}'::jsonb,
        is_indexed BOOLEAN DEFAULT false,
        created_at TIMESTAMP DEFAULT NOW()
    );
    """
    )

    # Create an IVFFLAT index on the embedding column to accelerate similarity search.
    await conn.execute(
        """
    CREATE INDEX IF NOT EXISTS idx_documents_embedding
    ON documents USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
    """
    )

    # Log a simple message to indicate success.
    print("DB init complete")

    # Always close the connection when done.
    await conn.close()


if __name__ == "__main__":
    # If invoked as a script (`python init_db.py`), run the async init function.
    asyncio.run(init())

