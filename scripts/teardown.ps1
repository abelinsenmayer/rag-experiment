# Teardown script for complete OpenSearch cluster reset
# This script stops the cluster and destroys all associated volumes for a fresh start

Write-Host "=== OpenSearch Cluster Teardown ==="
Write-Host "Stopping OpenSearch cluster and destroying all volumes..."

# Get the directory where this script is located
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$DockerComposeDir = Join-Path $ScriptDir "..\opensearch-cluster"

Set-Location $DockerComposeDir

# Stop containers and remove all volumes (including named volumes)
Write-Host "Stopping containers and removing volumes..."
docker compose down -v --remove-orphans

# Additionally, remove any dangling volumes that might be left
Write-Host "Removing any remaining OpenSearch volumes..."
docker volume prune -f

# Remove any leftover containers (in case of orphaned containers)
Write-Host "Removing any leftover containers..."
docker container prune -f

Write-Host ""
Write-Host "=== Teardown Complete ==="
Write-Host "OpenSearch cluster has been completely stopped."
Write-Host "All volumes and data have been destroyed."
Write-Host "You can now start fresh with: .\scripts\startup.ps1"
