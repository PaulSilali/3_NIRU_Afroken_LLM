# Implementation Guide: Complete System Features

## Overview

This document describes the complete implementation of all requested features:
1. LLM Integration (Fine-tuned Mistral/LLaMA-3)
2. Whisper ASR + Coqui TTS
3. PostgreSQL Integration
4. MinIO Integration
5. Admin Panel with PDF Upload, URL Scraping, and Reports

## 1. LLM Integration

### Configuration

Set environment variables:
```bash
# For fine-tuned model (Mistral/LLaMA-3)
FINE_TUNED_LLM_ENDPOINT=http://your-model-server:8000/v1/chat/completions

# Or fallback to generic LLM
LLM_ENDPOINT=http://your-llm-server:8000/generate
```

### Usage

The chat endpoint (`/api/v1/chat/messages`) automatically:
1. Retrieves relevant documents using RAG (PostgreSQL or FAISS)
2. Calls fine-tuned LLM service with context
3. Returns generated response with citations

### Files
- `app/services/llm_service.py` - LLM service wrapper
- `app/api/routes/chat.py` - Updated to use LLM service

## 2. Whisper ASR + Coqui TTS

### Endpoints

#### Transcribe Audio
```bash
POST /api/v1/audio/transcribe
Content-Type: multipart/form-data

file: <audio_file> (WAV, MP3, M4A, etc.)
language: "sw" (optional, auto-detects if not provided)
```

Response:
```json
{
  "text": "Transcribed text...",
  "language": "sw",
  "segments": [
    {"start": 0.0, "end": 2.5, "text": "First segment"},
    ...
  ]
}
```

#### Synthesize Speech
```bash
POST /api/v1/audio/synthesize
Content-Type: application/json

{
  "text": "Text to convert to speech",
  "language": "sw",
  "output_format": "wav"
}
```

Response: Audio file (WAV or MP3)

### Files
- `app/utils/audio.py` - Audio processing utilities
- `app/api/routes/audio.py` - Audio endpoints

## 3. PostgreSQL Integration

### Database Schema

Tables:
- `user` - User accounts
- `conversation` - Chat conversations
- `message` - Individual messages
- `document` - Documents with pgvector embeddings
- `processingjob` - Processing job tracking

### Vector Search

PostgreSQL with pgvector is used for:
- Storing document embeddings
- Similarity search using cosine distance
- Fast retrieval for RAG

### Configuration

```bash
DATABASE_URL=postgresql://user:pass@localhost:5432/afroken_db
```

### Files
- `app/models.py` - Database models
- `app/services/rag_service.py` - Vector search service
- `app/db.py` - Database initialization

## 4. MinIO Integration

### Configuration

```bash
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_SECURE=false
```

### Usage

MinIO is used for:
- Storing uploaded PDFs
- Storing scraped HTML files
- Archiving audio interactions (future)

### Files
- `app/utils/storage.py` - MinIO utilities
- `app/api/routes/admin.py` - Uses MinIO for document storage

## 5. Admin Panel Features

### PDF Upload

```bash
POST /api/v1/admin/documents/upload-pdf
Content-Type: multipart/form-data

file: <pdf_file>
category: "ministry_faq" (optional)
```

Response:
```json
{
  "job_id": "uuid",
  "status": "pending",
  "message": "PDF upload started. Check job status for progress."
}
```

**Process:**
1. PDF saved to temporary location
2. Text extracted from PDF
3. Converted to Markdown with YAML front-matter
4. Uploaded to MinIO
5. Stored in PostgreSQL with embedding
6. Processing job tracked

### URL Scraping

```bash
POST /api/v1/admin/documents/scrape-url
Content-Type: application/json

{
  "url": "https://www.nhif.or.ke/services",
  "category": "ministry_faq" (optional)
}
```

Response:
```json
{
  "job_id": "uuid",
  "status": "pending",
  "message": "URL scraping started. Check job status for progress."
}
```

**Process:**
1. Checks robots.txt compliance
2. Fetches HTML content
3. Extracts text and creates Markdown chunks
4. Uploads HTML to MinIO
5. Stores chunks in PostgreSQL with embeddings
6. Processing job tracked

