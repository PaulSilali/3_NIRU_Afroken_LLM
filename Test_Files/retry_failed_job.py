#!/usr/bin/env python3
"""
Retry a failed PDF processing job.

Usage:
    python retry_failed_job.py <job_id>
    python retry_failed_job.py  # Retries the most recent failed job
"""

import sys
from pathlib import Path
from datetime import datetime

# Add backend directory to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.db import engine
from app.models import ProcessingJob
from sqlmodel import Session, select
from app.api.routes.admin import process_pdf_background
import asyncio

def retry_job(job_id: str = None):
    """Retry a failed PDF processing job."""
    with Session(engine) as session:
        if job_id:
            job = session.get(ProcessingJob, job_id)
            if not job:
                print(f"❌ Job {job_id} not found")
                return False
        else:
            # Get most recent failed job
            job = session.exec(
                select(ProcessingJob)
                .where(ProcessingJob.status == "failed")
                .where(ProcessingJob.job_type == "pdf_upload")
                .order_by(ProcessingJob.created_at.desc())
            ).first()
            
            if not job:
                print("❌ No failed PDF upload jobs found")
                return False
            
            job_id = job.id
        
        print(f"Retrying job: {job_id[:8]}...")
        print(f"Source: {job.source}")
        print(f"Error: {job.error_message}")
        
        # Find the PDF file
        pdfs_dir = backend_dir / 'data' / 'pdfs'
        temp_dir = backend_dir / 'data' / 'temp'
        
        pdf_file = None
        # Check permanent location first
        if pdfs_dir.exists():
            pdf_file = pdfs_dir / job.source
            if not pdf_file.exists():
                pdf_file = None
        
        # Check temp location
        if not pdf_file and temp_dir.exists():
            for temp_file in temp_dir.glob(f"*{job.source}"):
                pdf_file = temp_file
                break
        
        if not pdf_file or not pdf_file.exists():
            print(f"❌ PDF file not found: {job.source}")
            print(f"   Checked: {pdfs_dir}")
            print(f"   Checked: {temp_dir}")
            return False
        
        print(f"✅ Found PDF: {pdf_file}")
        
        # Reset job status
        job.status = "pending"
        job.progress = 0
        job.error_message = None
        job.updated_at = datetime.utcnow()
        session.add(job)
        session.commit()
        
        print("✅ Job reset to pending")
        
        # Process the PDF
        print("🔄 Processing PDF...")
        try:
            asyncio.run(process_pdf_background(
                job_id=job_id,
                file_path=pdf_file,
                filename=job.source,
                category=None
            ))
            print("✅ Job processing completed!")
            return True
        except Exception as e:
            print(f"❌ Processing failed: {e}")
            import traceback
            traceback.print_exc()
            return False


if __name__ == "__main__":
    job_id = sys.argv[1] if len(sys.argv) > 1 else None
    success = retry_job(job_id)
    sys.exit(0 if success else 1)

