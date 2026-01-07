# RAG Experiment: Evaluating Retrieval-Augmented Generation

A toy RAG (Retrieval-Augmented Generation) solution designed to experimentally compare the performance of an LLM with and without access to retrieved context from a knowledge base.

## Project Overview

This project implements a complete RAG pipeline to answer a specific research question: **Does providing relevant Wikipedia articles as context improve an LLM's ability to answer factual questions?**

The experiment uses:
- **LLM**: Ollama running Gemma3 model locally
- **Knowledge Base**: Mini-Wikipedia dataset stored in OpenSearch with neural search capabilities
- **Evaluation Dataset**: Question-answer pairs from the Mini-Wikipedia dataset
- **Evaluation Method**: Semantic equivalence comparison using the LLM itself

### How It Works

The system runs two parallel evaluations on the same set of questions:

1. **Baseline Mode**: Gemma3 answers questions using only its pre-trained knowledge
2. **RAG Mode**: Gemma3 answers questions with access to the 10 most relevant Wikipedia articles retrieved via neural search

Both sets of answers are then compared against ground truth answers using semantic equivalence evaluation, and the accuracy percentages are compared to determine RAG's impact.

## Prerequisites

Before running this project, ensure you have the following installed:

### Required Software

1. **Docker Desktop** (or Docker Engine + Docker Compose)
   - Used to run the OpenSearch cluster
   - Download: https://www.docker.com/products/docker-desktop/

