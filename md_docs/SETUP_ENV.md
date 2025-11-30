# Setting Up .env File

## Current Issue
Your `DATABASE_URL` is set to: `postgresql://afroken:11403775411@postgres:5432/afroken_llm_db`

The hostname "postgres" is a Docker service name and won't work for local development.

## Quick Fix

### Option 1: Use SQLite (Recommended - Easiest) ⭐

1. **Create `.env` file** in `afroken_llm_backend/` directory:
   ```bash
   DATABASE_URL=sqlite:///./afroken_local.db
   ENV=development
   ```

2. **Restart your backend server**

That's it! SQLite will automatically create the database file.

---

### Option 2: Fix PostgreSQL Connection

If you want to use PostgreSQL, change the hostname from `postgres` to `localhost`:

1. **Create `.env` file** in `afroken_llm_backend/` directory:
   ```bash
   DATABASE_URL=postgresql://afroken:11403775411@localhost:5432/afroken_llm_db
   ENV=development
   ```

2. **Make sure PostgreSQL is running** on your machine

3. **Restart your backend server**

---

## How to Create .env File

### On Windows (PowerShell):
```powershell
cd afroken_llm_backend
@"
DATABASE_URL=sqlite:///./afroken_local.db
ENV=development
"@ | Out-File -FilePath .env -Encoding utf8
```

### On Windows (Command Prompt):
```cmd
cd afroken_llm_backend
echo DATABASE_URL=sqlite:///./afroken_local.db > .env
echo ENV=development >> .env
```

### Or manually:
1. Open `afroken_llm_backend/` folder
2. Create a new file named `.env` (with the dot at the beginning)
3. Add these lines:
   ```
   DATABASE_URL=sqlite:///./afroken_local.db
   ENV=development
   ```

---

## Test Database Connection

After creating the `.env` file, test the connection:

```powershell
cd afroken_llm_backend
python test_db_connection.py
```

You should see:
```
✅ Database is available!
✅ Basic query successful!
✅ Database connection test PASSED!
```

---

## Verify It Works

1. **Restart your backend server**
2. **Check console** - should see "✓ Database initialized"
3. **Try uploading a PDF** - should work now!

