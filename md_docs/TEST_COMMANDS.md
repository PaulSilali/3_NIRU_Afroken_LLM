# Test Commands and Verification

## Setup and Installation

```bash
# 1. Create and activate virtual environment
cd afroken_llm_backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements_local.txt
```

**Expected output:** All packages install successfully. If `faiss-cpu` fails on Windows, that's OK - Python fallback will be used.

## Step-by-Step Verification

### Step 1: Fetch URLs

```bash
python fetch_and_extract.py urls.txt
```

**Expected output:**
```
Found 8 URLs to fetch
[1/8] Processing https://www.kra.go.ke/services/pin
Saved 001_kra_go_ke_services_pin_abc123.html and 001_kra_go_ke_services_pin_abc123.txt
...
Fetch complete. Manifest saved to raw/fetch_manifest.json
Processed 8 URLs
```

**Verify:** Check `afroken_llm_backend/raw/fetch_manifest.json` exists with entries.

### Step 2: Chunk and Write Markdown

```bash
python chunk_and_write_md.py
```

**Expected output:**
```
Processing 8 entries from manifest...
Created 001_kra_pin_registration.md
Created 002_ecitizen_home.md
...
Chunking complete. Created 15 Markdown files in data/docs
```

**Verify:** Check `data/docs/` contains `.md` files with YAML front-matter.

### Step 3: Build FAISS Index

```bash
python index_faiss.py
```

**Expected output:**
```
Found 15 Markdown files
Loading sentence transformer model...
Processing [1/15] 001_kra_pin_registration.md
...
Computing embeddings...
Embeddings shape: (15, 384)
Building FAISS index...
FAISS index saved to afroken_llm_backend/faiss_index.idx
Document map saved to afroken_llm_backend/doc_map.json

Index complete:
  - Documents: 15
  - Embedding dimension: 384
  - Index type: FAISS
```

**Verify:** 
- `afroken_llm_backend/faiss_index.idx` exists (or `.npy` if FAISS unavailable)
- `afroken_llm_backend/doc_map.json` exists with 15 entries

### Step 4: Start Backend

```bash
uvicorn app.main:app --reload --port 8000
```

**Expected output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
AfroKen backend startup complete
INFO:     Application startup complete.
```

**Verify:** No database errors (if DB not configured, that's OK for FAISS fallback).

### Step 5: Test Chat Endpoint

```bash
curl -X POST http://127.0.0.1:8000/api/v1/chat/messages \
  -H "Content-Type: application/json" \
  -d '{"message": "How do I get a KRA PIN?", "language": "en"}'
```

**Expected response (FAISS fallback):**
```json
{
  "reply": "**KRA PIN Registration Process**\nTo register for a KRA PIN, visit www.kra.go.ke...",
  "citations": [
    {
      "title": "KRA PIN Registration Process",
      "filename": "001_kra_pin_registration.md",
      "source": "https://www.kra.go.ke/services/pin"
    }
  ]
}
```

**Alternative test (Swahili):**
```bash
curl -X POST http://127.0.0.1:8000/api/v1/chat/messages \
  -H "Content-Type: application/json" \
  -d '{"message": "Ninawezaje kupata PIN ya KRA?", "language": "sw"}'
```

## Troubleshooting

### Index Not Found Error

```bash
# Rebuild index
python index_faiss.py
```

### Empty Results

1. Check `data/docs/` has `.md` files
2. Verify `doc_map.json` has entries
3. Check backend logs for errors

### FAISS Import Error (Windows)

This is expected. The system will use Python fallback automatically. Check for `faiss_index.npy` instead of `.idx`.

### CORS Errors

Update `app/main.py` CORS settings to include your frontend origin.

