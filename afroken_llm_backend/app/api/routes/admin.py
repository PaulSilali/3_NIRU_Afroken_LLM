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
            
            # Update embedding using raw SQL
            # Store as JSON string if pgvector not available (TEXT column), otherwise as vector
            if "postgresql" in str(engine.url):
                try:
                    # Try pgvector first
                    update_q = text(
                        "UPDATE document SET embedding = :e::vector WHERE id = :id"
                    )
                    session.execute(update_q, {"e": emb, "id": doc.id})
                    session.commit()
                except Exception:
                    # Fallback to TEXT (JSON string) if pgvector not available
                    import json
                    emb_json = json.dumps(emb.tolist() if hasattr(emb, 'tolist') else list(emb))
                    update_q = text(
                        "UPDATE document SET embedding = :e::text WHERE id = :id"
                    )
                    session.execute(update_q, {"e": emb_json, "id": doc.id})
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
                # Store as JSON string if pgvector not available (TEXT column), otherwise as vector
                if "postgresql" in str(engine.url):
                    try:
                        # Try pgvector first
                        update_q = text(
                            "UPDATE document SET embedding = :e::vector WHERE id = :id"
                        )
                        session.execute(update_q, {"e": emb, "id": doc.id})
                        session.commit()
                    except Exception:
                        # Fallback to TEXT (JSON string) if pgvector not available
                        import json
                        emb_json = json.dumps(emb.tolist() if hasattr(emb, 'tolist') else list(emb))
                        update_q = text(
                            "UPDATE document SET embedding = :e::text WHERE id = :id"
                        )
                        session.execute(update_q, {"e": emb_json, "id": doc.id})
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
        # Store as JSON string if pgvector not available (TEXT column), otherwise as vector
        try:
            # Try pgvector first
            update_q = text("UPDATE document SET embedding = :e::vector WHERE id = :id")
            session.execute(update_q, {"e": emb, "id": doc_id})
            session.commit()
        except Exception:
            # Fallback to TEXT (JSON string) if pgvector not available
            import json
            emb_json = json.dumps(emb.tolist() if hasattr(emb, 'tolist') else list(emb))
            update_q = text("UPDATE document SET embedding = :e::text WHERE id = :id")
            session.execute(update_q, {"e": emb_json, "id": doc_id})
            session.commit()
    
    return {"doc_id": doc_id, "path": path}


# ============================================================================
# SERVICES MANAGEMENT ENDPOINTS
# ============================================================================

@router.get("/services")
async def get_services():
    """Get all services from database."""
    try:
        with Session(engine) as session:
            query = text("SELECT id, name, category, description, service_website, keywords, is_active FROM services ORDER BY name")
            result = session.execute(query)
            rows = result.fetchall()
            
            services = []
            for row in rows:
                services.append({
                    "id": str(row[0]),
                    "name": row[1],
                    "category": row[2],
                    "description": row[3],
                    "website": row[4],
                    "keywords": row[5],
                    "is_active": row[6]
                })
            return {"services": services}
    except Exception as e:
        print(f"Error fetching services: {e}")
        return {"services": []}


