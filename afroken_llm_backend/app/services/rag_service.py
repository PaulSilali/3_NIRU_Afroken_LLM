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
    Perform a similarity search over the `documents` table.
    
    Supports both pgvector (if available) and TEXT-based embeddings (JSON strings).

    Args:
        embedding: A numeric vector representing the query text.
        top_k: Maximum number of most similar documents to return.

    Returns:
        A list of dictionaries, each representing a matching document with
        basic fields (id, title, content, source_url).
    """
    import json
    import numpy as np

    # Prepare a Python list to collect document dictionaries.
    docs: List[Dict[str, Any]] = []

    # Open a connection from the SQLAlchemy/SQLModel engine.
    with engine.connect() as conn:
        # Try pgvector first
        try:
            query = text(
                """
                SELECT id, title, content, source_url
                FROM documents
                WHERE embedding IS NOT NULL
                ORDER BY embedding <#> :q
                LIMIT :k
                """
            )
            result = conn.execute(query, {"q": embedding, "k": top_k})
            rows = result.fetchall()
        except Exception:
            # Fallback to TEXT-based cosine similarity (JSON strings)
            # Get all documents with embeddings
            query = text(
                """
                SELECT id, title, content, source_url, embedding
                FROM documents
                WHERE embedding IS NOT NULL
                """
            )
            result = conn.execute(query)
            all_rows = result.fetchall()
            
            # Calculate cosine similarity for each document
            query_emb = np.array(embedding)
            query_norm = query_emb / (np.linalg.norm(query_emb) + 1e-8)
            
            similarities = []
            for r in all_rows:
                try:
                    # Parse JSON embedding string
                    doc_emb_json = r[4]
                    if doc_emb_json:
                        doc_emb = np.array(json.loads(doc_emb_json))
                        doc_norm = doc_emb / (np.linalg.norm(doc_emb) + 1e-8)
                        similarity = np.dot(doc_norm, query_norm)
                        similarities.append((similarity, r))
                except (json.JSONDecodeError, ValueError, TypeError):
                    continue
            
            # Sort by similarity (descending) and take top_k
            similarities.sort(key=lambda x: x[0], reverse=True)
            rows = [r for _, r in similarities[:top_k]]

    # Convert each row tuple into a dict with friendly keys.
    for r in rows:
        docs.append(
            {
                "id": str(r[0]),  # Convert UUID to string
                "title": r[1],
                "content": r[2],
                "source_url": r[3],
            }
        )

    # Return a simple Python structure ready for use in prompts or API responses.
    return docs