### Job Status

```bash
GET /api/v1/admin/jobs/{job_id}
```

Response:
```json
{
  "job_id": "uuid",
  "job_type": "pdf_upload",
  "status": "completed",
  "progress": 100,
  "source": "handbook.pdf",
  "documents_processed": 1,
  "error_message": null,
  "result": {
    "document_id": "uuid",
    "markdown_file": "path/to/file.md",
    "minio_path": "http://minio/documents/pdfs/handbook.pdf"
  },
  "created_at": "2025-01-29T10:00:00",
  "updated_at": "2025-01-29T10:05:00"
}
```

### Processing Reports

```bash
GET /api/v1/admin/jobs?status=completed&job_type=pdf_upload&limit=50
```

Response:
```json
{
  "total_jobs": 100,
  "completed_jobs": 85,
  "failed_jobs": 5,
  "pending_jobs": 10,
  "jobs": [
    {
      "job_id": "uuid",
      "job_type": "pdf_upload",
      "status": "completed",
      ...
    },
    ...
  ]
}
```

### Files
- `app/api/routes/admin.py` - Admin endpoints
- `app/models.py` - ProcessingJob model
- `app/schemas.py` - Request/response schemas

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

New dependencies added:
- `openai-whisper` - Speech-to-text
- `TTS` - Text-to-speech (Coqui)
- `torch` - PyTorch for ML models
- `transformers` - Hugging Face transformers

### 2. Setup PostgreSQL

```bash
# Install pgvector extension
psql -d afroken_db -c "CREATE EXTENSION IF NOT EXISTS vector;"

# Run initialization script
python scripts/db/init_db.py
```

### 3. Setup MinIO (Optional)

```bash
# Using Docker
docker run -d \
  -p 9000:9000 \
  -p 9001:9001 \
  -e MINIO_ROOT_USER=minioadmin \
  -e MINIO_ROOT_PASSWORD=minioadmin \
  minio/minio server /data --console-address ":9001"
```

### 4. Configure Environment

Create `.env` file:
```bash
DATABASE_URL=postgresql://user:pass@localhost:5432/afroken_db
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
FINE_TUNED_LLM_ENDPOINT=http://your-model-server:8000/v1/chat/completions
```

## Testing

### Test Audio Transcription
```bash
curl -X POST http://localhost:8000/api/v1/audio/transcribe \
  -F "file=@audio.wav" \
  -F "language=sw"
```

### Test PDF Upload
```bash
curl -X POST http://localhost:8000/api/v1/admin/documents/upload-pdf \
  -F "file=@handbook.pdf" \
  -F "category=ministry_faq"
```

### Test URL Scraping
```bash
curl -X POST http://localhost:8000/api/v1/admin/documents/scrape-url \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.nhif.or.ke/services", "category": "ministry_faq"}'
```

### Check Job Status
```bash
curl http://localhost:8000/api/v1/admin/jobs/{job_id}
```

## Architecture Flow

### PDF Upload Flow
```
Admin Panel → POST /upload-pdf
  → Save to temp location
  → Background task starts
  → Extract text from PDF
  → Create Markdown file
  → Upload to MinIO
  → Store in PostgreSQL with embedding
  → Update job status
  → Return job_id
```

### URL Scraping Flow
```
Admin Panel → POST /scrape-url
  → Create processing job
  → Background task starts
  → Check robots.txt
  → Fetch HTML
  → Extract text
  → Chunk into Markdown files
  → Upload HTML to MinIO
  → Store chunks in PostgreSQL with embeddings
  → Update job status
  → Return job_id
```

### Chat Flow
```
User → POST /chat/messages
  → Get query embedding
  → Search PostgreSQL (pgvector) or FAISS
  → Retrieve top-k documents
  → Call fine-tuned LLM with context
  → Generate response
  → Return with citations
```

## Notes

- All processing jobs run in background tasks (non-blocking)
- PostgreSQL is optional (falls back to FAISS if unavailable)
- MinIO is optional (uses local files if unavailable)
- LLM is optional (returns document excerpts if unavailable)
- Audio processing requires GPU for best performance (CPU works but slower)

