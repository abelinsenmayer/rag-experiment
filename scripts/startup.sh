#!/bin/bash

# Unified startup script for RAG experiment
# This script starts OpenSearch cluster and sets up indexes

echo "=== RAG Experiment Startup ==="
echo "Starting OpenSearch cluster and setting up indexes..."

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Step 1: Start OpenSearch cluster
echo "Step 1: Starting OpenSearch cluster..."
$SCRIPT_DIR/start-opensearch.sh

# Check if OpenSearch started successfully
if [ $? -ne 0 ]; then
    echo "Error: Failed to start OpenSearch cluster"
    exit 1
fi

# Step 2: Set up OpenSearch indexes using Python
echo "Step 2: Setting up OpenSearch indexes..."
cd "$SCRIPT_DIR/.."

# Use poetry to run the Python setup
poetry run python src/opensearch_setup.py

# Check if index setup was successful
if [ $? -ne 0 ]; then
    echo "Error: Failed to set up OpenSearch indexes"
    echo "Stopping OpenSearch cluster..."
    $SCRIPT_DIR/stop-opensearch.sh
    exit 1
fi

echo "=== Startup Complete ==="
echo "OpenSearch cluster is running at http://localhost:9200"
echo "Indexes have been set up successfully."
echo ""
echo "To stop the cluster, run: ./scripts/stop-opensearch.sh"
