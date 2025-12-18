# Stop and destroy OpenSearch cluster using docker compose
Write-Host "Stopping OpenSearch cluster..."

# Get the directory where this script is located
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$DockerComposeDir = Join-Path $ScriptDir "..\opensearch-cluster"

Set-Location $DockerComposeDir
docker compose down -v

Write-Host "OpenSearch cluster stopped and volumes removed."
