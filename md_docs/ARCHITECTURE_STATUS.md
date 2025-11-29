# Architecture Status: LLM, Embeddings, Storage Implementation

## 1. LLM Usage in Application

### Current Implementation Status: ⚠️ **OPTIONAL / FALLBACK**

**Where LLM is used:**
- **File:** `app/api/routes/chat.py` (lines 331-349)
- **Endpoint:** `POST /api/v1/chat/messages`
- **Configuration:** `LLM_ENDPOINT` environment variable

**Current Behavior:**
```python
# From chat.py
if settings.LLM_ENDPOINT:
    # Calls external LLM endpoint
    payload = {
        "system": "You are AfroKen LLM...",
        "documents": context,
        "user_message": req.message,
        "language": req.language,
    }
    res = await client.post(settings.LLM_ENDPOINT, json=payload)
else:
    # FALLBACK: Returns top-k retrieved documents (no LLM)
    # This is what's currently working
```

**Which LLM:**
- ❌ **NOT IMPLEMENTED:** Mistral/LLaMA-3 7B fine-tuned via LoRA
- ✅ **CURRENT:** External LLM endpoint (if configured) OR FAISS fallback
- ✅ **WORKING:** FAISS-based retrieval without LLM (returns document excerpts)

**Why Fine-Tune Mistral/LLaMA-3 7B?**
Based on the research paper you shared, fine-tuning would:
1. **Domain-Specific Understanding:** Better grasp of government services terminology
2. **Kenyan Languages:** Support for Swahili, Luo, Kalenjin, etc.
3. **Context-Aware Responses:** Generate natural language from retrieved documents
4. **Tool-Calling:** Enable action execution (not just information retrieval)

**Current Status:**
- ✅ **Working without LLM:** FAISS retrieval returns document excerpts
- ⚠️ **LLM Optional:** Can be added via `LLM_ENDPOINT` environment variable
- ❌ **Fine-Tuning Not Done:** No Mistral/LLaMA fine-tuning implemented

---

## 2. Sentence Transformers (Embeddings)

### Implementation Status: ✅ **FULLY IMPLEMENTED & WORKING**

**Where it's used:**
- **File:** `app/utils/embeddings_fallback.py`
- **Model:** `all-MiniLM-L6-v2` (384-dimensional embeddings)
- **Usage:** RAG indexing and query embedding

**Implementation Details:**
```python
# From embeddings_fallback.py
from sentence_transformers import SentenceTransformer

# Lazy-loaded global model
_model: Optional[SentenceTransformer] = None

def get_embedding(text: str) -> np.ndarray:
    """Returns 384-dimensional embedding vector"""
    if _model is None:
        _model = SentenceTransformer('all-MiniLM-L6-v2')
    embedding = _model.encode(text, convert_to_numpy=True)
    return embedding.astype(np.float32)  # Shape: (384,)
```

**Where it's used:**
1. **Indexing:** `scripts/rag/index_faiss.py` - Generates embeddings for all documents
2. **Query:** `app/api/routes/chat.py` - Embeds user queries for similarity search
3. **Fallback:** Works offline, no external API needed

**Status:** ✅ **WORKING** - Fully functional, cached for performance

---

## 3. Whisper ASR + Coqui TTS

### Implementation Status: ❌ **NOT IMPLEMENTED**

**Search Results:**
- ❌ No Whisper ASR code found
- ❌ No Coqui TTS code found
- ❌ No audio processing endpoints

**What Would Be Needed:**
1. **Whisper ASR (Speech-to-Text):**
   - Endpoint: `POST /api/v1/audio/transcribe`
   - Input: Audio file (WAV, MP3)
   - Output: Text transcript
   - Use case: Voice queries from mobile app

2. **Coqui TTS (Text-to-Speech):**
   - Endpoint: `POST /api/v1/audio/synthesize`
   - Input: Text + language code
   - Output: Audio file (WAV, MP3)
   - Use case: Audio responses for USSD/voice calls

