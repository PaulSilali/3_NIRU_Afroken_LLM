#!/usr/bin/env python3
"""
Test database connection script.

This script tests if the database connection is working properly.
Run this to verify your DATABASE_URL configuration.
"""

import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.config import settings
from app.db import engine, is_db_available, init_db
from sqlalchemy import text

def test_connection():
    """Test database connection and display results."""
    print("=" * 60)
    print("Database Connection Test")
    print("=" * 60)
    print(f"\nDATABASE_URL: {settings.DATABASE_URL}")
    print(f"Database Type: {'PostgreSQL' if 'postgresql' in settings.DATABASE_URL.lower() else 'SQLite' if 'sqlite' in settings.DATABASE_URL.lower() else 'Unknown'}")
    print("\n" + "-" * 60)
    
    # Test 1: Check if database is available
    print("\n1. Testing database availability...")
    try:
        available = is_db_available()
        if available:
            print("   ✅ Database is available!")
        else:
            print("   ❌ Database is NOT available")
            print("\n   Troubleshooting:")
            if "postgres" in settings.DATABASE_URL.lower():
                print("   - If using PostgreSQL, make sure it's running")
                print("   - Check if hostname is correct (use 'localhost' not 'postgres' for local dev)")
                print("   - Verify credentials and database name")
            return False
    except Exception as e:
        print(f"   ❌ Error checking availability: {e}")
        return False
    
    # Test 2: Test basic query
    print("\n2. Testing basic query...")
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1 as test"))
            row = result.fetchone()
            if row and row[0] == 1:
                print("   ✅ Basic query successful!")
            else:
                print("   ❌ Query returned unexpected result")
                return False
    except Exception as e:
        print(f"   ❌ Query failed: {e}")
        return False
    
    # Test 3: Check if tables exist
    print("\n3. Checking database tables...")
    try:
        with engine.connect() as conn:
            if "postgresql" in settings.DATABASE_URL.lower():
                result = conn.execute(text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                    ORDER BY table_name
                """))
            else:  # SQLite
                result = conn.execute(text("""
                    SELECT name 
                    FROM sqlite_master 
                    WHERE type='table'
                    ORDER BY name
                """))
            
            tables = [row[0] for row in result.fetchall()]
            if tables:
                print(f"   ✅ Found {len(tables)} table(s):")
                for table in tables[:10]:  # Show first 10
                    print(f"      - {table}")
                if len(tables) > 10:
                    print(f"      ... and {len(tables) - 10} more")
            else:
                print("   ⚠️  No tables found (this is OK if database is new)")
                print("   💡 Run the backend server to create tables automatically")
    except Exception as e:
        print(f"   ⚠️  Could not check tables: {e}")
        print("   (This is OK if tables don't exist yet)")
    
    # Test 4: Try to initialize database
    print("\n4. Testing database initialization...")
    try:
        init_db()
        print("   ✅ Database initialization successful!")
    except Exception as e:
        print(f"   ⚠️  Initialization warning: {e}")
        print("   (This might be OK if tables already exist)")
    
    print("\n" + "=" * 60)
    print("✅ Database connection test PASSED!")
    print("=" * 60)
    print("\nYou can now:")
    print("  1. Start the backend server")
    print("  2. Upload PDFs and scrape URLs")
    print("  3. Use all admin features")
    return True

if __name__ == "__main__":
    try:
        success = test_connection()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