@router.post("/services")
async def create_service(
    title: str,
    description: str,
    category: str = "general",
    logo: UploadFile = File(None)
):
    """Create a new service with optional logo upload."""
    try:
        # Check if service already exists
        with Session(engine) as session:
            check_q = text("SELECT id FROM services WHERE LOWER(name) = LOWER(:name)")
            existing = session.execute(check_q, {"name": title}).fetchone()
            if existing:
                raise HTTPException(status_code=400, detail="Service with this name already exists")
        
        # Upload logo if provided
        logo_url = None
        if logo:
            try:
                logo_data = await logo.read()
                logo_url = upload_bytes(
                    "logos",
                    f"services/{title.lower().replace(' ', '_')}_{logo.filename}",
                    logo_data,
                    content_type=logo.content_type or "image/png"
                )
            except Exception as e:
                print(f"Warning: Logo upload failed: {e}")
        
        # Insert service into database
        with Session(engine) as session:
            insert_q = text(
                """
                INSERT INTO services (name, category, description, service_website, is_active, keywords)
                VALUES (:name, :cat, :desc, :web, true, :keywords)
                RETURNING id
                """
            )
            result = session.execute(
                insert_q,
                {
                    "name": title,
                    "cat": category,
                    "desc": description,
                    "web": logo_url or "",
                    "keywords": title.lower()
                }
            )
            service_id = result.scalar()
            session.commit()
            
            return {
                "id": str(service_id),
                "name": title,
                "category": category,
                "description": description,
                "logo_url": logo_url,
                "message": "Service created successfully"
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create service: {str(e)}")


# ============================================================================
# HUDUMA CENTRES MANAGEMENT ENDPOINTS
# ============================================================================

@router.get("/huduma-centres")
async def get_huduma_centres():
    """Get all Huduma Centres from database."""
    try:
        with Session(engine) as session:
            query = text(
                """
                SELECT id, name, center_code, county, sub_county, town, latitude, longitude, 
                       contact_phone, contact_email, services_offered, is_active
                FROM huduma_centres 
                ORDER BY county, name
                """
            )
            result = session.execute(query)
            rows = result.fetchall()
            
            centres = []
            for row in rows:
                centres.append({
                    "id": str(row[0]),
                    "name": row[1],
                    "center_code": row[2],
                    "county": row[3],
                    "sub_county": row[4],
                    "town": row[5],
                    "latitude": float(row[6]) if row[6] else None,
                    "longitude": float(row[7]) if row[7] else None,
                    "contact_phone": row[8],
                    "contact_email": row[9],
                    "services_offered": json.loads(row[10]) if row[10] else [],
                    "is_active": row[11]
                })
            return {"centres": centres}
    except Exception as e:
        print(f"Error fetching Huduma Centres: {e}")
        return {"centres": []}


@router.post("/huduma-centres")
async def create_huduma_centre(
    name: str,
    county: str,
    sub_county: str = None,
    town: str = None,
    latitude: float = None,
    longitude: float = None,
    contact_phone: str = None,
    contact_email: str = None
):
    """Create a new Huduma Centre."""
    try:
        # Generate center code
        center_code = f"HC-{name.upper().replace(' ', '-')[:20]}"
        
        with Session(engine) as session:
            insert_q = text(
                """
                INSERT INTO huduma_centres 
                (name, center_code, county, sub_county, town, latitude, longitude, 
                 contact_phone, contact_email, services_offered, opening_hours, facilities, is_active)
                VALUES 
                (:name, :code, :county, :sub_county, :town, :lat, :lon, 
                 :phone, :email, '[]'::jsonb, 
                 '{"monday": "8:00 AM - 5:00 PM", "tuesday": "8:00 AM - 5:00 PM", 
                   "wednesday": "8:00 AM - 5:00 PM", "thursday": "8:00 AM - 5:00 PM", 
                   "friday": "8:00 AM - 5:00 PM", "saturday": "8:00 AM - 1:00 PM", 
                   "sunday": "CLOSED"}'::jsonb,
                 '["parking", "wifi", "restrooms"]'::jsonb, true)
                RETURNING id
                """
            )
            result = session.execute(
                insert_q,
                {
                    "name": name,
                    "code": center_code,
                    "county": county,
                    "sub_county": sub_county,
                    "town": town,
                    "lat": latitude,
                    "lon": longitude,
                    "phone": contact_phone,
                    "email": contact_email
                }
            )
            centre_id = result.scalar()
            session.commit()
            
            return {
                "id": str(centre_id),
                "name": name,
                "center_code": center_code,
                "county": county,
                "message": "Huduma Centre created successfully"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create Huduma Centre: {str(e)}")


# ============================================================================
# CHAT METRICS ENDPOINT
# ============================================================================

@router.get("/metrics")
async def get_chat_metrics():
    """Get aggregated chat metrics from database."""
    try:
        with Session(engine) as session:
            # Get latest metrics (last 30 days aggregated)
            query = text(
                """
                SELECT 
                    COALESCE(SUM(total_conversations), 0) as total_conversations,
                    COALESCE(SUM(total_messages), 0) as total_messages,
                    COALESCE(SUM(total_queries), 0) as total_queries,
                    COALESCE(AVG(average_response_time_ms), 0) / 1000.0 as avg_response_time,
                    COALESCE(AVG(average_satisfaction_score), 0) * 20 as satisfaction_rate,
                    COALESCE(SUM(unique_users), 0) as unique_users
                FROM chat_metrics
                WHERE date_hour >= NOW() - INTERVAL '30 days'
                """
            )
            result = session.execute(query)
            row = result.fetchone()
            
            # Get top intents from latest metrics
            intents_query = text(
                """
                SELECT top_intents
                FROM chat_metrics
                WHERE date_hour >= NOW() - INTERVAL '30 days'
                  AND top_intents IS NOT NULL
                ORDER BY date_hour DESC
                LIMIT 1
                """
            )
            intents_result = session.execute(intents_query)
            intents_row = intents_result.fetchone()
            
            top_intents = []
            if intents_row and intents_row[0]:
                intents_data = json.loads(intents_row[0]) if isinstance(intents_row[0], str) else intents_row[0]
                if isinstance(intents_data, list):
                    top_intents = intents_data[:5]
            
            # Calculate escalations (placeholder - would need conversations table)
            escalations = 0
            
            return {
                "total_queries": int(row[2]) if row[2] else 0,
                "total_conversations": int(row[0]) if row[0] else 0,
                "total_messages": int(row[1]) if row[1] else 0,
                "avg_response_time": float(row[3]) if row[3] else 0,
                "satisfaction_rate": round(float(row[4]) if row[4] else 0),
                "escalations": escalations,
                "unique_users": int(row[5]) if row[5] else 0,
                "top_intents": top_intents
            }
    except Exception as e:
        print(f"Error fetching metrics: {e}")
        return {
            "total_queries": 0,
            "total_conversations": 0,
            "total_messages": 0,
            "avg_response_time": 0,
            "satisfaction_rate": 0,
            "escalations": 0,
            "unique_users": 0,
            "top_intents": []
        }
