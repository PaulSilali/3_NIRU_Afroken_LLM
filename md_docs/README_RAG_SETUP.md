# RAG Ingestion and Indexing Setup

This document describes how to set up and use the local RAG (Retrieval-Augmented Generation) toolchain for AfroKen LLM.

## Overview

The RAG system:
1. Fetches content from official government websites
2. Extracts and chunks text into Markdown files
3. Builds a FAISS vector index for fast similarity search
4. Provides fallback retrieval when LLM endpoint is not configured

## Directory Structure

```
afroken_llm_backend/
├── urls.txt                    # List of URLs to fetch
├── fetch_and_extract.py       # Fetch and extract script
├── chunk_and_write_md.py      # Chunk and write Markdown
├── index_faiss.py             # Build FAISS index
├── embeddings_fallback.py     # Embedding helper
├── faiss_index.idx            # FAISS index (generated)
├── doc_map.json               # Document metadata (generated)
└── raw/                       # Raw HTML/text files
    └── fetch_manifest.json

data/
└── docs/                      # Generated Markdown files
    └── *.md
```

## Setup Steps

### 1. Install Dependencies

```bash
cd afroken_llm_backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements_local.txt
```

**Note for Windows users:** If `faiss-cpu` fails to install, the system will automatically fall back to pure Python cosine similarity using NumPy.

### 2. Configure URLs

Edit `afroken_llm_backend/urls.txt` to add official government URLs you want to index:

```
# Add more official pages below. Do not add private or login-protected urls.

# KRA
https://www.kra.go.ke/services/pin
https://itax.kra.go.ke/itax/portal

# Add more URLs here...
```

**Important:** Only add public, non-login-protected URLs. The script checks `robots.txt` before fetching.

### 3. Run Ingestion Pipeline

**Option A: Use the shell script (recommended):**
```bash
chmod +x run_local.sh
./run_local.sh
```

**Option B: Run steps manually:**
```bash
# Step 1: Fetch URLs
python fetch_and_extract.py urls.txt

# Step 2: Chunk and write Markdown
python chunk_and_write_md.py

# Step 3: Build FAISS index
python index_faiss.py
```

### 4. Apply Chat Route Patch

The chat route needs to be updated to use the FAISS fallback. See `patch_chat_fallback.txt` for exact instructions.

**Quick patch:** Copy the code from `patch_chat_fallback.txt` and update `app/api/routes/chat.py` accordingly.

## Testing

### Test the Chat Endpoint

```bash
# Start backend (if not already running)
uvicorn app.main:app --reload --port 8000

# Test with curl
curl -X POST http://127.0.0.1:8000/api/v1/chat/messages \
  -H "Content-Type: application/json" \
  -d '{"message": "How do I get a KRA PIN?", "language": "en"}'
```

**Expected response (FAISS fallback):**
```json
{
  "reply": "**KRA PIN Registration**\n[excerpt from document]...",
  "citations": [
    {
      "title": "KRA PIN Registration Process",
      "filename": "001_kra_pin_registration.md",
      "source": "https://www.kra.go.ke/services/pin"
    }
  ]
}
```

## Configuration

### Environment Variables

- `EMBEDDING_ENDPOINT`: If set, uses HTTP endpoint for embeddings instead of local model
- `LLM_ENDPOINT`: If set, uses LLM for answer generation
- `OPENAI_API_KEY`: If set with `LLM_ENDPOINT`, enables OpenAI integration

**FAISS Fallback:** When neither `LLM_ENDPOINT` nor `OPENAI_API_KEY` is set, the system returns top-k retrieved documents instead of LLM-generated answers.

### Using OpenAI or Remote LLM

1. Set `LLM_ENDPOINT` in your `.env` file:
   ```
   LLM_ENDPOINT=https://your-llm-endpoint.com/chat
   ```

2. Or set `OPENAI_API_KEY`:
   ```
   OPENAI_API_KEY=sk-...
   ```

3. Restart the backend to apply changes.

## Managing the Corpus

### View Generated Documents

Documents are stored in `data/docs/` (repo root). Each file is a Markdown document with YAML front-matter.

### Clean and Rebuild

```bash
# Remove generated files
rm -rf data/docs/*.md
rm -rf afroken_llm_backend/raw/*
rm -f afroken_llm_backend/faiss_index.idx
rm -f afroken_llm_backend/faiss_index.npy
rm -f afroken_llm_backend/doc_map.json

# Rebuild
./run_local.sh
```

### Update Specific URLs

Edit `urls.txt` and re-run:
```bash
python fetch_and_extract.py urls.txt --force  # Re-fetch existing URLs
python chunk_and_write_md.py
python index_faiss.py
```

## Security & Ethics

- **Robots.txt:** The fetcher respects `robots.txt` and skips disallowed URLs
- **Rate Limiting:** Default 1.5s delay between requests (configurable)
- **No Copyrighted Content:** Only short excerpts and summaries are stored
- **Public URLs Only:** Do not add login-protected or private URLs

## Troubleshooting

### FAISS Installation Fails (Windows)

The system automatically falls back to pure Python cosine similarity. No action needed.

### Index Not Found Error

Ensure you've run the indexing pipeline:
```bash
python index_faiss.py
```

### Empty Results

- Check that `data/docs/` contains `.md` files
- Verify `doc_map.json` exists and has entries
- Check backend logs for errors

### CORS Errors (Frontend)

Ensure `app/main.py` allows your frontend origin:
```python
allow_origins=["http://localhost:5173", "http://localhost:3000"]
```

## Next Steps

1. Add more URLs to `urls.txt`
2. Run ingestion pipeline
3. Test chat endpoint
4. Configure LLM endpoint for full RAG experience
5. Monitor and update corpus regularly

