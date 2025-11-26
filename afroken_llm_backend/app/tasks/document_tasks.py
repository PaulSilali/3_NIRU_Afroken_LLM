from sqlalchemy import text

from app.tasks.celery_app import celery
from app.utils.embeddings import get_embedding
from app.db import engine


@celery.task(bind=True)
def index_document(self, doc_id: str, content: str):
    """
    Celery task to generate an embedding for a document and persist it.

    Wraps the async embedding call in asyncio.run for simplicity.
    """
    import asyncio

    emb = asyncio.run(get_embedding(content))
    with engine.connect() as conn:
        query = text("UPDATE documents SET embedding = :e::vector WHERE id = :id")
        conn.execute(query, {"e": emb, "id": doc_id})
        conn.commit()
    return {"doc_id": doc_id, "indexed": True}



