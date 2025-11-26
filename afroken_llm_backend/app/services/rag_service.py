from typing import List, Dict, Any

from sqlalchemy import text

from app.db import engine


def vector_search(embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Perform a pgvector similarity search over the documents table.

    NOTE: For production, configure a proper pgvector adapter for your driver.
    Some drivers accept a Python list directly; adjust binding if needed.
    """
    query = text(
        """
        SELECT id, title, content, source_url
        FROM documents
        ORDER BY embedding <#> :q
        LIMIT :k
        """
    )
    docs: List[Dict[str, Any]] = []
    with engine.connect() as conn:
        result = conn.execute(query, {"q": embedding, "k": top_k})
        rows = result.fetchall()

    for r in rows:
        docs.append(
            {"id": r[0], "title": r[1], "content": r[2], "source_url": r[3]}
        )
    return docs



