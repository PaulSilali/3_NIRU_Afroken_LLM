# Quick Start Guide

## Server Startup

### 1. Install Dependencies
```bash
cd afroken_llm_backend
pip install -r requirements.txt
```

### 2. Configure Environment
Ensure `.env` file exists with:
```env
DATABASE_URL=postgresql://afroken:11403775411@localhost:5432/afroken_llm_db
JWT_SECRET=your-secret-key
ENV=development
```

**Note**: If using Docker, change `localhost` to `postgres` in DATABASE_URL.

### 3. Initialize Database
```bash
# Connect to PostgreSQL and run schema
psql -U afroken -d afroken_llm_db -f ../afroken_llm_database/create_schema_without_pgvector.sql
```

### 4. Start Server
```bash
# Windows PowerShell
$env:PYTHONIOENCODING='utf-8'
python -m uvicorn app.main:app --reload --port 8000

# Linux/Mac
PYTHONIOENCODING=utf-8 python -m uvicorn app.main:app --reload --port 8000
```

### 5. Verify Server
```bash
curl http://localhost:8000/health
# Should return: {"status":"healthy","service":"AfroKen Backend","version":"0.1.0"}
```

## Frontend Connection

### 1. Start Frontend
```bash
cd afroken_llm_frontend
npm install
npm run dev
```

### 2. Configure API URL
Create `.env` file in frontend directory:
```env
VITE_API_BASE_URL=http://localhost:8000
```

### 3. Test Connection
- Open browser to `http://localhost:5173`
- Open browser console (F12)
- Check for API connection errors
- Test chat interface

## Testing Endpoints

### Chat Endpoint
```bash
curl -X POST http://localhost:8000/api/v1/chat/messages \
  -H "Content-Type: application/json" \
  -d '{"message": "How do I register for NHIF?", "language": "sw"}'
```

### Admin - Upload PDF
```bash
curl -X POST http://localhost:8000/api/v1/admin/documents/upload-pdf \
  -F "file=@test.pdf" \
  -F "category=test"
```

### Admin - Scrape URL
```bash
curl -X POST http://localhost:8000/api/v1/admin/documents/scrape-url \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "category": "test"}'
```

### Check Job Status
```bash
curl http://localhost:8000/api/v1/admin/jobs/{job_id}
```

## Troubleshooting

### Server Won't Start
1. Check Python version: `python --version` (should be 3.11+)
2. Check dependencies: `pip list | Select-String "fastapi|pydantic|sqlmodel"`
3. Check for port conflicts: `netstat -an | Select-String "8000"`

### Database Connection Errors
1. Verify PostgreSQL is running
2. Check DATABASE_URL in `.env`
3. Test connection: `psql -U afroken -d afroken_llm_db -c "SELECT 1"`

### Frontend Can't Connect
1. Check CORS settings in `app/main.py`
2. Verify `VITE_API_BASE_URL` in frontend `.env`
3. Check browser console for errors
4. Verify backend is running on port 8000

### RAG Not Working
1. Check if `doc_map.json` and `faiss_index.idx` exist in backend root
2. Check console output for RAG loading messages
3. Verify embeddings are being generated

## Database Tables

See `DATABASE_TABLES.md` for complete documentation.

### Key Tables:
- **users**: User accounts
- **conversations**: Chat sessions  
- **messages**: Chat messages
- **documents**: RAG documents
- **processing_jobs**: Background jobs
- **services**: Government services
- **huduma_centres**: Service locations

## Next Steps

1. ✅ Server starts successfully
2. ⏳ Test chat functionality
3. ⏳ Test admin dashboard
4. ⏳ Verify database storage
5. ⏳ Test PDF upload
6. ⏳ Test URL scraping
7. ⏳ Verify frontend-backend integration

