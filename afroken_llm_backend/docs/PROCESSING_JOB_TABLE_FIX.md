# Processing Job Table Fix

## Issues Fixed

### 1. Missing `processingjob` Table in Schema ✅

**Problem**: The `create_schema_without_pgvector.sql` file was missing the `processingjob` table definition.

**Solution**: Added the complete `processingjob` table definition with:
- All required fields matching the SQLModel `ProcessingJob` model
- Proper constraints and indexes
- UUID as VARCHAR(36) to match SQLModel's string UUID convention

**Location**: `afroken_llm_database/create_schema_without_pgvector.sql` (lines 565-600)

---

### 2. Frontend Processing Jobs Page Enhancements ✅

**Problem**: 
- Status indicators (pending/completed) needed better visibility
- Missing "processing" status indicator
- No empty state when no jobs exist
- Stats calculation could be improved

**Solution**:
- Added "Processing" badge with spinning icon
- Added "Failed" badge (only shows when > 0)
- Improved stats calculation to include processing count
- Added empty state message when no jobs found
- Enhanced job type display (replaces underscores with spaces)
- Added tooltip on source column for long filenames

**Location**: `afroken_llm_frontend/src/pages/AdminDashboard.tsx`

**Changes**:
- Line 373-380: Enhanced stats calculation
- Line 840-857: Added processing and failed badges
- Line 880-962: Improved table with empty state and better formatting

---

### 3. Documentation Update ✅

**Problem**: PDF_UPLOAD_DATABASE_GUIDE.md referenced `processingjob` table but didn't include complete schema details.

**Solution**: Updated documentation to include:
- Complete table structure
- Index information
- Field descriptions with data types

**Location**: `afroken_llm_backend/docs/PDF_UPLOAD_DATABASE_GUIDE.md`

---

## Table Schema

```sql
CREATE TABLE IF NOT EXISTS processingjob (
    id VARCHAR(36) PRIMARY KEY, -- UUID as string
    job_type VARCHAR(50) NOT NULL, -- 'pdf_upload', 'url_scrape', 'batch_process'
    status VARCHAR(20) NOT NULL DEFAULT 'pending', -- 'pending', 'processing', 'completed', 'failed'
    source VARCHAR(500) NOT NULL, -- Filename, URL, etc.
    progress INT DEFAULT 0 CHECK (progress >= 0 AND progress <= 100),
    documents_processed INT DEFAULT 0 CHECK (documents_processed >= 0),
    error_message TEXT,
    result TEXT, -- JSON string
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_status CHECK (status IN ('pending', 'processing', 'completed', 'failed'))
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_processingjob_status ON processingjob(status);
CREATE INDEX IF NOT EXISTS idx_processingjob_job_type ON processingjob(job_type);
CREATE INDEX IF NOT EXISTS idx_processingjob_created_at ON processingjob(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_processingjob_status_type ON processingjob(status, job_type);
```

---

## Status Indicators

The frontend now displays:

1. **Pending** (Outline badge, Clock icon) - Jobs waiting to start
2. **Processing** (Secondary badge, RefreshCw icon) - Jobs currently running
3. **Completed** (Green badge, CheckCircle2 icon) - Successfully completed jobs
4. **Failed** (Red badge, XCircle icon) - Jobs that failed (only shown if count > 0)

---

## Testing

To verify the fixes:

1. **Database Schema**:
   ```bash
   # Run the updated schema file
   psql -U your_user -d your_db -f afroken_llm_database/create_schema_without_pgvector.sql
   ```

2. **Frontend**:
   - Navigate to Admin Dashboard → Processing Jobs tab
   - Upload a PDF or scrape a URL
   - Verify status badges update correctly
   - Check that pending/completed counts are accurate
   - Verify empty state shows when no jobs exist

3. **Database Check**:
   ```sql
   -- Verify table exists
   SELECT * FROM processingjob LIMIT 5;
   
   -- Check indexes
   SELECT indexname FROM pg_indexes WHERE tablename = 'processingjob';
   ```

---

## Notes

- The table name is `processingjob` (singular, lowercase) to match SQLModel's convention
- UUIDs are stored as VARCHAR(36) strings, not PostgreSQL UUID type (matches SQLModel)
- The table works with both PostgreSQL and SQLite (SQLModel handles the differences)
- Status values are constrained to: 'pending', 'processing', 'completed', 'failed'

