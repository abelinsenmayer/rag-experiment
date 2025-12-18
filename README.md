# RAG Experiment

Python application for interacting with an OpenSearch cluster running in Docker.

## Setup

### Prerequisites
- Docker and Docker Compose
- Python 3.10+
- Poetry (for dependency management)
- PowerShell (Windows) or Bash (Linux/Mac/WSL)

### Installation

1. Install dependencies with Poetry:
```bash
poetry install
```

## Usage

### Start the OpenSearch cluster and set up indexes

#### PowerShell (Windows)
```powershell
.\scripts\startup.ps1
```

#### Bash (Linux/Mac/WSL)
```bash
./scripts/startup.sh
```

This will:
1. Start the OpenSearch cluster using Docker Compose
2. Wait for the cluster to be ready
3. Set up the necessary OpenSearch indexes

### Individual scripts

#### PowerShell (Windows)
- Start OpenSearch only: `.\scripts\start-opensearch.ps1`
- Stop OpenSearch: `.\scripts\stop-opensearch.ps1`

#### Bash (Linux/Mac/WSL)
- Start OpenSearch only: `./scripts/start-opensearch.sh`
- Stop OpenSearch: `./scripts/stop-opensearch.sh`

## OpenSearch Configuration

The OpenSearch cluster runs on:
- REST API: http://localhost:9200
- Performance Analyzer: http://localhost:9600

Security is disabled for development purposes.
