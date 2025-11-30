#!/usr/bin/env python3
"""
Test actual PDF upload end-to-end until saved in database.

This script:
1. Simulates a PDF upload
2. Creates a processing job
3. Processes the PDF
4. Verifies it's saved in the database
"""

import sys
from pathlib import Path
import uuid
from datetime import datetime

# Add backend directory to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.config import settings
from app.db import engine, is_db_available
from app.models import ProcessingJob, Document
from sqlmodel import Session, select
from scripts.rag.pdf_to_markdown import extract_text_from_pdf, create_markdown_from_pdf

def test_actual_upload():
    """Test actual PDF upload and database save."""
    print("=" * 70)
    print("Testing Actual PDF Upload to Database")
    print("=" * 70)
    
    # Check database
    if not is_db_available():
        print("❌ Database not available!")
        return False
    
    # Find a test PDF
    test_pdf = backend_dir / 'data' / 'pdfs' / 'NPS_And_KPS_HandBook.pdf'
    if not test_pdf.exists():
        print("❌ No test PDF found at data/pdfs/NPS_And_KPS_HandBook.pdf")
        return False
    
    print(f"\n✅ Found test PDF: {test_pdf.name}")
    
    try:
        # Step 1: Create processing job
        print("\n1. Creating processing job...")
        with Session(engine) as session:
            job = ProcessingJob(
                job_type="pdf_upload",
                status="pending",
                source=test_pdf.name,
                progress=0
            )
            session.add(job)
            session.commit()
            session.refresh(job)
            job_id = job.id
            print(f"   ✅ Job created: {job_id[:8]}...")
        
        # Step 2: Update job to processing
        print("\n2. Updating job status to processing...")
        with Session(engine) as session:
            job = session.get(ProcessingJob, job_id)
            if job:
                job.status = "processing"
                job.progress = 10
                job.updated_at = datetime.utcnow()
                session.add(job)
                session.commit()
                print("   ✅ Job status updated to processing")
        
        # Step 3: Extract text from PDF
        print("\n3. Extracting text from PDF...")
        text_content = extract_text_from_pdf(test_pdf)
        print(f"   ✅ Extracted {len(text_content)} characters")
        
        # Step 4: Update progress
        print("\n4. Updating progress...")
        with Session(engine) as session:
            job = session.get(ProcessingJob, job_id)
            if job:
                job.progress = 50
                job.updated_at = datetime.utcnow()
                session.add(job)
                session.commit()
                print("   ✅ Progress updated to 50%")
        
        # Step 5: Create markdown file
        print("\n5. Creating markdown file...")
        docs_dir = backend_dir / 'data' / 'docs'
        docs_dir.mkdir(parents=True, exist_ok=True)
        md_filename = create_markdown_from_pdf(
            pdf_path=test_pdf,
            output_dir=docs_dir,
            title=None,
            category="test",
            source=f"PDF Upload: {test_pdf.name}",
            tags=None
        )
        print(f"   ✅ Markdown created: {md_filename}")
        
        # Step 6: Create document in database
        print("\n6. Creating document in database...")
        with Session(engine) as session:
            doc = Document(
                title=test_pdf.stem,
                content=text_content[:50000],  # Truncate for DB
                source_url=str(test_pdf),
                document_type="pdf",
                category="test",
                is_indexed=True
            )
            session.add(doc)
            session.commit()
            session.refresh(doc)
            doc_id = doc.id
            print(f"   ✅ Document created: {doc_id[:8]}...")
        
        # Step 7: Update job as completed
        print("\n7. Updating job as completed...")
        import json
        with Session(engine) as session:
            job = session.get(ProcessingJob, job_id)
            if job:
                job.status = "completed"
                job.progress = 100
                job.documents_processed = 1
                job.updated_at = datetime.utcnow()
                job.result = json.dumps({
                    "document_id": str(doc_id),
                    "markdown_file": str(md_filename),
                    "pdf_path": str(test_pdf)
                })
                session.add(job)
                session.commit()
                print("   ✅ Job marked as completed")
        
        # Step 8: Verify in database
        print("\n8. Verifying in database...")
        with Session(engine) as session:
            # Check job
            job = session.get(ProcessingJob, job_id)
            if job and job.status == "completed":
                print(f"   ✅ Job found: {job.status} | {job.progress}% | {job.documents_processed} docs")
            else:
                print("   ❌ Job not found or not completed")
                return False
            
            # Check document
            doc = session.get(Document, doc_id)
            if doc:
                print(f"   ✅ Document found: {doc.title} | {doc.document_type} | {len(doc.content)} chars")
            else:
                print("   ❌ Document not found")
                return False
        
        print("\n" + "=" * 70)
        print("✅ SUCCESS! PDF upload test completed and saved to database!")
        print("=" * 70)
        print(f"\nJob ID: {job_id}")
        print(f"Document ID: {doc_id}")
        print(f"Status: {job.status}")
        print(f"Documents Processed: {job.documents_processed}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error during upload test: {e}")
        import traceback
        traceback.print_exc()
        
        # Mark job as failed if it exists
        try:
            with Session(engine) as session:
                job = session.get(ProcessingJob, job_id)
                if job:
                    job.status = "failed"
                    job.error_message = str(e)
                    job.updated_at = datetime.utcnow()
                    session.add(job)
                    session.commit()
        except:
            pass
        
        return False


if __name__ == "__main__":
    try:
        success = test_actual_upload()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

