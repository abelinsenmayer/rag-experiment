# Unified startup script for RAG experiment
# This script starts OpenSearch cluster and sets up indexes

Write-Host "=== RAG Experiment Startup ==="
Write-Host "Starting OpenSearch cluster and setting up indexes..."

# Get the directory where this script is located
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Join-Path $ScriptDir ".."

# Step 1: Start OpenSearch cluster
Write-Host "Step 1: Starting OpenSearch cluster..."
$StartScript = Join-Path $ScriptDir "start-opensearch.ps1"
& $StartScript

# Check if OpenSearch started successfully
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to start OpenSearch cluster"
    exit 1
}

# Step 2: Set up OpenSearch indexes using Python
Write-Host "Step 2: Setting up OpenSearch indexes..."
Set-Location $ProjectRoot

# Use poetry to run the Python setup
poetry run python src/opensearch_setup.py

# Check if index setup was successful
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to set up OpenSearch indexes"
    Write-Host "Stopping OpenSearch cluster..."
    $StopScript = Join-Path $ScriptDir "stop-opensearch.ps1"
    & $StopScript
    exit 1
}

Write-Host "=== Startup Complete ==="
Write-Host "OpenSearch cluster is running at http://localhost:9200"
Write-Host "Indexes have been set up successfully."
Write-Host ""
Write-Host "To stop the cluster, run: .\scripts\stop-opensearch.ps1"
