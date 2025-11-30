#!/usr/bin/env python3
"""Quick check of jobs and documents in database."""

from app.db import engine
from app.models import ProcessingJob, Document
from sqlmodel import Session, select

with Session(engine) as session:
    print("=" * 70)
    print("PROCESSING JOBS")
    print("=" * 70)
    jobs = session.exec(select(ProcessingJob).order_by(ProcessingJob.created_at.desc()).limit(5)).all()
    for j in jobs:
        print(f"\nJob: {j.id[:8]}...")
        print(f"  Status: {j.status}")
        print(f"  Source: {j.source}")
        print(f"  Progress: {j.progress}%")
        print(f"  Documents: {j.documents_processed}")
        if j.error_message:
            print(f"  Error: {j.error_message[:100]}")
    
    print("\n" + "=" * 70)
    print("DOCUMENTS")
    print("=" * 70)
    docs = session.exec(select(Document).order_by(Document.created_at.desc()).limit(5)).all()
    for d in docs:
        print(f"\nDocument: {d.id[:8]}...")
        print(f"  Title: {d.title}")
        print(f"  Type: {d.document_type}")
        print(f"  Category: {d.category}")
        print(f"  Content: {len(d.content)} chars")
        print(f"  Indexed: {d.is_indexed}")