**To Implement:**
```python
# Would need to add:
# requirements.txt
openai-whisper  # or faster-whisper
TTS  # Coqui TTS library

# New endpoints in app/api/routes/audio.py
@router.post("/transcribe")
async def transcribe_audio(file: UploadFile):
    # Use Whisper to convert audio -> text
    pass

@router.post("/synthesize")
async def synthesize_speech(text: str, language: str = "sw"):
    # Use Coqui TTS to convert text -> audio
    pass
```

**Status:** ❌ **NOT IMPLEMENTED** - Would be useful for voice/USSD features

---

## 4. PostgreSQL Usage

### Implementation Status: ⚠️ **OPTIONAL / PARTIALLY WORKING**

**What PostgreSQL is Used For:**

### A. **Citizen Logs & Metadata** ✅ **IMPLEMENTED**

**Tables:**
1. **`user`** - Citizen/user accounts
   - `id`, `phone_number`, `email`, `preferred_language`, `is_active`, `created_at`

2. **`conversation`** - Chat conversation threads
   - `id`, `user_id`, `service_category`, `status`, `summary`, `sentiment`, `created_at`

3. **`message`** - Individual messages in conversations
   - `id`, `conversation_id`, `role`, `content`, `language`, `citations`, `tokens_used`, `cost_usd`, `created_at`

**File:** `app/models.py` (lines 14-86)

**Status:** ✅ **Schema defined** - Tables created on startup if DB available

### B. **Document Storage with pgvector** ✅ **IMPLEMENTED**

**Table:** `documents`
- `id`, `title`, `content`, `source_url`, `document_type`, `category`
- `embedding vector(384)` - **pgvector column for similarity search**
- `metadata JSONB` - Additional metadata
- `is_indexed`, `created_at`

**Files:**
- Schema: `app/models.py` (lines 89-111)
- Vector search: `app/services/rag_service.py`
- DB init: `scripts/db/init_db.py`

**Vector Search Implementation:**
```python
# From rag_service.py
def vector_search(embedding: List[float], top_k: int = 5):
    query = text("""
        SELECT id, title, content, source_url
        FROM documents
        ORDER BY embedding <#> :q  -- pgvector cosine distance
        LIMIT :k
    """)
    # Returns top-k similar documents
```

**Current Status:**
- ✅ **Schema Ready:** All tables defined
- ✅ **pgvector Support:** Vector search implemented
- ⚠️ **Optional:** Works without DB (uses FAISS fallback)
- ⚠️ **Not Currently Used:** Chat endpoint uses FAISS, not PostgreSQL

**Why Not Currently Used:**
- Chat endpoint (`chat.py`) uses FAISS index files (`faiss_index.idx`, `doc_map.json`)
- PostgreSQL vector search is available but not called in current flow
- Fallback to SQLite if PostgreSQL unavailable

---

## 5. MinIO Usage

### Implementation Status: ⚠️ **IMPLEMENTED BUT NOT ACTIVELY USED**

**What MinIO is Used For:**

### A. **Documents Storage** ✅ **IMPLEMENTED**

**File:** `app/utils/storage.py`

**Functions:**
```python
def upload_bytes(bucket: str, object_name: str, data: bytes) -> str:
    """Upload document to MinIO, returns URL"""
    client.put_object(bucket, object_name, io.BytesIO(data))
    return f"{settings.MINIO_ENDPOINT}/{bucket}/{object_name}"
```

**Where it's used:**
- `app/api/routes/admin.py` - Document upload endpoint
- Stores raw PDFs, HTML files, etc.

**Status:** ✅ **Code exists** - But not actively used in current RAG pipeline

### B. **Audio Interactions** ❌ **NOT IMPLEMENTED**

**Expected Use:**
- Store audio recordings from voice queries
- Store synthesized TTS audio responses
- Archive USSD voice interactions

**Status:** ❌ **Not implemented** - Would need audio endpoints first

