# PDF Upload - Database Storage Guide

## 📋 What Happens When You Upload a PDF

### Complete Flow:

```
1. User selects PDF file in frontend
   ↓
2. Frontend sends POST /api/v1/admin/documents/upload-pdf
   ↓
3. Backend saves PDF to: data/temp/{uuid}_{filename}.pdf
   ↓
4. Backend creates ProcessingJob record in database
   ↓
5. Background processing starts:
   ├─ Extract text from PDF
   ├─ Convert to Markdown → data/docs/{filename}.md
   ├─ Upload to MinIO (if configured) → documents/pdfs/{filename}
   ├─ Save PDF permanently → data/pdfs/{filename}
   ├─ Generate embedding (vector representation)
   ├─ Store Document record in database
   └─ Update ProcessingJob status to "completed"
   ↓
6. Frontend shows success message
```

---

## 🗄️ Database Tables

### 1. **`processingjob` Table** (Job Tracking)

**Purpose**: Tracks the upload/processing job status

**Table Name**: `processingjob` (singular, lowercase - SQLModel convention)

**What Gets Stored**:
- `id` - Unique job ID (UUID as string, VARCHAR(36))
- `job_type` - Always `"pdf_upload"` for PDF uploads (or `"url_scrape"` for URL scraping)
- `status` - `"pending"` → `"processing"` → `"completed"` or `"failed"`
- `source` - Original PDF filename or URL
- `progress` - Progress percentage (0, 10, 50, 100)
- `documents_processed` - Number of documents created (usually 1)
- `error_message` - Error details if failed (TEXT)
- `result` - JSON string with:
  ```json
  {
    "document_id": "uuid-of-document",
    "markdown_file": "path/to/markdown.md",
    "minio_path": "minio-url-if-configured",
    "pdf_path": "data/pdfs/filename.pdf"
  }
  ```
- `created_at` - When upload started (TIMESTAMP)
- `updated_at` - Last status update (TIMESTAMP)

**Indexes**:
- `idx_processingjob_status` - Fast lookup by status
- `idx_processingjob_job_type` - Fast lookup by job type
- `idx_processingjob_created_at` - Fast sorting by creation time
- `idx_processingjob_status_type` - Composite index for filtered queries

**How to Check**:
```sql
-- SQLite
SELECT * FROM processingjob WHERE job_type = 'pdf_upload' ORDER BY created_at DESC;

-- PostgreSQL
SELECT * FROM processingjob WHERE job_type = 'pdf_upload' ORDER BY created_at DESC;
```

---

### 2. **`document` Table** (Document Storage)

**Purpose**: Stores the actual document content, metadata, and embeddings for RAG search

**What Gets Stored**:
- `id` - Unique document ID (UUID)
- `title` - PDF filename (e.g., "handbook.pdf")
- `content` - Extracted text content (truncated to 50,000 chars)
- `source_url` - Path to PDF file (MinIO URL if configured, or local path)
- `document_type` - Always `"pdf"` for PDF uploads
- `category` - Category you selected (e.g., "ministry_faq", "service_workflow")
- `is_indexed` - Always `true` for uploaded PDFs
- `embedding` - Vector embedding (384 dimensions) stored as:
  - JSON string (if pgvector not available)
  - Vector type (if pgvector available)
- `created_at` - When document was created

**How to Check**:
```sql
-- SQLite
SELECT id, title, document_type, category, created_at, 
       LENGTH(content) as content_length,
       is_indexed
FROM document 
WHERE document_type = 'pdf' 
ORDER BY created_at DESC;

-- PostgreSQL
SELECT id, title, document_type, category, created_at,
       LENGTH(content) as content_length,
       is_indexed
FROM document
WHERE document_type = 'pdf'
ORDER BY created_at DESC;
```

---

## 📊 Complete Data Flow

### Step-by-Step Database Operations:

1. **Initial Upload** (Synchronous):
   ```sql
   INSERT INTO processingjob (
     id, job_type, status, source, progress, created_at, updated_at
   ) VALUES (
     'uuid', 'pdf_upload', 'pending', 'filename.pdf', 0, NOW(), NOW()
   );
   ```

2. **Processing Started** (Background):
   ```sql
   UPDATE processingjob 
   SET status = 'processing', progress = 10, updated_at = NOW()
   WHERE id = 'job_id';
   ```

3. **Text Extracted** (Background):
   ```sql
   UPDATE processingjob 
   SET progress = 50, updated_at = NOW()
   WHERE id = 'job_id';
   ```

