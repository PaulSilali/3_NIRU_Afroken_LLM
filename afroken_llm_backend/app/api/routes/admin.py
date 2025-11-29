"""
Admin-facing endpoints for document ingestion, URL scraping, and processing reports.
"""

import os
import json
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Optional
import uuid

from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from sqlalchemy import text
from sqlmodel import Session, select

from app.utils.storage import upload_bytes, ensure_bucket
from app.db import engine
from app.utils.embeddings import get_embedding
from app.models import ProcessingJob, Document
from app.schemas import (
    URLScrapeRequest, ProcessingJobResponse, ProcessingReportResponse
)

# Import PDF processing
import sys
backend_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(backend_dir))
try:
    from scripts.rag.pdf_to_markdown import extract_text_from_pdf, create_markdown_from_pdf
    from scripts.rag.fetch_and_extract import fetch_url, extract_text, check_robots_allowed
    from scripts.rag.chunk_and_write_md import chunk_text, write_markdown_chunk, detect_category
except ImportError as e:
    print(f"Warning: Could not import RAG scripts: {e}")
    # Define fallback functions
    def extract_text_from_pdf(path):
        raise NotImplementedError("PDF processing not available")
    def create_markdown_from_pdf(*args, **kwargs):
        raise NotImplementedError("PDF processing not available")
    def fetch_url(url):
        raise NotImplementedError("URL fetching not available")
    def extract_text(html, url):
        raise NotImplementedError("Text extraction not available")
    def check_robots_allowed(url):
        return True
    def chunk_text(text, chunk_size=200):
        return [text]
    def write_markdown_chunk(*args, **kwargs):
        return None
    def detect_category(text):
        return "scraped"

router = APIRouter()


async def process_pdf_background(
    job_id: str,
    file_path: Path,
    filename: str,
    category: Optional[str] = None
):
    """Background task to process uploaded PDF."""
    try:
        # Update job status
        with Session(engine) as session:
            job = session.get(ProcessingJob, job_id)
            if job:
                job.status = "processing"
                job.progress = 10
                session.add(job)
                session.commit()
        
        # Extract text from PDF
        text_content = extract_text_from_pdf(file_path)
        
        # Update progress
        with Session(engine) as session:
            job = session.get(ProcessingJob, job_id)
            if job:
                job.progress = 50
                session.add(job)
                session.commit()
        
        # Upload to MinIO
        minio_path = None
        if os.getenv("MINIO_ENDPOINT"):
            try:
                with open(file_path, 'rb') as f:
                    file_data = f.read()
                minio_path = upload_bytes(
                    "documents",
                    f"pdfs/{filename}",
                    file_data,
                    content_type="application/pdf"
                )
            except Exception as e:
                print(f"Warning: MinIO upload failed: {e}")
        
        # Save to data/docs/ as Markdown
        docs_dir = backend_dir / 'data' / 'docs'
        docs_dir.mkdir(parents=True, exist_ok=True)
        
        # Create markdown file
        try:
            md_filename = create_markdown_from_pdf(
                pdf_path=file_path,
                output_dir=docs_dir,
                title=None,  # Auto-generate from filename
                category=category,
                source=f"PDF Upload: {filename}",
                tags=None
            )
        except Exception as e:
            print(f"Warning: Markdown creation failed: {e}")
            md_filename = None
        
        # Store in PostgreSQL with embedding
        with Session(engine) as session:
            # Generate embedding
            emb = asyncio.run(get_embedding(text_content[:10000]))  # Truncate for embedding
            
            # Create document record
            doc = Document(
                title=filename,
                content=text_content[:50000],  # Truncate for DB
                source_url=minio_path or str(file_path),
                document_type="pdf",
                category=category,
                is_indexed=True
            )
            session.add(doc)
            session.commit()
            
            # Update embedding using raw SQL (pgvector)
            if "postgresql" in str(engine.url):
                update_q = text(
                    "UPDATE document SET embedding = :e::vector WHERE id = :id"
                )
                session.execute(update_q, {"e": emb, "id": doc.id})
                session.commit()
        
        # Update job as completed
        with Session(engine) as session:
            job = session.get(ProcessingJob, job_id)
            if job:
                job.status = "completed"
                job.progress = 100
                job.documents_processed = 1
                job.result = json.dumps({
                    "document_id": doc.id,
                    "markdown_file": str(md_filename),
                    "minio_path": minio_path
                })
                session.add(job)
                session.commit()
        
        # Clean up temp file
        if file_path.exists():
            file_path.unlink()
            
    except Exception as e:
        # Mark job as failed
        with Session(engine) as session:
            job = session.get(ProcessingJob, job_id)
            if job:
                job.status = "failed"
                job.error_message = str(e)
                session.add(job)
                session.commit()


