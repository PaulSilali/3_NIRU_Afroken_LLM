# Backend Reorganization Plan

## Current Issues
- RAG pipeline scripts scattered in root directory
- Documentation files mixed with code
- Configuration files not organized
- Docker files in root
- No clear separation of concerns

## Proposed Structure

```
afroken_llm_backend/
├── app/                          # Main FastAPI application
│   ├── api/                      # API routes
│   ├── core/                     # Core functionality (security, etc.)
│   ├── services/                 # Business logic services
│   ├── tasks/                    # Celery tasks
│   └── utils/                    # Utility functions
│
├── scripts/                      # Utility scripts
│   ├── rag/                      # RAG pipeline scripts
│   │   ├── fetch_and_extract.py
│   │   ├── chunk_and_write_md.py
│   │   ├── index_faiss.py
│   │   ├── check_robots_report.py
│   │   └── embeddings_fallback.py
│   └── db/                       # Database scripts
│       └── init_db.py
│
├── data/                         # Data directories
│   ├── raw/                      # Raw fetched HTML/text (from fetch_and_extract.py)
│   ├── docs/                     # Processed Markdown files (from chunk_and_write_md.py)
│   └── corpus/                   # Legacy corpus (move corpus_2 here)
│
├── config/                       # Configuration files
│   ├── urls.txt                  # URLs to scrape
│   └── requirements_local.txt    # Local RAG dependencies
│
├── docs/                         # Documentation
│   ├── README.md                 # Main README
│   ├── NEXT_STEPS.md
│   ├── IMPROVEMENTS_APPLIED.md
│   ├── ROBOTS_CHECK_GUIDE.md
│   └── patch_chat_fallback.txt
│
├── docker/                       # Docker configuration
│   ├── docker-compose.yml
│   └── Dockerfile
│
├── requirements.txt              # Main dependencies (keep at root)
├── run_local.sh                 # Main entry script (keep at root)
└── .gitignore
```

## Migration Steps

1. ✅ Create new directory structure
2. Move RAG scripts to scripts/rag/
3. Move documentation to docs/
4. Move config files to config/
5. Move Docker files to docker/
6. Move corpus_2 to data/corpus/
7. Update import paths in scripts
8. Update references in run_local.sh
9. Update README with new structure

