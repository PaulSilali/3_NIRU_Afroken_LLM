# PowerShell script to create .env file with SQLite configuration

$envContent = @"
# Database Configuration
# Using SQLite for local development (easiest option)
DATABASE_URL=sqlite:///./afroken_local.db

# Environment
ENV=development

# Optional: MinIO Configuration (for object storage)
# MINIO_ENDPOINT=localhost:9000
# MINIO_ACCESS_KEY=minioadmin
# MINIO_SECRET_KEY=minioadmin
# MINIO_SECURE=false

# Optional: Redis Configuration (for Celery tasks)
# REDIS_URL=redis://localhost:6379/0

# Optional: LLM Endpoint (if using external LLM service)
# LLM_ENDPOINT=http://localhost:11434/api/generate

# JWT Secret (change in production!)
JWT_SECRET=dev-secret-key-change-in-production
"@

$envPath = Join-Path $PSScriptRoot ".env"

if (Test-Path $envPath) {
    Write-Host "⚠️  .env file already exists!"
    Write-Host "Current contents:"
    Get-Content $envPath
    Write-Host ""
    $overwrite = Read-Host "Do you want to overwrite it? (y/N)"
    if ($overwrite -ne "y" -and $overwrite -ne "Y") {
        Write-Host "Cancelled. .env file not modified."
        exit 0
    }
}

$envContent | Out-File -FilePath $envPath -Encoding utf8 -NoNewline
Write-Host "✅ Created .env file at: $envPath"
Write-Host ""
Write-Host "Configuration:"
Write-Host "  DATABASE_URL=sqlite:///./afroken_local.db"
Write-Host "  ENV=development"
Write-Host ""
Write-Host "Next steps:"
Write-Host "  1. Restart your backend server"
Write-Host "  2. Run: python test_db_connection.py"
Write-Host "  3. Try uploading a PDF!"

