"""
Retrieval-Augmented Generation (RAG) service helpers.

Currently exposes a single `vector_search` function that queries a Postgres
`documents` table using pgvector similarity.
"""

from typing import List, Dict, Any

from sqlalchemy import text

from app.db import engine


def vector_search(embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Perform a pgvector similarity search over the `documents` table.

    Args:
        embedding: A numeric vector representing the query text.
        top_k: Maximum number of most similar documents to return.

    Returns:
        A list of dictionaries, each representing a matching document with
        basic fields (id, title, content, source_url).

    NOTE: For production, configure a proper pgvector adapter for your driver.
    Some drivers accept a Python list directly; adjust binding if needed.
    """

    # SQL with pgvector `<#>` operator for cosine distance (or similar metric).
    query = text(
        """
        SELECT id, title, content, source_url
        FROM documents
        ORDER BY embedding <#> :q
        LIMIT :k
        """
    )

    # Prepare a Python list to collect document dictionaries.
    docs: List[Dict[str, Any]] = []

    # Open a connection from the SQLAlchemy/SQLModel engine.
    with engine.connect() as conn:
        # Execute the parameterized query, binding our embedding and top_k limit.
        result = conn.execute(query, {"q": embedding, "k": top_k})
        # Pull all matching rows into memory (small top_k keeps this safe).
        rows = result.fetchall()

    # Convert each row tuple into a dict with friendly keys.
    for r in rows:
        docs.append(
            {
                "id": r[0],
                "title": r[1],
                "content": r[2],
                "source_url": r[3],
            }
        )

    # Return a simple Python structure ready for use in prompts or API responses.
    return docs

