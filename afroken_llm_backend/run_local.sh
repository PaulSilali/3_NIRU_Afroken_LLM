#!/bin/bash
# Local RAG ingestion and backend startup script

set -e

BACKEND_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$BACKEND_DIR/.." && pwd)"

echo "=== AfroKen LLM Local RAG Setup ==="
echo "Backend dir: $BACKEND_DIR"
echo "Repo root: $REPO_ROOT"

# Activate venv
if [ -d "$BACKEND_DIR/venv" ]; then
    echo "Activating virtual environment..."
    source "$BACKEND_DIR/venv/bin/activate"
else
    echo "Warning: venv not found. Create it with: python -m venv venv"
fi

# Check if FAISS index exists
INDEX_FILE="$BACKEND_DIR/faiss_index.idx"
INDEX_NPY="$BACKEND_DIR/faiss_index.npy"
DOC_MAP="$BACKEND_DIR/doc_map.json"

if [ ! -f "$INDEX_FILE" ] && [ ! -f "$INDEX_NPY" ] || [ ! -f "$DOC_MAP" ]; then
    echo ""
    echo "=== Building RAG Index ==="
    echo "Index not found. Running ingestion pipeline..."
    
    # Step 1: Fetch and extract
    echo ""
    echo "Step 1: Fetching URLs..."
    python "$BACKEND_DIR/scripts/rag/fetch_and_extract.py" "$BACKEND_DIR/config/urls.txt"
    
    # Step 2: Chunk and write MD
    echo ""
    echo "Step 2: Chunking and writing Markdown..."
    python "$BACKEND_DIR/scripts/rag/chunk_and_write_md.py"
    
    # Step 3: Build FAISS index
    echo ""
    echo "Step 3: Building FAISS index..."
    python "$BACKEND_DIR/scripts/rag/index_faiss.py"
    
    echo ""
    echo "=== Index Build Complete ==="
else
    echo "Index found. Skipping ingestion. (Delete $INDEX_FILE to rebuild)"
fi

# Start backend
echo ""
echo "=== Starting FastAPI Backend ==="
echo "Backend will run on http://localhost:8000"
echo "API docs: http://localhost:8000/docs"
echo ""
echo "To start frontend separately:"
echo "  cd $REPO_ROOT/afroken_llm_frontend"
echo "  npm install  # if first time"
echo "  npm run dev"
echo ""

cd "$BACKEND_DIR"
uvicorn app.main:app --reload --port 8000