async def scrape_url_background(
    job_id: str,
    url: str,
    category: Optional[str] = None
):
    """Background task to scrape URL."""
    try:
        # Update job status
        with Session(engine) as session:
            job = session.get(ProcessingJob, job_id)
            if job:
                job.status = "processing"
                job.progress = 10
                session.add(job)
                session.commit()
        
        # Check robots.txt
        if not check_robots_allowed(url):
            raise Exception(f"URL {url} is disallowed by robots.txt")
        
        # Fetch URL
        result = fetch_url(url)
        if not result:
            raise Exception(f"Failed to fetch URL: {url}")
        
        html_content, title = result
        
        # Extract text
        title, text_content = extract_text(html_content, url)
        
        # Update progress
        with Session(engine) as session:
            job = session.get(ProcessingJob, job_id)
            if job:
                job.progress = 50
                session.add(job)
                session.commit()
        
        # Save raw HTML to MinIO
        minio_path = None
        if os.getenv("MINIO_ENDPOINT"):
            try:
                html_bytes = html_content.encode('utf-8')
                minio_path = upload_bytes(
                    "documents",
                    f"scraped/{url.replace('https://', '').replace('http://', '').replace('/', '_')}.html",
                    html_bytes,
                    content_type="text/html"
                )
            except Exception as e:
                print(f"Warning: MinIO upload failed: {e}")
        
        # Save to data/docs/ as Markdown
        docs_dir = backend_dir / 'data' / 'docs'
        docs_dir.mkdir(parents=True, exist_ok=True)
        
        # Chunk text and create markdown files
        chunks = chunk_text(text_content, chunk_size=200)
        md_files = []
        
        # Auto-detect category if not provided
        detected_category = category or detect_category(url, title, text_content)
        
        # Extract tags
        from scripts.rag.chunk_and_write_md import extract_tags, slugify, sanitize_title
        tags = extract_tags(text_content, url)
        
        for i, chunk_text_content in enumerate(chunks):
            # Generate filename
            base_slug = slugify(title)
            if len(chunks) > 1:
                filename = f"{base_slug}_chunk{i+1}.md"
                chunk_title = f"{sanitize_title(title)} (Part {i+1})"
            else:
                filename = f"{base_slug}.md"
                chunk_title = sanitize_title(title)
            
            # Create markdown file
            md_file = docs_dir / filename
            with open(md_file, 'w', encoding='utf-8') as f:
                # YAML front-matter
                f.write("---\n")
                f.write(f'title: "{chunk_title}"\n')
                f.write(f'filename: "{filename}"\n')
                f.write(f'category: "{detected_category}"\n')
                f.write('jurisdiction: "Kenya"\n')
                f.write('lang: "en"\n')
                f.write(f'source: "{url}"\n')
                f.write(f'last_updated: "{datetime.now().strftime("%Y-%m-%d")}"\n')
                f.write(f'tags: {json.dumps(tags)}\n')
                f.write("---\n\n")
                
                # Content
                f.write(chunk_text_content)
                f.write("\n\nSources:\n")
                f.write(f"- {url}\n")
            
            md_files.append(md_file)
        
        # Store in PostgreSQL with embeddings
        doc_ids = []
        for md_file in md_files:
            with Session(engine) as session:
                # Read markdown content
                with open(md_file, 'r', encoding='utf-8') as f:
                    md_content = f.read()
                
                # Extract content (skip YAML front-matter)
                content_start = md_content.find('---', 3) + 3
                content_text = md_content[content_start:].strip()
                
                # Generate embedding
                emb = asyncio.run(get_embedding(content_text[:10000]))
                
                # Create document record
                doc = Document(
                    title=title,
                    content=content_text[:50000],
                    source_url=url,
                    document_type="html",
                    category=category or "scraped",
                    is_indexed=True
                )
                session.add(doc)
                session.commit()
                
                # Update embedding
                if "postgresql" in str(engine.url):
                    update_q = text(
                        "UPDATE document SET embedding = :e::vector WHERE id = :id"
                    )
                    session.execute(update_q, {"e": emb, "id": doc.id})
                    session.commit()
                
                doc_ids.append(doc.id)
        
        # Update job as completed
        with Session(engine) as session:
            job = session.get(ProcessingJob, job_id)
            if job:
                job.status = "completed"
                job.progress = 100
                job.documents_processed = len(doc_ids)
                job.result = json.dumps({
                    "document_ids": doc_ids,
                    "markdown_files": [str(f) for f in md_files],
                    "minio_path": minio_path
                })
                session.add(job)
                session.commit()
                
    except Exception as e:
        # Mark job as failed
        with Session(engine) as session:
            job = session.get(ProcessingJob, job_id)
            if job:
                job.status = "failed"
                job.error_message = str(e)
                session.add(job)
                session.commit()


