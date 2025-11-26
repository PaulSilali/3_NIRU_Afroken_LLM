from fastapi import APIRouter, UploadFile, File
from sqlalchemy import text

from app.utils.storage import upload_bytes
from app.db import engine
from app.utils.embeddings import get_embedding


router = APIRouter()


@router.post("/documents/upload")
async def upload_document(file: UploadFile = File(...), source: str = "ministry"):
    """
    Ingest a document:
    - upload to MinIO
    - store the text content in Postgres
    - synchronously generate an embedding and store it (hackathon-friendly)
      (for prod, push embedding to a Celery task instead)
    """
    contents = await file.read()
    path = upload_bytes(
        "documents", file.filename, contents, content_type=file.content_type
    )

    text_content = contents.decode("utf-8", errors="ignore")[:10000]

    with engine.connect() as conn:
        insert_q = text(
            """
            INSERT INTO documents (title, content, source_url, document_type, category, is_indexed)
            VALUES (:t, :c, :s, :d, :cat, false)
            RETURNING id
            """
        )
        res = conn.execute(
            insert_q,
            {
                "t": file.filename,
                "c": text_content,
                "s": path,
                "d": None,
                "cat": None,
            },
        )
        doc_id = res.scalar()

        # Generate embedding inline for simplicity
        emb = await get_embedding(text_content)
        update_q = text("UPDATE documents SET embedding = :e::vector WHERE id = :id")
        conn.execute(update_q, {"e": emb, "id": doc_id})
        conn.commit()

    return {"doc_id": doc_id, "path": path}



