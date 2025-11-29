# Quick Start Guide - Complete System

## 🚀 Start Everything in 3 Steps

### Step 1: Activate Virtual Environment

```powershell
# In PowerShell (from afroken_llm_backend directory)
.\venv\Scripts\Activate.ps1
```

If you get an execution policy error, run:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Step 2: Start Backend (Automatically Builds RAG if Needed)

```powershell
# Option A: Use the PowerShell script (Recommended)
.\start_backend.ps1

# Option B: Use the bash script (if you have Git Bash/WSL)
./run_local.sh

# Option C: Manual commands
python scripts/rag/fetch_and_extract.py config/urls.txt
python scripts/rag/chunk_and_write_md.py
python scripts/rag/index_faiss.py
uvicorn app.main:app --reload --port 8000
```

### Step 3: Start Frontend (New Terminal)

```powershell
# Open a NEW terminal/PowerShell window
cd ..\afroken_llm_frontend
npm install  # Only if first time
npm run dev
```

## ✅ Verification

1. **Backend Health**: Open http://localhost:8000/health
   - Should return: `{"status": "healthy", ...}`

2. **Backend API Docs**: Open http://localhost:8000/docs
   - Should show Swagger UI

3. **Frontend**: Open http://localhost:5173 (or port shown in terminal)
   - Should show the AfroKen frontend

4. **Test Chat**: 
   - Click chat button
   - Send: "How do I get a KRA PIN?"
   - Should get response with citations

## 🔍 Troubleshooting

### "Module not found" errors
```powershell
pip install -r requirements.txt
pip install -r config/requirements_local.txt
```

### "RAG index not found" in logs
The startup script should build it automatically. If not:
```powershell
python scripts/rag/fetch_and_extract.py config/urls.txt
python scripts/rag/chunk_and_write_md.py
python scripts/rag/index_faiss.py
```

### Frontend can't connect
- Check backend is running: http://localhost:8000/health
- Check CORS in `app/main.py` includes your frontend port
- Check browser console (F12) for errors

### Chat returns empty
- Verify `doc_map.json` exists in backend root
- Check backend logs for errors
- Test API directly:
```powershell
curl -X POST http://localhost:8000/api/v1/chat/messages `
  -H "Content-Type: application/json" `
  -d '{\"message\":\"test\",\"language\":\"en\"}'
```

## 📊 Expected Output

**Backend logs should show:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
✓ RAG resources preloaded
AfroKen backend startup complete
```

**Chat should:**
- Return relevant document excerpts
- Include citations with source URLs
- Respond in < 1 second

## 🎯 Next Steps

Once everything is running:
1. Test various queries in the chat
2. Check citations are accurate
3. Monitor backend logs for any errors
4. Review `doc_map.json` to see indexed documents

