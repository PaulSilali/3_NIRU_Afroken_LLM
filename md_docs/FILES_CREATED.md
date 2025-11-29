# RAG Toolchain - Files Created

## Summary

Complete RAG ingestion and indexing toolchain created for AfroKen LLM.

## Created Files

### Core Scripts
1. **`urls.txt`** - Template list of official government URLs to fetch
2. **`fetch_and_extract.py`** - Fetches URLs, respects robots.txt, extracts text
3. **`chunk_and_write_md.py`** - Chunks text into ~200-word Markdown files
4. **`index_faiss.py`** - Builds FAISS vector index from Markdown corpus
5. **`embeddings_fallback.py`** - Embedding helper with local model fallback
6. **`run_local.sh`** - Shell script to run full pipeline (Unix/Mac)

### Configuration
7. **`requirements_local.txt`** - Additional Python dependencies for RAG

### Documentation
8. **`README_RAG_SETUP.md`** - Complete setup and usage guide
9. **`RUNBOOK.md`** - Quick start runbook
10. **`TEST_COMMANDS.md`** - Step-by-step verification commands
11. **`FRONTEND_HINTS.md`** - Frontend integration guidance
12. **`SAFETY_SYSTEM_PROMPT.md`** - LLM safety prompt guidelines
13. **`patch_chat_fallback.txt`** - Instructions for chat route updates

### Modified Files
14. **`app/api/routes/chat.py`** - Updated with FAISS fallback logic

## Directory Structure

```
afroken_llm_backend/
├── urls.txt                    # URL list
├── fetch_and_extract.py       # Fetch script
├── chunk_and_write_md.py      # Chunk script
├── index_faiss.py              # Index script
├── embeddings_fallback.py     # Embedding helper
├── run_local.sh               # Pipeline script
├── requirements_local.txt     # Dependencies
├── faiss_index.idx            # Generated: FAISS index
├── faiss_index.npy            # Generated: NumPy fallback
├── doc_map.json               # Generated: Document metadata
├── raw/                       # Generated: Raw HTML/text
│   └── fetch_manifest.json
└── app/api/routes/chat.py     # Modified: FAISS fallback

data/                          # Generated: Markdown corpus
└── docs/
    └── *.md
```

## Key Features

- ✅ Robots.txt compliance
- ✅ Rate limiting (1.5s default)
- ✅ FAISS indexing with Python fallback
- ✅ Automatic category detection
- ✅ YAML front-matter in Markdown files
- ✅ FAISS fallback when LLM not configured
- ✅ Windows-compatible (NumPy fallback)

## FAISS Index Location

**Primary:** `afroken_llm_backend/faiss_index.idx`  
**Fallback:** `afroken_llm_backend/faiss_index.npy` (if FAISS unavailable)

## Quick Commands

```bash
# Full pipeline
./run_local.sh  # or run steps manually

# Individual steps
python fetch_and_extract.py urls.txt
python chunk_and_write_md.py
python index_faiss.py
uvicorn app.main:app --reload --port 8000

# Test
curl -X POST http://127.0.0.1:8000/api/v1/chat/messages \
  -H "Content-Type: application/json" \
  -d '{"message": "How do I get a KRA PIN?", "language": "en"}'
```

## Git Commands

```bash
git add afroken_llm_backend/urls.txt
git add afroken_llm_backend/fetch_and_extract.py
git add afroken_llm_backend/chunk_and_write_md.py
git add afroken_llm_backend/index_faiss.py
git add afroken_llm_backend/embeddings_fallback.py
git add afroken_llm_backend/run_local.sh
git add afroken_llm_backend/requirements_local.txt
git add afroken_llm_backend/README_RAG_SETUP.md
git add afroken_llm_backend/RUNBOOK.md
git add afroken_llm_backend/TEST_COMMANDS.md
git add afroken_llm_backend/FRONTEND_HINTS.md
git add afroken_llm_backend/SAFETY_SYSTEM_PROMPT.md
git add afroken_llm_backend/patch_chat_fallback.txt
git add afroken_llm_backend/app/api/routes/chat.py
git commit -m "feat(rag): add local RAG ingestion & indexing toolchain"
```