4. **Document Created** (Background):
   ```sql
   INSERT INTO document (
     id, title, content, source_url, document_type, 
     category, is_indexed, created_at
   ) VALUES (
     'doc_uuid', 'filename.pdf', 'extracted text...', 
     'path/to/file.pdf', 'pdf', 'ministry_faq', true, NOW()
   );
   
   -- Then update embedding
   UPDATE document 
   SET embedding = '[384-dimension vector]'
   WHERE id = 'doc_uuid';
   ```

5. **Job Completed** (Background):
   ```sql
   UPDATE processingjob 
   SET status = 'completed', 
       progress = 100, 
       documents_processed = 1,
       result = '{"document_id": "...", ...}',
       updated_at = NOW()
   WHERE id = 'job_id';
   ```

---

## 🔍 How to Check Your Uploaded PDFs

### Using SQLite (Current Setup):

```bash
# Open SQLite database
cd afroken_llm_backend
sqlite3 afroken_local.db

# Check processing jobs
SELECT id, job_type, status, source, progress, created_at 
FROM processingjob 
WHERE job_type = 'pdf_upload' 
ORDER BY created_at DESC 
LIMIT 10;

# Check documents
SELECT id, title, category, document_type, 
       LENGTH(content) as content_length,
       created_at 
FROM document 
WHERE document_type = 'pdf' 
ORDER BY created_at DESC;

# Check specific job result
SELECT id, status, result 
FROM processingjob 
WHERE id = 'your-job-id-here';

# Exit SQLite
.quit
```

### Using Python Script:

```python
from app.db import engine
from sqlmodel import Session, select
from app.models import ProcessingJob, Document

with Session(engine) as session:
    # Get all PDF upload jobs
    jobs = session.exec(
        select(ProcessingJob)
        .where(ProcessingJob.job_type == "pdf_upload")
        .order_by(ProcessingJob.created_at.desc())
        .limit(10)
    ).all()
    
    for job in jobs:
        print(f"Job: {job.id}")
        print(f"  Status: {job.status}")
        print(f"  Source: {job.source}")
        print(f"  Progress: {job.progress}%")
        print(f"  Created: {job.created_at}")
        if job.result:
            import json
            result = json.loads(job.result)
            print(f"  Document ID: {result.get('document_id')}")
        print()
    
    # Get all PDF documents
    docs = session.exec(
        select(Document)
        .where(Document.document_type == "pdf")
        .order_by(Document.created_at.desc())
        .limit(10)
    ).all()
    
    print(f"\nTotal PDF Documents: {len(docs)}")
    for doc in docs:
        print(f"  - {doc.title} ({doc.category}) - {len(doc.content)} chars")
```

---

## 📁 File System Storage

In addition to database, files are stored:

1. **Temporary**: `data/temp/{uuid}_{filename}.pdf` (deleted after processing)
2. **Permanent PDF**: `data/pdfs/{filename}.pdf` (kept permanently)
3. **Markdown**: `data/docs/{filename}.md` (converted text for RAG)
4. **MinIO** (if configured): `documents/pdfs/{filename}` (cloud storage)

---

## ✅ Verification Checklist

After uploading a PDF, verify:

- [ ] **ProcessingJob created**: Check `processingjob` table
- [ ] **Job status**: Should be `"completed"` (not `"failed"`)
- [ ] **Document created**: Check `document` table
- [ ] **PDF file exists**: Check `data/pdfs/` folder
- [ ] **Markdown created**: Check `data/docs/` folder
- [ ] **Embedding stored**: Check `document.embedding` field (not NULL)
- [ ] **Content extracted**: Check `document.content` has text

---

## 🐛 Troubleshooting

### If PDF upload fails:

1. **Check ProcessingJob**:
   ```sql
   SELECT * FROM processingjob 
   WHERE status = 'failed' 
   ORDER BY created_at DESC;
   ```
   Look at `error_message` field for details.

2. **Check if document was created**:
   ```sql
   SELECT * FROM document 
   WHERE document_type = 'pdf' 
   ORDER BY created_at DESC;
   ```

3. **Check file system**:
   - `data/temp/` - Should be empty (temp files cleaned up)
   - `data/pdfs/` - Should have your PDF
   - `data/docs/` - Should have markdown file

---

## 📝 Summary

**Two main tables store PDF upload data:**

1. **`processingjob`** - Tracks the upload job (status, progress, errors)
2. **`document`** - Stores the actual document (content, embedding, metadata)

**Quick Check Commands:**
```sql
-- See all PDF upload jobs
SELECT * FROM processingjob WHERE job_type = 'pdf_upload';

-- See all PDF documents
SELECT * FROM document WHERE document_type = 'pdf';
```

