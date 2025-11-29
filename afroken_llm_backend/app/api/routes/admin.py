"""
Admin-facing endpoints for document ingestion and indexing.
"""

from fastapi import APIRouter, UploadFile, File
from sqlalchemy import text

from app.utils.storage import upload_bytes
from app.db import engine
from app.utils.embeddings import get_embedding


# Create a router instance; it will be included in `main.py` under `/api/v1/admin`.
router = APIRouter()


@router.post("/documents/upload")
async def upload_document(file: UploadFile = File(...), source: str = "ministry"):
    """
    Ingest a document by uploading a file and indexing its content.

    Steps:
    1. Upload file bytes to MinIO and get a storage path.
    2. Decode the file to text (truncated for safety) and insert a DB row.
    3. Synchronously generate an embedding and update the same row.

    For production, you would typically offload step 3 to a Celery task instead
    of blocking the HTTP request.
    """

    # Read the entire uploaded file into memory as raw bytes.
    contents = await file.read()

    # Upload the raw bytes to MinIO under the "documents" bucket.
    path = upload_bytes(
        "documents", file.filename, contents, content_type=file.content_type
    )

    # Best-effort decode of the file contents as UTF‑8 text, ignoring invalid bytes.
    # Truncate to 10k characters to keep DB rows and prompts manageable.
    text_content = contents.decode("utf-8", errors="ignore")[:10000]

    # Open a database connection via SQLAlchemy engine.
    with engine.connect() as conn:
        # Parameterized INSERT statement to create a new document row.
        insert_q = text(
            """
            INSERT INTO documents (title, content, source_url, document_type, category, is_indexed)
            VALUES (:t, :c, :s, :d, :cat, false)
            RETURNING id
            """
        )
        # Execute the insert with the file metadata and decoded text.
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
        # Fetch the generated primary key for the new document row.
        doc_id = res.scalar()

        # Generate an embedding inline for simplicity (synchronous path).
        emb = await get_embedding(text_content)
        # Prepare an UPDATE statement to write the embedding into the row.
        update_q = text("UPDATE documents SET embedding = :e::vector WHERE id = :id")
        # Execute the update with the computed embedding.
        conn.execute(update_q, {"e": emb, "id": doc_id})
        # Commit the transaction so both insert and update are persisted.
        conn.commit()

    # Return both the database identifier and storage path to the client.
    return {"doc_id": doc_id, "path": path}
