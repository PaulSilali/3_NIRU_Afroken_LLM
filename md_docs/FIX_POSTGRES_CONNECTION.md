# Fix PostgreSQL Connection

## Current Issue
PostgreSQL password authentication is failing. The connection string in `.env` might have incorrect credentials.

## Current DATABASE_URL
```
postgresql+psycopg2://afroken:11403775411@localhost:5432/afroken_llm_db
```

## Steps to Fix

### Option 1: Verify PostgreSQL is Running

```powershell
# Check if PostgreSQL service is running
Get-Service -Name postgresql*

# Or check if port 5432 is listening
netstat -an | findstr 5432
```

### Option 2: Test Connection Manually

```powershell
# Try connecting with psql (if installed)
psql -U afroken -d afroken_llm_db -h localhost -p 5432
```

### Option 3: Update .env with Correct Credentials

If your PostgreSQL has different credentials, update `.env`:

```bash
# Format: postgresql+psycopg2://USERNAME:PASSWORD@HOST:PORT/DATABASE
DATABASE_URL=postgresql+psycopg2://postgres:your_password@localhost:5432/afroken_llm_db
```

### Option 4: Create Database and User

If database doesn't exist, create it:

```sql
-- Connect as postgres superuser
psql -U postgres

-- Create database
CREATE DATABASE afroken_llm_db;

-- Create user
CREATE USER afroken WITH PASSWORD '11403775411';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE afroken_llm_db TO afroken;

-- Exit
\q
```

### Option 5: Use Default PostgreSQL User

If you don't have the `afroken` user, use default `postgres`:

```bash
DATABASE_URL=postgresql+psycopg2://postgres:your_postgres_password@localhost:5432/afroken_llm_db
```

## After Fixing Connection

1. **Restart backend server**
2. **Run test**: `python test_pdf_upload.py`
3. **Upload PDF** through admin dashboard
4. **Check database**: Jobs should be saved in `processingjob` table

## Verify Connection

```python
python -c "from app.db import is_db_available; print('Connected!' if is_db_available() else 'Failed!')"
```

