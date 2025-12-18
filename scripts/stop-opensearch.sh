#!/bin/bash

# Stop and destroy OpenSearch cluster using docker compose
echo "Stopping OpenSearch cluster..."
cd "$(dirname "$0")/opensearch-cluster"
docker compose down -v

echo "OpenSearch cluster stopped and volumes removed."
