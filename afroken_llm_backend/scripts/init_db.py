import os
import asyncio
import asyncpg


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://afroken:afroken_pass@localhost:5432/afroken_db",
)


async def init() -> None:
    conn = await asyncpg.connect(DATABASE_URL)
    # Enable pgvector extension
    await conn.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    # Create documents table with embedding column
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
    # Create ivfflat index on embedding
    await conn.execute(
        """
    CREATE INDEX IF NOT EXISTS idx_documents_embedding
    ON documents USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
    """
    )
    print("DB init complete")
    await conn.close()


if __name__ == "__main__":
    asyncio.run(init())


