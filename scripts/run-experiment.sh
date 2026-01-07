#!/bin/bash
# Run the complete RAG experiment: setup OpenSearch and run Q&A evaluation

echo "========================================"
echo "RAG Experiment Runner"
echo "========================================"
echo ""

# Check if OpenSearch is running
echo "Checking OpenSearch connection..."
if curl -s -f http://localhost:9200 > /dev/null 2>&1; then
    echo "✓ OpenSearch is running"
else
    echo "✗ OpenSearch is not running or not accessible"
    echo "Please start OpenSearch first using:"
    echo "  ./scripts/startup.sh"
    exit 1
fi

echo ""

# Check if Ollama is running
echo "Checking Ollama connection..."
if curl -s -f http://localhost:11434 > /dev/null 2>&1; then
    echo "✓ Ollama is running"
else
    echo "✗ Ollama is not running or not accessible"
    echo "Please start Ollama and ensure the gemma2 model is available"
    exit 1
fi

echo ""
echo "========================================"
echo "Phase 1: OpenSearch Setup & Data Ingestion"
echo "========================================"
echo ""

# Run OpenSearch setup
echo "Running OpenSearch setup script..."
poetry run python src/opensearch_setup.py

if [ $? -ne 0 ]; then
    echo ""
    echo "✗ OpenSearch setup failed"
    exit 1
fi

echo ""
echo "✓ OpenSearch setup completed successfully"
echo ""

echo "========================================"
echo "Phase 2: Q&A Evaluation (Regular vs RAG)"
echo "========================================"
echo ""

# Run Q&A test runner
echo "Running Q&A evaluation..."
echo ""
poetry run python src/qa_test_runner.py

if [ $? -ne 0 ]; then
    echo ""
    echo "✗ Q&A evaluation failed"
    exit 1
fi

echo ""
echo "========================================"
echo "Experiment Complete!"
echo "========================================"
