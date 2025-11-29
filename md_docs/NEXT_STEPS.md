# Next Steps: Connect Frontend to Backend

## ✅ Current Status
- Frontend is running
- Backend RAG toolchain is ready
- Frontend API updated to call real backend

## 🚀 Step-by-Step Instructions

### Step 1: Start the Backend Server

Open a **new terminal** (keep frontend running) and run:

```bash
cd afroken_llm_backend

# Activate virtual environment
source venv/bin/activate  # Windows: venv\Scripts\activate

# Start the backend
uvicorn app.main:app --reload --port 8000
```

**Expected output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
✓ RAG resources preloaded  # (if index exists)
```

### Step 2: Build RAG Index (If Not Done)

If you see "RAG index not found" in the logs, build it:

```bash
# In the backend directory
python fetch_and_extract.py urls.txt
python chunk_and_write_md.py
python index_faiss.py
```

**Or use the shell script (Linux/Mac):**
```bash
chmod +x run_local.sh
./run_local.sh
```

### Step 3: Verify Backend is Running

Test the backend directly:

```bash
curl http://127.0.0.1:8000/health
```

Should return:
```json
{"status": "healthy", "service": "AfroKen Backend", "version": "0.1.0"}
```

### Step 4: Test Chat Endpoint

```bash
curl -X POST http://127.0.0.1:8000/api/v1/chat/messages \
  -H "Content-Type: application/json" \
  -d '{"message": "How do I get a KRA PIN?", "language": "en"}'
```

**Expected response (FAISS fallback):**
```json
{
  "reply": "**KRA PIN Registration Process**\n[excerpt from document]...",
  "citations": [
    {
      "title": "...",
      "filename": "...",
      "source": "https://..."
    }
  ]
}
```

### Step 5: Test Frontend Connection

1. **Open your frontend** in browser (usually `http://localhost:5173`)
2. **Open browser DevTools** (F12) → Network tab
3. **Click the chat button** and send a message
4. **Check Network tab** for:
   - Request to `http://localhost:8000/api/v1/chat/messages`
   - Status: 200 OK
   - Response with `reply` and `citations`

### Step 6: Verify CORS is Working

If you see CORS errors in browser console:
- Check that backend is running on port 8000
- Verify `app/main.py` has your frontend origin in CORS settings
- Frontend should be on `http://localhost:5173` (Vite default)

## 🔧 Troubleshooting

### Issue: "Network Error" or "Failed to fetch"

**Solution:**
1. Check backend is running: `curl http://127.0.0.1:8000/health`
2. Check frontend is calling correct URL (check browser console)
3. Verify CORS settings in `app/main.py`

### Issue: "RAG index not found"

**Solution:**
```bash
cd afroken_llm_backend
python index_faiss.py
```

### Issue: Frontend still using mocks

**Solution:**
- Check browser console for API errors
- Verify `VITE_API_BASE_URL` is not set to empty
- Frontend will auto-fallback to mocks if backend fails

### Issue: Field name mismatch errors

**Solution:**
- Frontend now handles the transformation automatically
- Backend returns `reply`, frontend expects `answer` - transformation added
- Backend returns `language`, frontend sends `lang` - fixed in API call

## ✅ Success Indicators

You'll know it's working when:
1. ✅ Backend logs show: "✓ RAG resources preloaded"
2. ✅ Browser Network tab shows successful POST to `/api/v1/chat/messages`
3. ✅ Chat responses come from your RAG corpus (not mocks)
4. ✅ Citations appear with real document titles and sources
5. ✅ Response time is fast (~50-200ms, not 1s+)

## 🎯 Quick Test Commands

```bash
# Terminal 1: Backend
cd afroken_llm_backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000

# Terminal 2: Test (in new terminal)
curl -X POST http://127.0.0.1:8000/api/v1/chat/messages \
  -H "Content-Type: application/json" \
  -d '{"message": "How do I register for NHIF?", "language": "en"}'
```

## 📝 Environment Variables (Optional)

Create `afroken_llm_frontend/.env` if you want to customize:

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_USE_MOCK=false
```

## 🚀 You're Ready!

Once backend is running and frontend connects:
- Chat will use real RAG retrieval
- Responses come from your indexed documents
- Citations show actual sources
- System is production-ready!

