# Installing pgvector Extension for PostgreSQL

The AfroKen schema uses `pgvector` for vector embeddings and RAG (Retrieval Augmented Generation). If you see the error:

```
ERROR: extension "pgvector" is not available
```

You need to install the pgvector extension first.

## Installation Options

### Option 1: Using Pre-built Binaries (Easiest for Windows)

1. **Download pgvector for PostgreSQL 17:**
   - Visit: https://github.com/pgvector/pgvector/releases
   - Download the Windows binary for PostgreSQL 17
   - Or use: `pgvector-v0.5.1-windows-x64.zip` (check latest version)

2. **Extract and Install:**
   ```powershell
   # Extract the zip file
   # Copy the following files to your PostgreSQL installation:
   # - vector.dll → C:\Program Files\PostgreSQL\17\lib\
   # - vector.control → C:\Program Files\PostgreSQL\17\share\extension\
   # - vector--*.sql → C:\Program Files\PostgreSQL\17\share\extension\
   ```

3. **Restart PostgreSQL service:**
   ```powershell
   # Run as Administrator
   Restart-Service postgresql-x64-17
   ```

### Option 2: Build from Source (Advanced)

1. **Install Prerequisites:**
   - Visual Studio Build Tools
   - PostgreSQL development headers
   - Git

2. **Clone and Build:**
   ```powershell
   git clone --branch v0.5.1 https://github.com/pgvector/pgvector.git
   cd pgvector
   # Follow Windows build instructions in the repository
   ```

### Option 3: Use Docker (Recommended for Development)

If you're using Docker, use a PostgreSQL image with pgvector pre-installed:

```yaml
# docker-compose.yml
services:
  postgres:
    image: pgvector/pgvector:pg17
    environment:
      POSTGRES_DB: afroken_db
      POSTGRES_USER: afroken
      POSTGRES_PASSWORD: your_password
    ports:
      - "5432:5432"
```

### Option 4: Use Schema Without pgvector (Temporary Workaround)

If you can't install pgvector right now, you can modify the schema to use `TEXT` instead of `vector(384)` for embedding columns:

1. Replace `vector(384)` with `TEXT` in:
   - `messages.embedding`
   - `documents.embedding`
   - `document_chunks.embedding`

2. Skip the vector index creation

**Note:** This disables vector search/RAG functionality, but the rest of the schema will work.

## Verify Installation

After installation, verify pgvector is available:

```sql
-- Connect to your database
psql -U your_username -d your_database

-- Check if extension can be created
CREATE EXTENSION IF NOT EXISTS vector;

-- Verify
SELECT * FROM pg_extension WHERE extname = 'vector';
```

## Troubleshooting

### "Could not open extension control file"
- Make sure `vector.control` is in `C:\Program Files\PostgreSQL\17\share\extension\`
- Check file permissions (PostgreSQL service account needs read access)

### "library not found" or "DLL not found"
- Make sure `vector.dll` is in `C:\Program Files\PostgreSQL\17\lib\`
- Check that the DLL matches your PostgreSQL version (17)
- Restart PostgreSQL service after copying files

### "Access Denied" errors
- Run PowerShell/Command Prompt as Administrator
- Check that PostgreSQL service account has permissions to the installation directory

## Resources

- pgvector GitHub: https://github.com/pgvector/pgvector
- pgvector Documentation: https://github.com/pgvector/pgvector#installation
- PostgreSQL 17 Downloads: https://www.postgresql.org/download/windows/

