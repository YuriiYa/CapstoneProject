# AI-Agentic RAG System - Capstone Project

## Project Overview

This is an AI-Agentic RAG (Retrieval-Augmented Generation) system built as part of the Ciklum AI Academy. The system processes multi-format knowledge bases (PDFs and audio) and generates intelligent responses with autonomous reasoning, tool-calling, and self-reflection capabilities.

## Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [Usage](#usage)
- [Testing](#testing)
- [Deployment Options](#deployment-options)
- [Quick Reference](#quick-reference)
- [File Organization](#file-organization)
- [Troubleshooting](#troubleshooting)
- [Resources](#resources)

## Features

### Core RAG Capabilities

- **Multi-format Data Processing**: Handles PDFs and audio/video files with ffmpeg-based audio extraction
- **Intelligent Chunking**: Semantic text chunking with configurable overlap
- **Vector Search**: ChromaDB-based similarity search with nomic-embed-text embeddings
- **Hybrid Retrieval**: Combines vector similarity with keyword matching for better results

### Agentic Features

- **Query Analysis**: Understands user intent and identifies key concepts
- **Chain-of-Thought Reasoning**: Step-by-step reasoning for complex queries
- **Tool Execution**: Can use tools like search, calculate, compare, and summarize
- **Self-Reflection**: Evaluates answer quality and confidence
- **Self-Correction**: Automatically improves low-confidence answers

### Deployment & Infrastructure

- **Containerized Architecture**: Docker/Podman-based with health checks and proper orchestration
- **Modern UI**: Open WebUI provides ChatGPT-like interface
- **REST API**: Flask-based API for programmatic access
- **CLI Interface**: Command-line tool for testing and development
- **Cross-Platform**: Works on Linux, macOS, Windows, and Raspberry Pi 5

### Evaluation & Monitoring

- **Confidence Scoring**: Every answer includes a confidence score
- **Source Citations**: Tracks and displays source documents
- **Performance Metrics**: Retrieval and generation quality metrics
- **Test Suite**: Comprehensive test questions for validation

## Technology Stack

- **LLM**: Gemma 3 12B (via Ollama)
- **Embeddings**: nomic-embed-text
- **Vector DB**: ChromaDB
- **Audio Transcription**: Whisper
- **Audio Processing**: ffmpeg (for MP4 to WAV conversion)
- **Backend**: Flask + Python
- **Frontend**: Open WebUI
- **Containerization**: Podman

## Quick Start

### Prerequisites

- Podman installed
- 14GB+ RAM available (8GB for Raspberry Pi 5)
- 25GB+ disk space
- Python 3.11+ (for local development)
- ffmpeg (included in containers, required for local Windows setup)

### Automated Setup (Recommended)

```sh
podman compose up
```

This will:

1. Start all services (Ollama, Whisper, ChromaDB, Flask API, Open WebUI)
2. Wait for health checks to pass
3. Pull required models (Gemma 3 12B + nomic-embed-text)
4. Display service URLs

### Manual Setup Steps

#### 1. Start Services

```bash
# OR using Podman Compose
podman compose up -d
```

#### 2. Pull Models

```bash
# Pull Gemma 3 12B (Laptop/Desktop)
podman exec ollama ollama pull gemma3:12b-instruct-q4_K_M

# OR Gemma 3 2B (Raspberry Pi 5)
podman exec ollama ollama pull gemma3:2b-instruct-q4_K_M

# Pull embedding model
podman exec ollama ollama pull nomic-embed-text

# Verify models
podman exec ollama ollama list
```

#### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
# or in case previous fails
pip install --no-cache-dir -r requirements.txt
```

#### 4. Process Data

```bash
# Automated processing (recommended)
python process_data.py

# Or transcribe videos only
python transcribe_videos.py
```

#### 5. Access the System

- **Open WebUI**: <http://localhost:3000>
- **Flask API**: <http://localhost:5000>
- **CLI Interface**: `python main.py`

## Project Structure

```
CapstoneProject/
├── api/                          # Flask API backend
│   ├── app.py                   # Main API application
│   ├── routes/                  # API routes
│   └── middleware/              # API middleware
├── src/                         # Source code
│   ├── agent/                   # Agentic components
│   │   ├── reasoning_engine.py # Query analysis & reasoning
│   │   ├── tool_manager.py     # Tool registration & execution
│   │   ├── reflection_module.py # Self-assessment
│   │   └── post_generator.py   # LinkedIn post generation
│   ├── data_processing/         # Data processing modules
│   │   ├── pdf_loader.py       # PDF text extraction
│   │   ├── audio_transcriber.py # Audio transcription (ffmpeg + Whisper)
│   │   └── text_chunker.py     # Text chunking strategies
│   ├── embeddings/              # Embedding generation
│   │   ├── embedding_generator.py # Ollama embeddings
│   │   └── vector_store.py     # ChromaDB interface
│   ├── evaluation/              # Evaluation metrics
│   │   └── evaluator.py        # RAG evaluation
│   ├── llm/                     # LLM client and prompts
│   │   ├── llm_client.py       # Ollama client
│   │   └── prompt_templates.py # Prompt templates
│   └── retrieval/               # Retrieval logic
│       └── retriever.py        # Hybrid retrieval
├── data/                        # Data storage (gitignored)
│   ├── processed/               # Processed data
│   │   ├── pdf_text/           # Extracted PDF text
│   │   ├── audio_transcripts/  # Audio transcriptions
│   │   └── chunks/             # Text chunks
│   ├── embeddings/             # Generated embeddings
│   └── raw/                    # Raw data files
├── resources/                   # Source materials
│   ├── *.pdf                   # PDF documents
│   └── *.mp4                   # Video files (gitignored)
├── tests/                       # Test files
│   ├── test_questions.py       # RAG system tests
│   └── __init__.py
├── tools/                       # Utility tools
├── docker-compose.yml           # Full Podman configuration
├── docker-compose.simple.yml    # Simplified Podman config (Windows)
├── Dockerfile.flask             # Flask container with ffmpeg
├── docker-startup.sh            # Container startup (Linux/Mac)
├── docker-startup.bat           # Container startup (Windows)
├── main.py                      # CLI interface
├── process_data.py              # Data processing pipeline
├── transcribe_videos.py         # Video transcription utility
├── requirements.txt             # Python dependencies
└── *.md                         # Documentation files
```

## Configuration

### Environment Variables (.env)

```bash
# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=gemma3:12b-instruct-q4_K_M
OLLAMA_EMBEDDING_MODEL=nomic-embed-text

# Whisper Configuration
WHISPER_BASE_URL=http://localhost:9000
WHISPER_MODEL=base

# ChromaDB Configuration
CHROMA_HOST=localhost
CHROMA_PORT=8000
CHROMA_COLLECTION_NAME=rag_knowledge_base

# Application Configuration
MAX_TOKENS=500
TEMPERATURE=0.7
TOP_K_RETRIEVAL=5
CHUNK_SIZE=800
CHUNK_OVERLAP=150
```

### Service URLs

| Service | URL | Purpose |
|---------|-----|---------|
| Open WebUI | <http://localhost:3000> | Web chat interface |
| Flask API | <http://localhost:5000> | REST API |
| Ollama | <http://localhost:11434> | LLM service |
| ChromaDB | <http://localhost:8000> | Vector database |
| Whisper | <http://localhost:9000> | Audio transcription |

## Usage

### CLI Interface

```bash
# Start the CLI
python main.py

# Available commands:
# - Type any question to get an answer
# - 'menu' - Show interactive menu
# - 'test' - Run required test questions
# - 'post' - Generate LinkedIn post
# - 'stats' - Show vector store statistics
# - 'quit' - Exit
```

### Flask API

Can play with rest api:

[Endpoints](./api/api.http)

### Open WebUI

1. Navigate to <http://localhost:3000>
2. Create an account (first user becomes admin)
3. Select Rag Agent from model dropdown
4. Start asking questions about your knowledge base

### Python Client Example

```python
import requests

# Query the RAG system
response = requests.post(
    'http://localhost:5000/api/chat',
    json={
        'message': 'What is hybrid search?',
        'include_reasoning': True
    }
)

result = response.json()
print(f"Answer: {result['answer']}")
print(f"Confidence: {result['confidence']:.2%}")
print(f"Sources: {len(result['sources'])}")
```

## Testing

### Required Test Questions

1. "What are the production 'Do's' for RAG?"
2. "What is the difference between standard retrieval and the ColPali approach?"
3. "Why is hybrid search better than vector-only search?"

### Running Tests

```bash
# Via CLI
python main.py
# Then type: test

# Or directly
python tests/test_questions.py
```

## Deployment Options

### Option 1: Laptop/Desktop (Development)

- **Model**: gemma3:12b-instruct-q4_K_M
- **RAM**: 14GB+
- **Storage**: 25GB+
- **CPU**: 4+ cores
- **Best for**: Development and testing

### Option 2: Raspberry Pi 5 (Edge Deployment)

- **Model**: gemma3:2b-instruct-q4_K_M
- **RAM**: 8GB
- **Storage**: 64GB+
- **Power**: 27W USB-C PD (52Pi PD Power HAT recommended)
- **Best for**: Edge deployment and demos

See [PI5AI.md](./PI5AI.md) for detailed Raspberry Pi 5 setup.

## Quick Reference

### Essential Commands

#### Start/Stop Services

```bash
# Start all services
podman compose up -d

# Stop all services
podman compose down

# Restart a service
podman compose restart [service_name]

# View logs
podman compose logs -f [service_name]

# Check status
podman compose ps
```

#### Pull Models

```bash
# Gemma 3 12B (Laptop/Desktop)
podman exec ollama ollama pull gemma3:12b-instruct-q4_K_M

# Gemma 3 2B (Raspberry Pi 5)
podman exec ollama ollama pull gemma3:2b-instruct-q4_K_M

# Embedding model
podman exec ollama ollama pull nomic-embed-text

# List models
podman exec ollama ollama list
```

#### Process Data

```bash
# Full pipeline
python process_data.py

# Transcribe videos only
python transcribe_videos.py

# Manual steps
python src/data_processing/pdf_loader.py --input ./resources
python src/data_processing/audio_transcriber.py --input ./resources
```

### Podman Management

```bash
# View logs
podman compose logs -f

# Check resource usage
podman stats

# Enter container
podman exec -it [container] /bin/bash

# Remove all containers and volumes
podman compose down -v

# Rebuild containers
podman compose up -d --build
```

## File Organization

### Permanent Files (Keep)

#### Core Application

- `main.py` - CLI interface
- `process_data.py` - Data processing pipeline
- `transcribe_videos.py` - **Video transcription utility**
- `api/app.py` - Flask API backend
- `src/**/*.py` - All source code modules

#### Docker Configuration

- `docker-compose.yml` - Full Podman setup with Flask
- `docker-compose.nohealth.yml` - Simplified setup (Windows)
- `Dockerfile.flask` - Flask container with ffmpeg

#### Documentation

- `README.md` - This file (main documentation)
- `IMPLEMENTATION.md` - System architecture and design
- `PI5AI.md` - Raspberry Pi 5 deployment guide

#### Configuration

- `requirements.txt` - Python dependencies
- `.env` - Environment variables (user-created)
- `.gitignore` - Git ignore patterns
- `architecture.mmd` - System architecture diagram

### Why Keep `transcribe_videos.py`?

This standalone utility is **NOT temporary** because:

1. Users can transcribe new videos without running full pipeline
2. Useful for debugging transcription issues
3. Referenced in documentation
4. Focused tool for one specific task

**Example use cases:**

```bash
# Transcribe new videos
python transcribe_videos.py

# In Podman container
podman compose exec flask-api python transcribe_videos.py
```

### Temporary Files (Gitignored)

- `test_*.py` - Temporary test files
- `*.wav` - Temporary audio extractions
- `data/processed/` - Generated data
- `data/embeddings/` - Generated embeddings

## Troubleshooting

### Services Not Starting

```bash
# Check service status
podman compose ps

# View logs
podman compose logs -f [service_name]

# Restart services
podman compose restart
```

### Ollama Connection Issues

```bash
# Test Ollama
curl http://localhost:11434/api/tags

# Check if models are loaded
podman exec ollama ollama list

# Pull models again
podman exec ollama ollama pull gemma3:12b-instruct-q4_K_M
```

Instructions how to connect to webui in case it is run on podman and api run on machine locally can be found [here](./FLASK_CONNECTION_FIX.md)

### Crun error while composing flask api

Error:
`Error response from daemon: crun: creating cgroup directory /sys/fs/cgroup/systemd... No such file or directory: OCI runtime attempted to invoke a command that was not found`

Disable Bake/Buildx for this project (quickest)

```bash
podman compose -f docker-compose.nohealth.yml up -d

$env:COMPOSE_DOCKER_CLI_BUILD=0
$env:DOCKER_BUILDKIT=0
podman compose up
```

### Memory Issues

- Use smaller model: `gemma3:2b-instruct-q4_K_M`
- Reduce batch sizes in configuration
- Increase Podman memory limits in Podman Desktop settings (if using Podman Desktop)

### Poor Answers

```bash
# Reprocess data
python process_data.py

# Check vector store
curl http://localhost:5000/api/admin/stats
```

### Clean Restart

```bash
podman compose down
podman volume rm capstoneproject_chroma_data
podman compose up -d
python process_data.py
```

### Windows Build Issues

If you encounter Podman build errors on Windows:

```batch
REM Run Flask locally
python api/app.py
```

### Audio Transcription Issues

If videos return empty transcriptions:

- Check ffmpeg is installed: `ffmpeg -version`
- Verify Whisper service: `curl http://localhost:9000/`
- Check Whisper logs: `podman logs whisper`

## Resources

### Documentation

- [IMPLEMENTATION.md](./IMPLEMENTATION.md) - Detailed implementation guide
- [PI5AI.md](./PI5AI.md) - Raspberry Pi 5 requirements
- [DOCKER_DEPLOYMENT.md](./DOCKER_DEPLOYMENT.md) - Complete Podman deployment guide

### External Resources

- [Ollama Documentation](https://ollama.ai/)
- [ChromaDB Docs](https://docs.trychroma.com/)
- [Whisper ASR](https://github.com/ahmetoner/whisper-asr-webservice)
- [Gemma 3 Model Card](https://ai.google.dev/gemma)

### Knowledge Base Materials

All materials are located in `./resources/`:

- RAG Intro.pdf
- Databases for GenAI.pdf
- Productized & Enterprise RAG.pdf
- Architecture & Design Patterns.pdf
- Video lectures (MP4 files - transcribed automatically)

## System Requirements

### Minimum Requirements

- **RAM**: 14GB (8GB for Raspberry Pi 5 with Gemma 3 2B)
- **Storage**: 25GB free space
- **CPU**: 4+ cores recommended
- **OS**: Linux, macOS, Windows 10/11, or Raspberry Pi OS

### Recommended Requirements

- **RAM**: 32GB for optimal performance
- **Storage**: 50GB+ for multiple models
- **CPU**: 8+ cores
- **GPU**: Optional (not required, CPU-only deployment)

## Contributing

This is a capstone project for the Ciklum AI Academy. For questions or issues, please refer to the course materials or contact your mentor.

## License

Educational project - Ciklum AI Academy

## Acknowledgments

- Built as part of the Ciklum AI Academy Engineering Track
- Uses Gemma 3 by Google
- Powered by Ollama, ChromaDB, and Whisper
- Audio processing with ffmpeg

---

## How to

### Chroma DB

```bash

chroma browse rag_knowledge_base --local
chroma browse rag_knowledge_base --host http://localhost:8000
```

### Useful commands

### Browse ChromaDB

```powershell
python browse_chroma.py
```

### Test Flask API

```powershell
curl http://localhost:5000/health
```

### Check Containers

```powershell
podman ps
```

### View Container Logs

```powershell
podman logs chromadb
podman logs ollama
podman logs open-webui
```

## Implmenting MCP tool Server

Run API

```bash
.\venv\Scripts\Activate.ps1
python api/app.py

```

Run
MCP Server via mcpo

```bash
.\venv\Scripts\Activate.ps1
pip install mcpo
mcpo --host 0.0.0.0 --port 8001 -- python -X utf8 -u mcp_linkedin_server.py
# to see detailed logs, you need to run in separate terminal
Get-Content -Path "C:\projects\AI Academy\CapstoneProject\mcp_server.log" -Wait
```

Register in Open WebUI:
Open <http://localhost:3000> → login
Go to Settings → Admin Settings → External Tools
Under Manage Tool Servers, click "+" to add a new connection.
Use `http://{your external ip}:8001` as url
Bearer token `dummy-key`
Save — Open WebUI will discover the tools from mcpo's

Enable tools in a chat:
Start a New Chat
Select a model that support choosing tools (e.g. Ollama3.2, mistral-nemo)
Click the Tools icon (wrench) in the message bar

### MCP Troubleshooting

Check farewallto avoid blockage:
`New-NetFirewallRule -DisplayName "mcpo port 8001" -Direction Inbound -Protocol TCP -LocalPort 8001 -Action Allow`

Getting error:
'charmap' codec can't encode character '\U0001f50d' in position 0: character maps to <undefined>

- Why happening: ython's stdout defaults to cp1252 (charmap) on Windows, which can't handle emoji characters (like 🔍) that appear in the pipeline's print/log output. Since mcpo communicates with the MCP server via stdio, this encoding mismatch crashes the process.

- How to fix: Run mcp with command parameter `-X utf8`

### Questions to check

`tool_generate_linkedin_post_post`:
Create a LinkedIn post about my AI capstone project.
Agent: an agentic RAG system with self-reflection and tool use.
Tech stack: Python, Ollama, ChromaDB, Flask, MCP.
Achievements: integrated MCP tool server, Open WebUI support,
automated LinkedIn post generation.
Tone: professional. Length: medium.

Generate a LinkedIn post about my RAG agent project.

`tool_rag_query_post`:
I want to know: What is the difference between standard retrieval and the ColPali approach?. Query the RAG knowledge base.

**Quick Links:**

- [Implementation Details](./IMPLEMENTATION.md)
- [Linkedin Post Generator](https://github.com/talsraviv/peoples-post-generator/tree/main?tab=readme-ov-file)
