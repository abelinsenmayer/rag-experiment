#!/usr/bin/env pwsh
# Run the complete RAG experiment: setup OpenSearch and run Q+A evaluation

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "RAG Experiment Runner" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if OpenSearch is running
Write-Host "Checking OpenSearch connection..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:9200" -Method Get -TimeoutSec 5 -ErrorAction Stop
    Write-Host "[OK] OpenSearch is running" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] OpenSearch is not running or not accessible" -ForegroundColor Red
    Write-Host "Please start OpenSearch first using:" -ForegroundColor Yellow
    Write-Host "  .\scripts\startup.ps1" -ForegroundColor White
    exit 1
}

Write-Host ""

# Check if Ollama is running
Write-Host "Checking Ollama connection..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:11434" -Method Get -TimeoutSec 5 -ErrorAction Stop
    Write-Host "[OK] Ollama is running" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Ollama is not running or not accessible" -ForegroundColor Red
    Write-Host "Please start Ollama and ensure the gemma2 model is available" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Phase 1: OpenSearch Setup + Data Ingestion" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Run OpenSearch setup
Write-Host "Running OpenSearch setup script..." -ForegroundColor Yellow
poetry run python src/opensearch_setup.py

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "[ERROR] OpenSearch setup failed" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "[OK] OpenSearch setup completed successfully" -ForegroundColor Green
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Phase 2: Q+A Evaluation (Regular vs RAG)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Run Q+A test runner
Write-Host "Running Q+A evaluation..." -ForegroundColor Yellow
Write-Host ""
poetry run python src/qa_test_runner.py

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "[ERROR] Q+A evaluation failed" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Experiment Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
