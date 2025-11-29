# AfroKen LLM Backend

FastAPI backend for the AfroKen LLM Citizen Service Copilot.

## Project Structure

```
afroken_llm_backend/
├── app/                          # Main FastAPI application
│   ├── api/                      # API routes
│   │   └── routes/               # Route handlers
│   ├── core/                      # Core functionality
│   ├── services/                  # Business logic services
│   ├── tasks/                     # Celery background tasks
│   └── utils/                     # Utility functions
│
├── scripts/                       # Utility scripts
│   ├── rag/                       # RAG pipeline scripts
│   │   ├── fetch_and_extract.py   # Fetch URLs and extract content
│   │   ├── chunk_and_write_md.py  # Chunk text into Markdown
│   │   ├── index_faiss.py         # Build FAISS vector index
│   │   └── check_robots_report.py # Pre-check robots.txt compliance
│   └── db/                        # Database scripts
│       └── init_db.py             # Initialize database
│
├── data/                          # Data directories
│   ├── raw/                       # Raw fetched HTML/text files
│   ├── docs/                      # Processed Markdown files
│   └── corpus/                    # Legacy corpus files
│
├── config/                        # Configuration files
│   ├── urls.txt                   # URLs to scrape for RAG corpus
│   └── requirements_local.txt     # Local RAG dependencies
│
├── docker/                        # Docker configuration
│   ├── docker-compose.yml         # Docker Compose setup
│   └── Dockerfile                 # Docker image definition
│
├── docs/                          # Documentation
│   ├── README.md                  # This file
│   ├── NEXT_STEPS.md              # Next steps guide
│   ├── IMPROVEMENTS_APPLIED.md    # Applied improvements log
│   ├── ROBOTS_CHECK_GUIDE.md      # Robots.txt checking guide
│   └── patch_chat_fallback.txt    # Chat fallback patch notes
│
├── requirements.txt               # Main Python dependencies
├── run_local.sh                   # Local development startup script
└── .gitignore                     # Git ignore rules
```

## Quick Start

### 1. Setup Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r config/requirements_local.txt
```

### 2. Build RAG Corpus (Optional)

```bash
# Pre-check robots.txt compliance
python scripts/rag/check_robots_report.py config/urls.txt

# Build RAG index (or use run_local.sh)
python scripts/rag/fetch_and_extract.py config/urls.txt
python scripts/rag/chunk_and_write_md.py
python scripts/rag/index_faiss.py
```

### 3. Start Backend

```bash
# Using the startup script (recommended)
./run_local.sh

# Or manually
uvicorn app.main:app --reload --port 8000
```

The API will be available at:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

## RAG Pipeline

The RAG (Retrieval-Augmented Generation) pipeline consists of three main scripts:

1. **fetch_and_extract.py**: Fetches URLs, checks robots.txt, extracts text
2. **chunk_and_write_md.py**: Chunks text into Markdown files with YAML front-matter
3. **index_faiss.py**: Generates embeddings and builds FAISS vector index

See individual script files for detailed documentation.

## Configuration

- **Environment Variables**: Set in `.env` file (see `.env.example`)
- **URLs**: Edit `config/urls.txt` to add/remove URLs for scraping
- **Dependencies**: Main deps in `requirements.txt`, RAG deps in `config/requirements_local.txt`

## Documentation

- [Next Steps Guide](NEXT_STEPS.md)
- [Robots.txt Check Guide](ROBOTS_CHECK_GUIDE.md)
- [Improvements Applied](IMPROVEMENTS_APPLIED.md)

## Development

### Running Tests

```bash
pytest
```

### Code Style

```bash
black .
flake8 .
```

## Production Deployment

See `docker/Dockerfile` and `docker/docker-compose.yml` for containerized deployment.

## License

[Your License Here]
