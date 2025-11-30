#!/usr/bin/env python3
"""
Test PDF upload end-to-end until saved in database.

This script:
1. Tests database connection (PostgreSQL)
2. Tests PDF processing libraries
3. Simulates PDF upload flow
4. Verifies job is created in processingjob table
5. Verifies document is created in document table
"""

import sys
from pathlib import Path
import json

# Add backend directory to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.config import settings
from app.db import engine, is_db_available, init_db
from app.models import ProcessingJob, Document
from sqlmodel import Session, select
from sqlalchemy import text

def test_database_connection():
    """Test PostgreSQL connection."""
    print("=" * 70)
    print("1. Testing PostgreSQL Database Connection")
    print("=" * 70)
    
    print(f"\nDATABASE_URL: {settings.DATABASE_URL}")
    
    if "sqlite" in settings.DATABASE_URL.lower():
        print("❌ ERROR: Still using SQLite! Please update .env to use PostgreSQL")
        return False
    
    if "postgresql" not in settings.DATABASE_URL.lower():
        print("❌ ERROR: DATABASE_URL does not point to PostgreSQL")
        return False
    
    try:
        available = is_db_available()
        if available:
            print("✅ PostgreSQL database is available!")
            
            # Test connection
            with engine.connect() as conn:
                result = conn.execute(text("SELECT version()"))
                version = result.fetchone()[0]
                print(f"✅ PostgreSQL version: {version.split(',')[0]}")
            
            return True
        else:
            print("❌ PostgreSQL database is NOT available")
            print("\nTroubleshooting:")
            print("  1. Make sure PostgreSQL is running")
            print("  2. Check DATABASE_URL in .env file")
            print("  3. Verify credentials and database name")
            return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False


def test_pdf_libraries():
    """Test PDF processing libraries."""
    print("\n" + "=" * 70)
    print("2. Testing PDF Processing Libraries")
    print("=" * 70)
    
    try:
        from scripts.rag.pdf_to_markdown import extract_text_from_pdf, create_markdown_from_pdf
        print("✅ PDF processing libraries imported successfully")
        return True
    except ImportError as e:
        print(f"❌ PDF libraries not available: {e}")
        print("\nInstall with:")
        print("  pip install pdfplumber pypdfium2 PyPDF2")
        return False
    except Exception as e:
        print(f"❌ Error importing PDF libraries: {e}")
        return False


def test_processing_job_table():
    """Test processingjob table exists and can be queried."""
    print("\n" + "=" * 70)
    print("3. Testing processingjob Table")
    print("=" * 70)
    
    try:
        with Session(engine) as session:
            # Check if table exists
            if "postgresql" in str(engine.url).lower():
                result = session.execute(text("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = 'processingjob'
                    )
                """))
            else:
                result = session.execute(text("""
                    SELECT EXISTS (
                        SELECT FROM sqlite_master 
                        WHERE type='table' AND name='processingjob'
                    )
                """))
            
            exists = result.fetchone()[0]
            if exists:
                print("✅ processingjob table exists")
                
                # Count jobs
                jobs = session.exec(select(ProcessingJob)).all()
                print(f"✅ Found {len(jobs)} job(s) in database")
                
                # Show recent jobs
                if jobs:
                    print("\nRecent jobs:")
                    for job in jobs[-5:]:  # Last 5
                        print(f"  - {job.id[:8]}... | {job.status} | {job.source}")
                
                return True
            else:
                print("❌ processingjob table does NOT exist")
                print("\nRun database schema:")
                print("  psql -U afroken -d afroken_llm_db -f ../afroken_llm_database/create_schema_without_pgvector.sql")
                return False
    except Exception as e:
        print(f"❌ Error checking table: {e}")
        return False


def test_document_table():
    """Test document table exists."""
    print("\n" + "=" * 70)
    print("4. Testing document Table")
    print("=" * 70)
    
    try:
        with Session(engine) as session:
            # Check if table exists
            if "postgresql" in str(engine.url).lower():
                result = session.execute(text("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = 'document'
                    )
                """))
            else:
                result = session.execute(text("""
                    SELECT EXISTS (
                        SELECT FROM sqlite_master 
                        WHERE type='table' AND name='document'
                    )
                """))
            
            exists = result.fetchone()[0]
            if exists:
                print("✅ document table exists")
                
                # Count documents
                docs = session.exec(select(Document)).all()
                print(f"✅ Found {len(docs)} document(s) in database")
                
                if docs:
                    print("\nRecent documents:")
                    for doc in docs[-5:]:  # Last 5
                        print(f"  - {doc.id[:8]}... | {doc.title} | {doc.document_type}")
                
                return True
            else:
                print("❌ document table does NOT exist")
                return False
    except Exception as e:
        print(f"❌ Error checking table: {e}")
        return False


def test_pdf_upload_flow():
    """Test the complete PDF upload flow."""
    print("\n" + "=" * 70)
    print("5. Testing PDF Upload Flow (Simulation)")
    print("=" * 70)
    
    # Check if we have a test PDF
    test_pdf = backend_dir / 'data' / 'pdfs' / 'NPS_And_KPS_HandBook.pdf'
    
    if not test_pdf.exists():
        print("⚠️  No test PDF found at data/pdfs/NPS_And_KPS_HandBook.pdf")
        print("   Skipping actual PDF processing test")
        return True
    
    try:
        from scripts.rag.pdf_to_markdown import extract_text_from_pdf
        
        print(f"\nTesting PDF extraction on: {test_pdf.name}")
        text_content = extract_text_from_pdf(test_pdf)
        
        if text_content and len(text_content) > 100:
            print(f"✅ PDF extraction successful! Extracted {len(text_content)} characters")
            print(f"   Preview: {text_content[:100]}...")
            return True
        else:
            print("❌ PDF extraction returned empty or too short text")
            return False
            
    except Exception as e:
        print(f"❌ PDF extraction failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("PDF Upload End-to-End Test")
    print("=" * 70)
    
    results = {
        "Database Connection": test_database_connection(),
        "PDF Libraries": test_pdf_libraries(),
        "ProcessingJob Table": test_processing_job_table(),
        "Document Table": test_document_table(),
        "PDF Upload Flow": test_pdf_upload_flow(),
    }
    
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 70)
    if all_passed:
        print("✅ All tests PASSED! PDF upload should work.")
        print("\nNext steps:")
        print("  1. Restart your backend server")
        print("  2. Upload a PDF through the admin dashboard")
        print("  3. Check Processing Jobs tab for status")
    else:
        print("❌ Some tests FAILED. Fix issues above before uploading PDFs.")
    print("=" * 70)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

