# RAG Toolchain Runbook

## Quick Start

### 1. Setup Environment

```bash
cd afroken_llm_backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements_local.txt
```

### 2. Run Full Pipeline

**Linux/Mac:**
```bash
chmod +x run_local.sh
./run_local.sh
```

**Windows (PowerShell):**
```powershell
# Run steps manually:
python fetch_and_extract.py urls.txt
python chunk_and_write_md.py
python index_faiss.py
uvicorn app.main:app --reload --port 8000
```

### 3. Test Chat Endpoint

```bash
curl -X POST http://127.0.0.1:8000/api/v1/chat/messages \
  -H "Content-Type: application/json" \
  -d '{"message": "How do I get a KRA PIN?", "language": "en"}'
```

## File Locations

- **FAISS Index:** `afroken_llm_backend/faiss_index.idx` (or `.npy` for Python fallback)
- **Document Map:** `afroken_llm_backend/doc_map.json`
- **Markdown Corpus:** `data/docs/*.md` (repo root)
- **Raw Files:** `afroken_llm_backend/raw/*.html` and `*.txt`

## Expected Output

After running the pipeline:
- `raw/fetch_manifest.json` - List of fetched URLs
- `data/docs/*.md` - Chunked Markdown files (15-30 files typical)
- `faiss_index.idx` or `faiss_index.npy` - Vector index
- `doc_map.json` - Document metadata mapping

## Troubleshooting

- **FAISS fails on Windows:** Automatic fallback to NumPy - no action needed
- **Index not found:** Run `python index_faiss.py`
- **Empty results:** Check `data/docs/` has `.md` files
- **CORS errors:** Update `app/main.py` CORS settings

## Next Steps

1. Add more URLs to `urls.txt`
2. Re-run pipeline to update corpus
3. Configure `LLM_ENDPOINT` for full RAG experience
4. Test with frontend at `http://localhost:5173`

