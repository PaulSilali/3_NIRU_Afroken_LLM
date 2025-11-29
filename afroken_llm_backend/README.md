# AfroKen LLM Backend

FastAPI backend for the AfroKen LLM Citizen Service Copilot.

> **📖 Full documentation**: See [docs/README.md](docs/README.md) for complete setup and usage guide.

## Quick Start

```bash
# Setup
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
pip install -r config/requirements_local.txt

# Build RAG corpus (optional)
python scripts/rag/check_robots_report.py config/urls.txt
python scripts/rag/fetch_and_extract.py config/urls.txt
python scripts/rag/chunk_and_write_md.py
python scripts/rag/index_faiss.py

# Start backend
./run_local.sh
# Or: uvicorn app.main:app --reload --port 8000
```

## Project Structure

```
afroken_llm_backend/
├── app/              # FastAPI application
├── scripts/          # Utility scripts (RAG pipeline, DB)
├── data/             # Data directories (raw, docs, corpus)
├── config/           # Configuration files
├── docs/             # Documentation
└── docker/           # Docker configuration
```

See [docs/README.md](docs/README.md) for detailed structure and documentation.

## Features

- ✅ FastAPI REST API
- ✅ RAG (Retrieval-Augmented Generation) with FAISS
- ✅ Local embedding fallback (sentence-transformers)
- ✅ Robots.txt compliance checking
- ✅ Document ingestion pipeline
- ✅ Chat endpoint with RAG fallback

## Documentation

- [Complete README](docs/README.md)
- [Next Steps Guide](docs/NEXT_STEPS.md)
- [Robots.txt Check Guide](docs/ROBOTS_CHECK_GUIDE.md)
- [Improvements Applied](docs/IMPROVEMENTS_APPLIED.md)