**Current RAG Pipeline:**
- Documents stored in: `data/docs/` (Markdown files)
- Raw files in: `data/raw/` (HTML, text files)
- **NOT using MinIO** for current ingestion pipeline

---

## Summary: Implementation Status

| Component | Status | Notes |
|-----------|--------|-------|
| **LLM (Mistral/LLaMA-3)** | ❌ Not Implemented | Optional via `LLM_ENDPOINT`, currently uses FAISS fallback |
| **Fine-Tuning (LoRA)** | ❌ Not Done | Would improve domain-specific responses |
| **Sentence Transformers** | ✅ **WORKING** | `all-MiniLM-L6-v2`, fully functional |
| **Whisper ASR** | ❌ Not Implemented | Would enable voice queries |
| **Coqui TTS** | ❌ Not Implemented | Would enable audio responses |
| **PostgreSQL (logs)** | ⚠️ Optional | Schema ready, works without DB |
| **PostgreSQL (pgvector)** | ⚠️ Optional | Implemented but not used (FAISS preferred) |
| **MinIO (documents)** | ⚠️ Optional | Code exists, not used in current pipeline |
| **MinIO (audio)** | ❌ Not Implemented | Would need audio endpoints first |

---

## What's Actually Working Right Now

### ✅ **Fully Functional:**
1. **FAISS-based RAG** - Document retrieval without LLM
2. **Sentence Transformers** - Embedding generation
3. **Chat Endpoint** - Returns document excerpts with citations
4. **Local Pipeline** - URL scraping → Markdown → FAISS indexing

### ⚠️ **Optional/Not Used:**
1. **PostgreSQL** - Available but chat uses FAISS
2. **MinIO** - Code exists but pipeline uses local files
3. **LLM Endpoint** - Can be configured but not required

### ❌ **Missing:**
1. **Fine-Tuned LLM** - Would improve response quality
2. **Whisper ASR** - Voice input support
3. **Coqui TTS** - Audio output support

---

## Recommendations

### Short-term (Keep Current Approach):
- ✅ Current FAISS + Sentence Transformers is working well
- ✅ No LLM needed for MVP
- ✅ Local file storage is sufficient

### Medium-term (If Adding Features):
1. **Add Whisper ASR** - Enable voice queries
2. **Add Coqui TTS** - Enable audio responses
3. **Use PostgreSQL** - For conversation logging (currently schema only)

### Long-term (If Scaling):
1. **Fine-Tune LLM** - Better response quality
2. **Use MinIO** - For document archival
3. **Use pgvector** - For larger-scale vector search

---

## Answer to Your Questions

1. **Where do we use LLM?** 
   - Optional in `chat.py` via `LLM_ENDPOINT` env var
   - Currently NOT using LLM (FAISS fallback works)

2. **Which LLM?**
   - Document mentions Mistral/LLaMA-3 7B, but **NOT IMPLEMENTED**
   - Currently: External endpoint (if configured) OR no LLM

3. **Why fine-tune?**
   - Domain-specific understanding (government services)
   - Kenyan language support
   - Better response quality

4. **Whisper ASR + Coqui TTS?**
   - ❌ **NOT IMPLEMENTED** - Would need to add

5. **Sentence Transformers?**
   - ✅ **FULLY IMPLEMENTED** - `all-MiniLM-L6-v2`, working perfectly

6. **PostgreSQL for storage?**
   - ✅ Schema ready for citizen logs, metadata
   - ⚠️ pgvector implemented but not used (FAISS preferred)
   - ⚠️ Works without DB (SQLite fallback)

7. **MinIO for documents/audio?**
   - ⚠️ Code exists for documents, but not used in pipeline
   - ❌ Audio storage not implemented (no audio endpoints)

8. **Is implementation working?**
   - ✅ **YES** - FAISS RAG is fully functional
   - ⚠️ **PARTIALLY** - PostgreSQL/MinIO optional, not required
   - ❌ **NO** - LLM fine-tuning, ASR, TTS not implemented