2. **Ollama**
   - Local LLM runtime for running the Gemma3 model
   - Download: https://ollama.ai/
   - After installation, download the Gemma3 model
   - Ensure Ollama is running (default: http://localhost:11434)

3. **Python 3.10+**
   - Required for running the Python scripts
   - Download: https://www.python.org/downloads/

4. **Poetry**
   - Python dependency management
   - Install: https://python-poetry.org/docs/#installation
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

5. **PowerShell** (Windows) or **Bash** (Linux/Mac/WSL)
   - For running setup scripts

## Setup Instructions

### 1. Install Python Dependencies

```bash
poetry install
```

This installs all required Python packages including:
- `opensearch-py` - OpenSearch client
- `datasets` - HuggingFace datasets for Mini-Wikipedia
- `ollama` - Ollama Python client

### 2. Start OpenSearch and Initialize the Knowledge Base

#### First-Time Setup (PowerShell - Windows)
```powershell
.\scripts\startup.ps1
```

#### First-Time Setup (Bash - Linux/Mac/WSL)
```bash
./scripts/startup.sh
```

This startup script will:
1. Start the OpenSearch cluster using Docker Compose
2. Wait for the cluster to become healthy
3. Configure ML settings for neural search
4. Register and deploy the sentence-transformers embedding model
5. Create the NLP index with k-NN vector search support
6. Create an ingest pipeline for automatic text embedding
7. Load the Mini-Wikipedia corpus into OpenSearch (this may take several minutes)

## Running the RAG Evaluation

### Execute the Complete Experiment

Run the unified experiment script that handles both OpenSearch setup and Q&A evaluation:

#### PowerShell (Windows)
```powershell
.\scripts\run-experiment.ps1
```

#### Bash (Linux/Mac/WSL)
```bash
./scripts/run-experiment.sh
```

This script will:
1. Verify that OpenSearch and Ollama are running
2. Run the OpenSearch setup (configure indexes and ingest Wikipedia data)
3. Run the Q&A evaluation comparing regular Gemma3 vs RAG-enabled Gemma3
4. Display comparative results

**Note**: The first run will take 10-15 minutes as it downloads the embedding model and ingests thousands of Wikipedia articles.

### Customizing the Number of Test Questions

By default, the evaluation tests 10 questions. To test with a different number:

```python
# Edit src/qa_test_runner.py, line 242:
run_qa_test(num_questions=20)  # Test with 20 questions
```

Then run the experiment script again.

### What the Experiment Does

The experiment performs a comprehensive evaluation in several phases:

#### Phase 1: Data Loading
- Loads the Mini-Wikipedia question-answer dataset from HuggingFace
- Extracts the specified number of Q&A pairs for testing

#### Phase 2: Baseline Evaluation (Regular Gemma3)
- For each question:
  - Sends the question to Gemma3 with instructions for concise answers
  - Stores the response alongside the correct answer
- Progress updates shown every 10 questions

#### Phase 3: RAG Evaluation (Gemma3 + Wikipedia Context)
- For each question:
  - Queries OpenSearch to retrieve the 10 most relevant Wikipedia articles using neural search
  - Constructs a RAG prompt containing the question and retrieved context
  - Sends the enriched prompt to Gemma3
  - Stores the response alongside the correct answer
- Progress updates shown every 10 questions

#### Phase 4: Semantic Equivalence Analysis
- For each answer pair (both baseline and RAG):
  - Uses Gemma3 itself to compare the generated answer with the ground truth
  - Gemma3 evaluates semantic equivalence and responds with "CORRECT" or "INCORRECT"
  - Tallies correct answers for both modes

#### Phase 5: Comparative Results
- Calculates accuracy percentages for both modes
- Displays side-by-side comparison
- Shows absolute and relative improvement/decline of RAG vs baseline

### Understanding the Evaluation Modes

#### Baseline Mode (Regular Gemma3)

**Input to LLM:**
```
[Question]

Answer in a single word or a short sentence. 
Do not ask follow-up questions or make suggestions.
```

**Example:**
```
What did Abraham Lincoln accomplish as president?

Answer in a single word or a short sentence.
Do not ask follow-up questions or make suggestions.
```

The LLM relies solely on its pre-trained knowledge to answer.

#### RAG Mode (Gemma3 + Wikipedia Context)

**Input to LLM:**
```
QUESTION:
[Question]

CONTEXT:
Context 1: [Wikipedia passage 1]
Context 2: [Wikipedia passage 2]
...
Context 10: [Wikipedia passage 10]

Using the CONTEXT provided, answer the QUESTION. 
Keep your answer grounded in the facts of the CONTEXT. 
If the CONTEXT doesn't contain the answer to the QUESTION, say you don't know.
Answer in a single word or a short sentence. 
Do not ask follow-up questions or make suggestions.
```

**Example:**
```
QUESTION:
What did Abraham Lincoln accomplish as president?

CONTEXT:
Context 1: Abraham Lincoln was the 16th President of the United States...
Context 2: During his presidency, Lincoln led the nation through the Civil War...
...

Using the CONTEXT provided, answer the QUESTION...
```

The LLM has access to relevant factual information retrieved from the knowledge base.

### How Evaluation Works

The evaluation uses **semantic equivalence** rather than exact string matching:

1. **Answer Generation**: Both modes generate answers to the same questions
2. **Semantic Comparison**: For each generated answer, Gemma3 compares it with the ground truth answer
3. **Binary Classification**: Gemma3 determines if the answers are semantically equivalent (CORRECT) or not (INCORRECT)
4. **Accuracy Calculation**: Percentage of correct answers for each mode
5. **Performance Comparison**: Absolute and relative improvement metrics

**Why Semantic Equivalence?**
- Handles paraphrasing: "16th president" vs "president number 16"
- Accounts for different phrasings of the same fact
- More realistic than exact string matching
- Leverages the LLM's understanding of meaning

### Sample Output

```
🚀 Starting Regular Gemma3 Evaluation...
🤖 Processing regular questions 1-10 of 10...

🚀 Starting RAG-enabled Gemma3 Evaluation...
🤖 Processing RAG-enabled questions 1-10 of 10...

🔍 Evaluating regular gemma3 semantic equivalence 1-10 of 10...
🔍 Evaluating rag-enabled gemma3 semantic equivalence 1-10 of 10...

================================================================================
🏆 COMPARATIVE EVALUATION RESULTS
================================================================================

🤖 Regular Gemma3 Results:
   Total Questions: 10
   Correct Answers: 6
   Incorrect Answers: 4
   Accuracy: 60.0%

🤖📚 RAG-enabled Gemma3 Results:
   Total Questions: 10
   Correct Answers: 8
   Incorrect Answers: 2
   Accuracy: 80.0%

📊 Performance Comparison:
   ✅ RAG improved accuracy by 20.0 percentage points
   📈 RAG shows 33.3% relative improvement
================================================================================
```

## Managing the Environment

### Daily Use (Preserving Data)

Start OpenSearch without reinitializing:
```powershell
# Windows
.\scripts\start-opensearch.ps1

# Linux/Mac/WSL
./scripts/start-opensearch.sh
```

Stop OpenSearch (keeps data):
```powershell
# Windows
.\scripts\stop-opensearch.ps1

# Linux/Mac/WSL
./scripts/stop-opensearch.sh
```

### Complete Reset

Tear down everything and start fresh:
```powershell
# Windows
.\scripts\teardown.ps1
.\scripts\startup.ps1

# Linux/Mac/WSL
./scripts/teardown.sh
./scripts/startup.sh
```
