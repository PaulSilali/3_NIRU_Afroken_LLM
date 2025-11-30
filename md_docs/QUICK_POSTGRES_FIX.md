# Quick PostgreSQL Fix

## Current Error
```
503 Service Unavailable
password authentication failed for user "afroken"
```

## Quick Fix (Choose One)

### Option 1: Create User and Database (Recommended)

**Step 1: Connect to PostgreSQL**
```powershell
psql -U postgres
```

**Step 2: Run these SQL commands**
```sql
-- Create user
CREATE USER afroken WITH PASSWORD '11403775411';

-- Create database
CREATE DATABASE afroken_llm_db OWNER afroken;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE afroken_llm_db TO afroken;

-- Connect to database
\c afroken_llm_db

-- Grant schema privileges
GRANT ALL ON SCHEMA public TO afroken;

-- Exit
\q
```

**Step 3: Restart backend server**

---

### Option 2: Use Default postgres User

**Step 1: Update `.env` file**
```bash
DATABASE_URL=postgresql+psycopg2://postgres:YOUR_POSTGRES_PASSWORD@localhost:5432/afroken_llm_db
```
(Replace `YOUR_POSTGRES_PASSWORD` with your actual PostgreSQL password)

**Step 2: Create database**
```powershell
psql -U postgres -c "CREATE DATABASE afroken_llm_db;"
```

**Step 3: Restart backend server**

---

### Option 3: Check PostgreSQL Service

**Windows:**
```powershell
# Check if PostgreSQL is running
Get-Service -Name postgresql*

# Start PostgreSQL if stopped
net start postgresql-x64-15  # Replace 15 with your version
```

**Or use Services:**
1. Press `Win + R`
2. Type `services.msc`
3. Find "PostgreSQL" service
4. Right-click → Start (if stopped)

---

## Verify Fix

After fixing, test connection:
```powershell
python test_pdf_upload.py
```

You should see:
```
✅ PostgreSQL database is available!
✅ Database connection successful!
```

---

## After Fix

1. **Restart backend server** (important!)
2. **Upload PDF** through admin dashboard
3. **Check Processing Jobs** - job should appear
4. **Verify in database** - job saved in `processingjob` table

---

## Still Having Issues?

Run diagnostic:
```powershell
python setup_postgres.py
```

This will show detailed setup instructions.

