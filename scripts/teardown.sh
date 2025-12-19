#!/bin/bash

# Teardown script for complete OpenSearch cluster reset
# This script stops the cluster and destroys all associated volumes for a fresh start

echo "=== OpenSearch Cluster Teardown ==="
echo "Stopping OpenSearch cluster and destroying all volumes..."

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOCKER_COMPOSE_DIR="$SCRIPT_DIR/../opensearch-cluster"

cd "$DOCKER_COMPOSE_DIR"

# Stop containers and remove all volumes (including named volumes)
echo "Stopping containers and removing volumes..."
docker compose down -v --remove-orphans

# Additionally, remove any dangling volumes that might be left
echo "Removing any remaining OpenSearch volumes..."
docker volume prune -f

# Remove any leftover containers (in case of orphaned containers)
echo "Removing any leftover containers..."
docker container prune -f

echo ""
echo "=== Teardown Complete ==="
echo "OpenSearch cluster has been completely stopped."
echo "All volumes and data have been destroyed."
echo "You can now start fresh with: ./scripts/startup.sh"
