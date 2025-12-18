#!/bin/bash

# Start OpenSearch cluster using docker compose
echo "Starting OpenSearch cluster..."
cd "$(dirname "$0")/opensearch-cluster"
docker compose up -d

echo "Waiting for OpenSearch to be ready..."
# Wait for the cluster to respond to health checks
until curl -s http://localhost:9200/_cluster/health | grep -q '"status":"green\|yellow"'; do
    echo "OpenSearch is not ready yet. Waiting 5 seconds..."
    sleep 5
done

echo "OpenSearch cluster is ready!"
