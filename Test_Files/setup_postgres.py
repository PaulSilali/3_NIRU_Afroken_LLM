#!/usr/bin/env python3
"""
Setup PostgreSQL database and user for AfroKen LLM.

This script helps set up PostgreSQL connection.
Run this if you're getting password authentication errors.
"""

import sys
import subprocess
from pathlib import Path

def check_postgres_running():
    """Check if PostgreSQL is running."""
    print("Checking if PostgreSQL is running...")
    try:
        # Try to connect to PostgreSQL (any database)
        result = subprocess.run(
            ["psql", "-U", "postgres", "-c", "SELECT version();"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print("✅ PostgreSQL is running")
            return True
        else:
            print("❌ PostgreSQL connection failed")
            print(f"Error: {result.stderr}")
            return False
    except FileNotFoundError:
        print("⚠️  psql command not found. PostgreSQL might not be installed.")
        print("   Install PostgreSQL: https://www.postgresql.org/download/")
        return False
    except Exception as e:
        print(f"❌ Error checking PostgreSQL: {e}")
        return False


def create_database_and_user():
    """Create database and user."""
    print("\n" + "=" * 70)
    print("PostgreSQL Setup Instructions")
    print("=" * 70)
    
    print("\nTo create the database and user, run these SQL commands:")
    print("\n1. Connect to PostgreSQL as superuser:")
    print("   psql -U postgres")
    
    print("\n2. Run these SQL commands:")
    print("""
-- Create user (if doesn't exist)
CREATE USER afroken WITH PASSWORD '11403775411';

-- Create database
CREATE DATABASE afroken_llm_db OWNER afroken;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE afroken_llm_db TO afroken;

-- Connect to the new database
\\c afroken_llm_db

-- Grant schema privileges
GRANT ALL ON SCHEMA public TO afroken;

-- Exit
\\q
""")
    
    print("\n3. Or use default postgres user:")
    print("   Update .env file:")
    print("   DATABASE_URL=postgresql+psycopg2://postgres:YOUR_PASSWORD@localhost:5432/afroken_llm_db")
    
    print("\n4. Create database:")
    print("   psql -U postgres -c 'CREATE DATABASE afroken_llm_db;'")


def test_connection():
    """Test database connection."""
    print("\n" + "=" * 70)
    print("Testing Database Connection")
    print("=" * 70)
    
    try:
        from app.config import settings
        from app.db import is_db_available
        
        print(f"\nDATABASE_URL: {settings.DATABASE_URL}")
        
        if is_db_available():
            print("✅ Database connection successful!")
            return True
        else:
            print("❌ Database connection failed")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Main setup function."""
    print("=" * 70)
    print("PostgreSQL Setup for AfroKen LLM")
    print("=" * 70)
    
    # Check if PostgreSQL is running
    if not check_postgres_running():
        print("\n⚠️  PostgreSQL might not be running or accessible")
        print("\nTo start PostgreSQL:")
        print("  Windows: Start PostgreSQL service from Services")
        print("  Or: net start postgresql-x64-XX (replace XX with version)")
    
    # Show setup instructions
    create_database_and_user()
    
    # Test connection
    print("\n" + "=" * 70)
    test_connection()
    
    print("\n" + "=" * 70)
    print("After setting up PostgreSQL:")
    print("  1. Restart your backend server")
    print("  2. Run: python test_pdf_upload.py")
    print("  3. Try uploading a PDF")
    print("=" * 70)


if __name__ == "__main__":
    main()

