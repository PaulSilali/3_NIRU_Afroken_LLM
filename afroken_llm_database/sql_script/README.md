# AfroKen Database Schema Setup

## Quick Start (Recommended)

**Use the combined schema file** for easiest setup:

```bash
# Connect to your PostgreSQL database
psql -U afroken -d afroken_db

# Run the combined schema (includes everything)
\i sql_script/afroken_complete_schema.sql
```

This single file includes both the base schema and all extensions in the correct order.

## ⚠️ Important: pgvector Extension Required

The schema uses `pgvector` for vector embeddings and RAG functionality. If you see:

```
ERROR: extension "pgvector" is not available
```

**You have two options:**

### Option 1: Install pgvector (Recommended)
See **[INSTALL_PGVECTOR.md](INSTALL_PGVECTOR.md)** for detailed installation instructions for Windows/PostgreSQL 17.

### Option 2: Quick Workaround (Temporary)
If you can't install pgvector right now, you can manually edit `afroken_complete_schema.sql`:

1. Comment out or remove the pgvector extension line:
   ```sql
   -- CREATE EXTENSION IF NOT EXISTS "pgvector";
   ```

2. Replace all `vector(384)` with `TEXT` in:
   - `messages.embedding`
   - `documents.embedding`  
   - `document_chunks.embedding`

3. Skip the vector index creation (lines with `hnsw`)

**Note:** This disables vector search/RAG, but the rest of the schema will work.

---

## Alternative: Separate Files

If you prefer to run files separately, the database schema consists of **two SQL files** that must be run in this specific order:

### 1. Base Schema (Run First)
**File:** `afroken_complete_database.sql` (located in `Documentation/` folder)

This creates:
- PostgreSQL extensions (uuid-ossp, pgvector, pg_trgm, btree_gin)
- Custom types (user_role, language_type, conversation_status, etc.)
- **Core tables:**
  - `users`
  - `conversations`
  - `messages`
  - `documents`
  - `services`
  - And other base tables

### 2. Extension Schema (Run Second)
**File:** `Db_afroken_llm .sql` (this file)

This creates:
- Frontend/integration enhancement tables
- `attachments`
- `canned_responses`
- `quick_actions`
- `ui_templates`
- `translations`
- `notification_queue`
- `webhooks`
- `api_keys`
- `analytics_events`
- And other extension tables

## Quick Setup

```bash
# Connect to your PostgreSQL database
psql -U afroken -d afroken_db

# Run base schema first
\i Documentation/afroken_complete_database.sql

# Then run extension schema
\i sql_script/Db_afroken_llm\ .sql
```

## Common Errors

### Error: `relation "users" does not exist`
**Cause:** You're trying to run the extension script before the base schema.

**Solution:** Run `afroken_complete_database.sql` first, then run `Db_afroken_llm .sql`.

### Error: `type "language_type" does not exist`
**Cause:** The base schema hasn't been run, so custom types aren't created.

**Solution:** Run the base schema first to create all ENUM types.

## Verification

After running both scripts, verify the setup:

```sql
-- Check that base tables exist
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('users', 'conversations', 'messages', 'documents', 'services');

-- Check that extension tables exist
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('attachments', 'canned_responses', 'notification_queue');

-- Check that types exist
SELECT typname FROM pg_type 
WHERE typname IN ('user_role', 'language_type', 'conversation_status');
```

## Notes

- Both scripts use `CREATE TABLE IF NOT EXISTS`, so they're safe to run multiple times
- Foreign key constraints ensure referential integrity
- All tables use UUID primary keys for better distributed system support
- The extension script includes sample data inserts (canned_responses, quick_actions)

