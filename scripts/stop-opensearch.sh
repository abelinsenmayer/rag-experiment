#!/bin/bash

# Stop OpenSearch cluster using docker compose (preserves volumes)
echo "Stopping OpenSearch cluster..."
cd "$(dirname "$0")/opensearch-cluster"
docker compose down

echo "OpenSearch cluster stopped. Volumes preserved."
