# Complete System Startup Guide

This guide will help you start the backend, build the RAG corpus, and connect it to the frontend.

## Prerequisites

1. ✅ Python 3.10+ installed
2. ✅ Virtual environment created
3. ✅ Dependencies installed
4. ✅ Frontend ready (in separate terminal)

## Step-by-Step Startup

### Step 1: Activate Virtual Environment

```bash
# Windows PowerShell
.\venv\Scripts\Activate.ps1

# Windows CMD
venv\Scripts\activate.bat

# Linux/Mac
source venv/bin/activate
```

### Step 2: Install Dependencies (if not done)

```bash
pip install -r requirements.txt
pip install -r config/requirements_local.txt
```

### Step 3: Build RAG Corpus

#### Option A: Use the automated script (Recommended)

```bash
# This will check if index exists, if not, build it automatically
./run_local.sh
```

#### Option B: Manual step-by-step

```bash
# Step 3a: Pre-check robots.txt (optional but recommended)
python scripts/rag/check_robots_report.py config/urls.txt

# Step 3b: Fetch and extract content from URLs
python scripts/rag/fetch_and_extract.py config/urls.txt

# Step 3c: Chunk text into Markdown files
python scripts/rag/chunk_and_write_md.py

# Step 3d: Build FAISS index
python scripts/rag/index_faiss.py
```

### Step 4: Start Backend Server

```bash
# If using run_local.sh, backend starts automatically
# Otherwise, start manually:
uvicorn app.main:app --reload --port 8000
```

### Step 5: Start Frontend (in separate terminal)

```bash
cd ../afroken_llm_frontend
npm install  # if first time
npm run dev
```

### Step 6: Test the Connection

1. Open browser: http://localhost:5173 (or your frontend port)
2. Click chat button
3. Send a test message: "How do I get a KRA PIN?"
4. Check browser DevTools → Network tab for API calls

## Verification Checklist

- [ ] Backend running on http://localhost:8000
- [ ] Backend health check: http://localhost:8000/health
- [ ] FAISS index exists: `faiss_index.idx` or `faiss_index.npy`
- [ ] Document map exists: `doc_map.json`
- [ ] Frontend running on http://localhost:5173
- [ ] Chat sends messages to backend
- [ ] Backend returns responses with citations

## Troubleshooting

### Issue: "RAG index not found"
**Solution**: Run the RAG pipeline (Step 3)

### Issue: "Module not found" errors
**Solution**: 
```bash
pip install -r requirements.txt
pip install -r config/requirements_local.txt
```

### Issue: Frontend can't connect to backend
**Solution**: 
- Check CORS settings in `app/main.py`
- Verify backend is running on port 8000
- Check browser console for errors

### Issue: Chat returns empty responses
**Solution**:
- Verify `doc_map.json` exists and has content
- Check backend logs for errors
- Test API directly: `curl http://localhost:8000/api/v1/chat/messages -X POST -H "Content-Type: application/json" -d '{"message":"test","language":"en"}'`

## Quick Test Commands

```bash
# Test backend health
curl http://localhost:8000/health

# Test chat endpoint
curl -X POST http://localhost:8000/api/v1/chat/messages \
  -H "Content-Type: application/json" \
  -d '{"message":"How do I get a KRA PIN?","language":"en"}'
```

## Expected Output

When everything works:
- Backend logs show: "✓ RAG resources preloaded"
- Chat responses include document excerpts
- Citations appear with source URLs
- Response time is fast (~50-200ms)

