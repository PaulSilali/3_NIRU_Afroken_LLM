"""
Celery tasks related to document indexing and embeddings.
"""

from sqlalchemy import text

from app.tasks.celery_app import celery
from app.utils.embeddings import get_embedding
from app.db import engine


@celery.task(bind=True)
def index_document(self, doc_id: str, content: str):
    """
    Background task to generate and store an embedding for a document.

    Args:
        self: The task instance (because `bind=True`).
        doc_id: ID of the target document row in the `documents` table.
        content: Text content of the document to embed.

    This wraps the async `get_embedding` call in `asyncio.run` so that it can
    be used from within a synchronous Celery worker process.
    """

    import asyncio

    # Execute the async embedding function to obtain a vector for the content.
    emb = asyncio.run(get_embedding(content))

    # Open a DB connection through the shared SQLAlchemy engine.
    with engine.connect() as conn:
        # Prepare an UPDATE query that writes the embedding into the `embedding` column.
        query = text("UPDATE documents SET embedding = :e::vector WHERE id = :id")
        # Execute the update with the computed embedding and document id.
        conn.execute(query, {"e": emb, "id": doc_id})
        # Explicitly commit the transaction so changes are persisted.
        conn.commit()

    # Return a small status payload that Celery can store as the task result.
    return {"doc_id": doc_id, "indexed": True}

