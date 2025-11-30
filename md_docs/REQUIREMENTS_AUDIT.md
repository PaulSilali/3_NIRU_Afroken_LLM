# Requirements.txt Audit Report

## Deep Scan Results

### ✅ Currently in requirements.txt (34 lines)

#### Core Framework
- fastapi>=0.104.0 ✅
- uvicorn[standard]>=0.23.0 ✅
- sqlmodel>=0.0.14 ✅
- pydantic>=2.0.0 ✅
- pydantic-settings>=2.0.0 ✅

#### Database
- asyncpg==0.27.0 ✅
- psycopg2-binary==2.9.7 ✅
- pgvector==0.4.1 ✅

#### Utilities
- python-dotenv==1.0.0 ✅
- httpx==0.24.1 ✅
- aiofiles==23.1.0 ✅
- python-jose==3.3.0 ✅
- passlib[bcrypt]==1.7.4 ✅

#### Background Tasks
- redis==4.6.0 ✅
- celery==5.3.1 ✅

#### Storage
- minio==7.1.11 ✅

#### Testing
- pytest==7.3.2 ✅

#### Monitoring
- prometheus-client==0.16.0 ✅

#### Audio Processing
- openai-whisper==20231117 ✅
- TTS==0.20.0 ✅

#### PDF Processing
- PyPDF2==3.0.1 ✅
- pdfplumber>=0.10.3 ✅
- pypdfium2>=4.18.0 ✅

#### ML/AI
- torch==2.1.0 ✅
- transformers==4.35.0 ✅
- sentence-transformers==2.2.2 ✅
- faiss-cpu==1.7.4 ✅
- numpy==1.24.3 ✅

---

## ❌ MISSING Dependencies Found

### Critical Missing (Used in Production Code)

1. **requests** ❌
   - **Used in**: 
     - `scripts/rag/fetch_and_extract.py` (line 29)
     - `scripts/rag/check_robots_report.py` (line 23)
   - **Purpose**: HTTP requests for URL scraping
   - **Status**: Installed locally but NOT in requirements.txt

2. **beautifulsoup4** ❌
   - **Used in**: 
     - `scripts/rag/fetch_and_extract.py` (line 30)
   - **Purpose**: HTML parsing and text extraction
   - **Status**: Installed locally but NOT in requirements.txt

3. **readability-lxml** ❌
   - **Used in**: 
     - `scripts/rag/fetch_and_extract.py` (line 31)
   - **Purpose**: Main content extraction (removes ads, nav, etc.)
   - **Status**: Installed locally but NOT in requirements.txt

4. **pyyaml** ❌
   - **Used in**: 
     - `scripts/rag/index_faiss.py` (line 24)
   - **Purpose**: Parsing YAML front-matter from Markdown files
   - **Status**: Installed locally but NOT in requirements.txt

5. **sqlalchemy** ❌
   - **Used in**: 
     - `app/api/routes/admin.py` (line 14)
     - `app/services/rag_service.py` (line 10)
     - `app/tasks/document_tasks.py` (line 5)
     - `app/db.py` (multiple lines)
     - `check_uploads.py` (line 106)
     - `test_db_connection.py` (line 18)
   - **Purpose**: Raw SQL queries, database operations
   - **Status**: Likely included as dependency of sqlmodel, but should be explicit

6. **python-multipart** ❌
   - **Used in**: FastAPI file uploads (implicit requirement)
   - **Purpose**: Required for FastAPI multipart/form-data (file uploads)
   - **Status**: NOT in requirements.txt but needed for PDF upload endpoint

---

## 📋 Recommended Additions

Add these to requirements.txt:

```txt
# Web scraping and HTML processing
requests>=2.32.0
beautifulsoup4>=4.13.0
readability-lxml>=0.8.1

# YAML processing
pyyaml>=6.0.0

# Database (explicit dependency)
sqlalchemy>=2.0.0

# FastAPI file uploads
python-multipart>=0.0.6
```

---

## 🔍 Additional Notes

### Dependencies That Are Transitive (but should be explicit)

1. **sqlalchemy** - Required by sqlmodel, but used directly in code
2. **python-multipart** - Required by FastAPI for file uploads

### Dependencies in config/requirements_local.txt

The file `config/requirements_local.txt` contains:
- requests
- beautifulsoup4
- readability-lxml
- pyyaml
- sqlalchemy
- python-multipart

**Recommendation**: Merge these into main `requirements.txt` for consistency.

---

## ✅ Verification

Run this to check all imports:
```bash
python -c "
import requests
import bs4
import readability
import yaml
import sqlalchemy
import multipart
print('All dependencies available!')
"
```

---

## Summary

**Total Missing**: 6 packages
- 4 critical for RAG scripts (requests, beautifulsoup4, readability-lxml, pyyaml)
- 2 important for core functionality (sqlalchemy, python-multipart)

**Action Required**: Add all 6 packages to requirements.txt

