# CORS and Database Error Fixes

## Issues Fixed

### 1. ✅ CORS Error - Port 8080 Not Allowed
**Problem**: Frontend on `http://localhost:8080` was blocked by CORS policy.

**Root Cause**: 
- CORS was configured but when database errors occurred, the endpoint crashed before CORS headers could be sent
- Port 8080 was in the list but errors prevented headers from being added

**Fix Applied**:
- Updated CORS configuration to handle `settings.ENV` properly (defaults to "development")
- Added `http://127.0.0.1:8080` to allowed origins
- Added error handling to all admin endpoints so they return proper responses even when DB fails

### 2. ✅ Database Connection Error
**Problem**: Backend trying to connect to PostgreSQL hostname "postgres" (Docker service name) which doesn't exist locally.

**Error**: `could not translate host name "postgres" to address: No such host is known.`

**Root Cause**: 
- `DATABASE_URL` environment variable is set to use "postgres" hostname (for Docker)
- Running locally without Docker, so hostname doesn't resolve
- Endpoints crashed with 500 errors when DB connection failed

**Fix Applied**:
- Added comprehensive error handling to all admin endpoints
- Endpoints now gracefully handle database unavailability:
  - `/api/v1/admin/jobs` - Returns empty list when DB unavailable
  - `/api/v1/admin/jobs/{job_id}` - Returns 503 with helpful message
  - `/api/v1/admin/documents/upload-pdf` - Returns 503 with helpful message
  - `/api/v1/admin/documents/scrape-url` - Returns 503 with helpful message
  - `/api/v1/admin/services` - Returns empty list when DB unavailable
  - `/api/v1/admin/huduma-centres` - Returns empty list when DB unavailable
  - `/api/v1/admin/metrics` - Returns empty metrics when DB unavailable

## Solutions

### Option 1: Use SQLite (Recommended for Local Development)
Set `DATABASE_URL` to use SQLite instead of PostgreSQL:

```bash
# In .env file or environment
DATABASE_URL=sqlite:///./afroken_local.db
```

### Option 2: Fix PostgreSQL Connection
If you want to use PostgreSQL locally:

1. **Change hostname** in `DATABASE_URL`:
   ```bash
   # Instead of: postgresql://user:pass@postgres:5432/dbname
   # Use: postgresql://user:pass@localhost:5432/dbname
   DATABASE_URL=postgresql://user:pass@localhost:5432/afroken_db
   ```

2. **Or start PostgreSQL**:
   ```bash
   # Using Docker
   docker run -d --name postgres -e POSTGRES_PASSWORD=password -p 5432:5432 postgres
   ```

### Option 3: Remove DATABASE_URL (Use Default SQLite)
Simply don't set `DATABASE_URL` environment variable, and the app will default to SQLite.

## Testing

After applying fixes:
1. ✅ CORS errors should be resolved
2. ✅ Admin endpoints should return empty data instead of crashing
3. ✅ Upload/Scrape endpoints will show helpful error messages when DB is unavailable

## Next Steps

1. **For Local Development**: Use SQLite (Option 1)
2. **For Production**: Use PostgreSQL with correct connection string
3. **For Docker**: Keep "postgres" hostname but ensure Docker network is configured

