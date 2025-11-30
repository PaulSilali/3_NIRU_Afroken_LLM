# Quick Database Fix for PDF Upload

## Problem
You're getting a **503 Service Unavailable** error when trying to upload PDFs because the database is not available.

## Quick Fix (Choose One)

### Option 1: Use SQLite (Easiest - Recommended) ⭐

**This is the fastest solution!**

1. **Create or edit `.env` file** in `afroken_llm_backend/`:
   ```bash
   DATABASE_URL=sqlite:///./afroken_local.db
   ```

2. **Restart your backend server**

That's it! SQLite will automatically create the database file.

---

### Option 2: Fix PostgreSQL Connection

If your `DATABASE_URL` has `postgres` as the hostname (Docker service name), change it to `localhost`:

**Before:**
```bash
DATABASE_URL=postgresql://user:pass@postgres:5432/dbname
```

**After:**
```bash
DATABASE_URL=postgresql://user:pass@localhost:5432/dbname
```

Then make sure PostgreSQL is running on your machine.

---

### Option 3: Start PostgreSQL with Docker

If you want to use PostgreSQL:

```bash
docker run -d --name postgres \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=afroken_db \
  -p 5432:5432 \
  postgres
```

Then set your `DATABASE_URL`:
```bash
DATABASE_URL=postgresql://postgres:password@localhost:5432/afroken_db
```

---

## Verify Fix

After setting up the database:

1. **Restart backend server**
2. **Check backend console** - should see "✓ Database initialized"
3. **Try uploading a PDF** - should work now!

---

## What Changed?

- Added better error messages that tell you exactly how to fix the issue
- Added database availability check before attempting uploads
- Error messages now include quick fix instructions

---

## Still Having Issues?

Check:
1. Is the `.env` file in the correct location? (`afroken_llm_backend/.env`)
2. Did you restart the backend after changing `.env`?
3. Check backend console for database connection messages

