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

### Quick Start & Stop (Everyday Use)

For regular development, you'll typically want to just start and stop the OpenSearch cluster without setting up indexes or destroying data:

#### PowerShell (Windows)
```powershell
# Start OpenSearch cluster (preserves existing data)
.\scripts\start-opensearch.ps1

# Stop OpenSearch cluster (preserves data for next time)
.\scripts\stop-opensearch.ps1
```

#### Bash (Linux/Mac/WSL)
```bash
# Start OpenSearch cluster (preserves existing data)
./scripts/start-opensearch.sh

# Stop OpenSearch cluster (preserves data for next time)
./scripts/stop-opensearch.sh
```

### Full Setup & Teardown

Use these for initial setup or when you want a completely fresh environment:

#### Start the OpenSearch cluster and set up indexes

This performs a complete first-time setup including index creation.

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

### Individual Scripts

#### For Container Management (Data Preserved)

These scripts manage the OpenSearch containers while keeping your data intact:

**PowerShell (Windows)**
- `.\scripts\start-opensearch.ps1` - Starts the cluster with existing data
- `.\scripts\stop-opensearch.ps1` - Stops the cluster but preserves volumes

**Bash (Linux/Mac/WSL)**
- `./scripts/start-opensearch.sh` - Starts the cluster with existing data
- `./scripts/stop-opensearch.sh` - Stops the cluster but preserves volumes

#### For Complete Environment Reset

Use these when you want to start completely fresh:

**PowerShell (Windows)**
- `.\scripts\startup.ps1` - Full setup: starts cluster AND creates indexes
- `.\scripts\teardown.ps1` - Complete reset: stops cluster AND destroys all data

**Bash (Linux/Mac/WSL)**
- `./scripts/startup.sh` - Full setup: starts cluster AND creates indexes
- `./scripts/teardown.sh` - Complete reset: stops cluster AND destroys all data

#### When to Use Each Script

| Scenario | Recommended Script | Why |
|----------|-------------------|-----|
| First time running the project | `startup.ps1/sh` | Sets up indexes needed for the application |
| Daily development work | `start-opensearch.ps1/sh` | Quickly start with existing data |
| Taking a break (preserving work) | `stop-opensearch.ps1/sh` | Stop containers but keep data |
| Starting fresh after changes | `teardown.ps1/sh` then `startup.ps1/sh` | Clean slate with fresh setup |
| Troubleshooting data issues | `teardown.ps1/sh` | Remove potentially corrupted data |

## OpenSearch Configuration

The OpenSearch cluster runs on:
- REST API: http://localhost:9200
- Performance Analyzer: http://localhost:9600

Security is disabled for development purposes.
