# PowerShell script to start backend with RAG pipeline
# Usage: .\start_backend.ps1

Write-Host "=== AfroKen LLM Backend Startup ===" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & .\venv\Scripts\Activate.ps1
} else {
    Write-Host "Warning: Virtual environment not found!" -ForegroundColor Red
    Write-Host "Create it with: python -m venv venv" -ForegroundColor Yellow
    exit 1
}

# Check if RAG index exists
$indexExists = (Test-Path "faiss_index.idx") -or (Test-Path "faiss_index.npy")
$docMapExists = Test-Path "doc_map.json"

if (-not $indexExists -or -not $docMapExists) {
    Write-Host ""
    Write-Host "=== Building RAG Index ===" -ForegroundColor Cyan
    Write-Host "RAG index not found. Running ingestion pipeline..." -ForegroundColor Yellow
    Write-Host ""
    
    # Step 1: Fetch and extract
    Write-Host "Step 1: Fetching URLs..." -ForegroundColor Green
    python scripts/rag/fetch_and_extract.py config/urls.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error in fetch_and_extract.py" -ForegroundColor Red
        exit 1
    }
    
    # Step 2: Chunk and write MD
    Write-Host ""
    Write-Host "Step 2: Chunking and writing Markdown..." -ForegroundColor Green
    python scripts/rag/chunk_and_write_md.py
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error in chunk_and_write_md.py" -ForegroundColor Red
        exit 1
    }
    
    # Step 3: Build FAISS index
    Write-Host ""
    Write-Host "Step 3: Building FAISS index..." -ForegroundColor Green
    python scripts/rag/index_faiss.py
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error in index_faiss.py" -ForegroundColor Red
        exit 1
    }
    
    Write-Host ""
    Write-Host "=== Index Build Complete ===" -ForegroundColor Green
} else {
    Write-Host "RAG index found. Skipping ingestion." -ForegroundColor Green
    Write-Host "(Delete faiss_index.idx or faiss_index.npy to rebuild)" -ForegroundColor Gray
}

# Start backend
Write-Host ""
Write-Host "=== Starting FastAPI Backend ===" -ForegroundColor Cyan
Write-Host "Backend will run on: http://localhost:8000" -ForegroundColor Yellow
Write-Host "API docs: http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host "Health check: http://localhost:8000/health" -ForegroundColor Yellow
Write-Host ""
Write-Host "To start frontend (in separate terminal):" -ForegroundColor Cyan
Write-Host "  cd ..\afroken_llm_frontend" -ForegroundColor Gray
Write-Host "  npm install  # if first time" -ForegroundColor Gray
Write-Host "  npm run dev" -ForegroundColor Gray
Write-Host ""

# Start uvicorn
uvicorn app.main:app --reload --port 8000

