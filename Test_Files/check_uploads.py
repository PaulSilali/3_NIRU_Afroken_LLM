#!/usr/bin/env python3
"""
Quick script to check PDF uploads in the database.

Shows:
- All processing jobs (PDF uploads)
- All documents created from PDFs
- File system locations
"""

import sys
from pathlib import Path
import json

# Add backend directory to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.db import engine, is_db_available
from app.models import ProcessingJob, Document
from sqlmodel import Session, select

def check_uploads():
    """Check PDF uploads in database."""
    print("=" * 70)
    print("PDF Upload Database Check")
    print("=" * 70)
    
    # Check if database is available
    if not is_db_available():
        print("\n❌ Database is not available!")
        print("   Please check your DATABASE_URL configuration.")
        return
    
    print("\n✅ Database is available\n")
    
    with Session(engine) as session:
        # Get all PDF upload jobs
        print("-" * 70)
        print("PROCESSING JOBS (PDF Uploads)")
        print("-" * 70)
        
        jobs = session.exec(
            select(ProcessingJob)
            .where(ProcessingJob.job_type == "pdf_upload")
            .order_by(ProcessingJob.created_at.desc())
        ).all()
        
        if not jobs:
            print("No PDF upload jobs found.")
        else:
            print(f"\nFound {len(jobs)} PDF upload job(s):\n")
            for i, job in enumerate(jobs, 1):
                print(f"{i}. Job ID: {job.id}")
                print(f"   Status: {job.status}")
                print(f"   Source: {job.source}")
                print(f"   Progress: {job.progress}%")
                print(f"   Documents Processed: {job.documents_processed}")
                print(f"   Created: {job.created_at}")
                print(f"   Updated: {job.updated_at}")
                
                if job.error_message:
                    print(f"   ❌ Error: {job.error_message}")
                
                if job.result:
                    try:
                        result = json.loads(job.result)
                        print(f"   ✅ Result:")
                        print(f"      - Document ID: {result.get('document_id', 'N/A')}")
                        print(f"      - Markdown: {result.get('markdown_file', 'N/A')}")
                        print(f"      - PDF Path: {result.get('pdf_path', 'N/A')}")
                        if result.get('minio_path'):
                            print(f"      - MinIO: {result.get('minio_path')}")
                    except:
                        print(f"   Result: {job.result}")
                
                print()
        
        # Get all PDF documents
        print("-" * 70)
        print("DOCUMENTS (PDF Content)")
        print("-" * 70)
        
        docs = session.exec(
            select(Document)
            .where(Document.document_type == "pdf")
            .order_by(Document.created_at.desc())
        ).all()
        
        if not docs:
            print("No PDF documents found.")
        else:
            print(f"\nFound {len(docs)} PDF document(s):\n")
            for i, doc in enumerate(docs, 1):
                print(f"{i}. Document ID: {doc.id}")
                print(f"   Title: {doc.title}")
                print(f"   Category: {doc.category or 'N/A'}")
                print(f"   Content Length: {len(doc.content):,} characters")
                print(f"   Source URL: {doc.source_url or 'N/A'}")
                print(f"   Is Indexed: {doc.is_indexed}")
                print(f"   Created: {doc.created_at}")
                
                # Check if embedding exists
                try:
                    with session.connection() as conn:
                        from sqlalchemy import text
                        if "sqlite" in str(engine.url).lower():
                            result = conn.execute(
                                text("SELECT embedding FROM document WHERE id = :id"),
                                {"id": doc.id}
                            )
                        else:
                            result = conn.execute(
                                text("SELECT embedding::text FROM document WHERE id = :id"),
                                {"id": doc.id}
                            )
                        row = result.fetchone()
                        if row and row[0]:
                            emb_data = row[0]
                            if isinstance(emb_data, str):
                                try:
                                    emb_json = json.loads(emb_data)
                                    print(f"   ✅ Embedding: {len(emb_json)} dimensions")
                                except:
                                    print(f"   ✅ Embedding: Present (text format)")
                            else:
                                print(f"   ✅ Embedding: Present")
                        else:
                            print(f"   ⚠️  Embedding: Missing")
                except Exception as e:
                    print(f"   ⚠️  Could not check embedding: {e}")
                
                print()
        
        # Check file system
        print("-" * 70)
        print("FILE SYSTEM CHECK")
        print("-" * 70)
        
        pdfs_dir = backend_dir / 'data' / 'pdfs'
        docs_dir = backend_dir / 'data' / 'docs'
        temp_dir = backend_dir / 'data' / 'temp'
        
        print(f"\nPDF Files ({pdfs_dir}):")
        if pdfs_dir.exists():
            pdf_files = list(pdfs_dir.glob("*.pdf"))
            print(f"   Found {len(pdf_files)} PDF file(s)")
            for pdf in pdf_files[:5]:  # Show first 5
                size = pdf.stat().st_size / 1024  # KB
                print(f"   - {pdf.name} ({size:.1f} KB)")
            if len(pdf_files) > 5:
                print(f"   ... and {len(pdf_files) - 5} more")
        else:
            print("   Directory does not exist")
        
        print(f"\nMarkdown Files ({docs_dir}):")
        if docs_dir.exists():
            md_files = list(docs_dir.glob("*.md"))
            print(f"   Found {len(md_files)} markdown file(s)")
            for md in md_files[:5]:  # Show first 5
                print(f"   - {md.name}")
            if len(md_files) > 5:
                print(f"   ... and {len(md_files) - 5} more")
        else:
            print("   Directory does not exist")
        
        print(f"\nTemp Files ({temp_dir}):")
        if temp_dir.exists():
            temp_files = list(temp_dir.glob("*.pdf"))
            if temp_files:
                print(f"   ⚠️  Found {len(temp_files)} temp file(s) (should be cleaned up)")
                for temp in temp_files[:3]:
                    print(f"   - {temp.name}")
            else:
                print("   ✅ No temp files (clean)")
        else:
            print("   Directory does not exist")
    
    print("\n" + "=" * 70)
    print("Check Complete!")
    print("=" * 70)

if __name__ == "__main__":
    try:
        check_uploads()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