@router.post("/documents/upload-pdf")
async def upload_pdf(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    category: Optional[str] = None
):
    """
    Upload and process a PDF file.
    
    Steps:
    1. Save PDF to temporary location
    2. Extract text and convert to Markdown
    3. Upload to MinIO
    4. Store in PostgreSQL with embedding
    5. Create processing job for tracking
    """
    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    # Save to temporary location
    temp_dir = backend_dir / 'data' / 'temp'
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    temp_path = temp_dir / f"{uuid.uuid4()}_{file.filename}"
    contents = await file.read()
    with open(temp_path, 'wb') as f:
        f.write(contents)
    
    # Create processing job
    with Session(engine) as session:
        job = ProcessingJob(
            job_type="pdf_upload",
            status="pending",
            source=file.filename,
            progress=0
        )
        session.add(job)
        session.commit()
        job_id = job.id
    
    # Start background processing
    background_tasks.add_task(
        process_pdf_background,
        job_id,
        temp_path,
        file.filename,
        category
    )
    
    return {
        "job_id": job_id,
        "status": "pending",
        "message": "PDF upload started. Check job status for progress."
    }


@router.post("/documents/scrape-url")
async def scrape_url(
    background_tasks: BackgroundTasks,
    request: URLScrapeRequest
):
    """
    Scrape a URL and process its content.
    
    Steps:
    1. Check robots.txt
    2. Fetch HTML content
    3. Extract text and create Markdown chunks
    4. Upload to MinIO
    5. Store in PostgreSQL with embeddings
    6. Create processing job for tracking
    """
    # Create processing job
    with Session(engine) as session:
        job = ProcessingJob(
            job_type="url_scrape",
            status="pending",
            source=request.url,
            progress=0
        )
        session.add(job)
        session.commit()
        job_id = job.id
    
    # Start background processing
    background_tasks.add_task(
        scrape_url_background,
        job_id,
        request.url,
        request.category
    )
    
    return {
        "job_id": job_id,
        "status": "pending",
        "message": "URL scraping started. Check job status for progress."
    }


@router.get("/jobs/{job_id}", response_model=ProcessingJobResponse)
async def get_job_status(job_id: str):
    """Get status of a processing job."""
    with Session(engine) as session:
        job = session.get(ProcessingJob, job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return ProcessingJobResponse(
            job_id=job.id,
            job_type=job.job_type,
            status=job.status,
            progress=job.progress,
            source=job.source,
            documents_processed=job.documents_processed,
            error_message=job.error_message,
            result=json.loads(job.result) if job.result else None,
            created_at=job.created_at.isoformat(),
            updated_at=job.updated_at.isoformat()
        )


@router.get("/jobs", response_model=ProcessingReportResponse)
async def get_all_jobs(
    status: Optional[str] = None,
    job_type: Optional[str] = None,
    limit: int = 50
):
    """
    Get all processing jobs with optional filtering.
    
    Returns a report of all jobs with statistics.
    """
    with Session(engine) as session:
        # Build query
        query = select(ProcessingJob)
        
        if status:
            query = query.where(ProcessingJob.status == status)
        if job_type:
            query = query.where(ProcessingJob.job_type == job_type)
        
        query = query.order_by(ProcessingJob.created_at.desc()).limit(limit)
        
        jobs = session.exec(query).all()
        
        # Calculate statistics
        all_jobs = session.exec(select(ProcessingJob)).all()
        total = len(list(all_jobs))
        completed = len([j for j in all_jobs if j.status == "completed"])
        failed = len([j for j in all_jobs if j.status == "failed"])
        pending = len([j for j in all_jobs if j.status == "pending"])
        
        return ProcessingReportResponse(
            total_jobs=total,
            completed_jobs=completed,
            failed_jobs=failed,
            pending_jobs=pending,
            jobs=[
                ProcessingJobResponse(
                    job_id=job.id,
                    job_type=job.job_type,
                    status=job.status,
                    progress=job.progress,
                    source=job.source,
                    documents_processed=job.documents_processed,
                    error_message=job.error_message,
                    result=json.loads(job.result) if job.result else None,
                    created_at=job.created_at.isoformat(),
                    updated_at=job.updated_at.isoformat()
                )
                for job in jobs
            ]
        )


@router.post("/documents/upload")
async def upload_document(file: UploadFile = File(...), source: str = "ministry"):
    """
    Legacy endpoint: Ingest a document by uploading a file and indexing its content.
    """
    contents = await file.read()
    
    # Upload to MinIO
    path = upload_bytes(
        "documents", file.filename, contents, content_type=file.content_type
    )
    
    # Decode text content
    text_content = contents.decode("utf-8", errors="ignore")[:10000]
    
    # Store in database
    with Session(engine) as session:
        insert_q = text(
            """
            INSERT INTO document (title, content, source_url, document_type, category, is_indexed)
            VALUES (:t, :c, :s, :d, :cat, false)
            RETURNING id
            """
        )
        res = session.execute(
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
        
        # Generate embedding
        emb = await get_embedding(text_content)
        update_q = text("UPDATE document SET embedding = :e::vector WHERE id = :id")
        session.execute(update_q, {"e": emb, "id": doc_id})
        session.commit()
    
    return {"doc_id": doc_id, "path": path}
