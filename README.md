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
- **Containerization**: Docker/Podman

## Quick Start

### Prerequisites

- Docker or Podman installed
- 14GB+ RAM available (8GB for Raspberry Pi 5)
- 25GB+ disk space
- Python 3.11+ (for local development)
- ffmpeg (included in Docker, required for local Windows setup)

### Automated Setup (Recommended)

```sh
docker-compose up
```

This will:

1. Start all services (Ollama, Whisper, ChromaDB, Flask API, Open WebUI)
2. Wait for health checks to pass
3. Pull required models (Gemma 3 12B + nomic-embed-text)
4. Display service URLs

### Manual Setup Steps

#### 1. Start Services

```bash
# Using Docker
docker compose up -d

# OR using Podman
podman-compose up -d
```

#### 2. Pull Models

```bash
# Pull Gemma 3 12B (Laptop/Desktop)
docker exec ollama ollama pull gemma3:12b-instruct-q4_K_M

# OR Gemma 3 2B (Raspberry Pi 5)
docker exec ollama ollama pull gemma3:2b-instruct-q4_K_M

# Pull embedding model
docker exec ollama ollama pull nomic-embed-text

# Verify models
docker exec ollama ollama list
```

#### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
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
- **API Docs**: <http://localhost:5000/apidocs>
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
├── docker-compose.yml           # Full Docker configuration
├── docker-compose.simple.yml    # Simplified Docker config (Windows)
├── Dockerfile.flask             # Flask container with ffmpeg
├── docker-startup.sh            # Docker startup (Linux/Mac)
├── docker-startup.bat           # Docker startup (Windows)
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
docker compose up -d

# Stop all services
docker compose down

# Restart a service
docker compose restart [service_name]

# View logs
docker compose logs -f [service_name]

# Check status
docker compose ps
```

#### Pull Models

```bash
# Gemma 3 12B (Laptop/Desktop)
docker exec ollama ollama pull gemma3:12b-instruct-q4_K_M

# Gemma 3 2B (Raspberry Pi 5)
docker exec ollama ollama pull gemma3:2b-instruct-q4_K_M

# Embedding model
docker exec ollama ollama pull nomic-embed-text

# List models
docker exec ollama ollama list
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

### Docker Management

```bash
# View logs
docker compose logs -f

# Check resource usage
docker stats

# Enter container
docker exec -it [container] /bin/bash

# Remove all containers and volumes
docker compose down -v

# Rebuild containers
docker compose up -d --build
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

- `docker-compose.yml` - Full Docker setup with Flask
- `docker-compose.simple.yml` - Simplified setup (Windows)
- `Dockerfile.flask` - Flask container with ffmpeg
- `docker-startup.sh` / `docker-startup.bat` - Startup scripts

#### Documentation

- `README.md` - This file (main documentation)
- `IMPLEMENTATION.md` - System architecture and design
- `PI5AI.md` - Raspberry Pi 5 deployment guide
- `WINDOWS_SETUP.md` - Windows-specific setup
- `DOCKER_DEPLOYMENT.md` - Docker deployment guide
- `DOCKER_UPDATES.md` - Docker configuration changes
- `TRANSCRIPTION_SUCCESS.md` - Audio transcription solution
- `DATA_PROCESSING_COMPLETE.md` - Data processing summary
- `TROUBLESHOOTING.md` - Common issues and solutions
- `COMPLETION_SUMMARY.md` - Project completion summary

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

# In Docker container
docker compose exec flask-api python transcribe_videos.py
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
docker compose ps

# View logs
docker compose logs -f [service_name]

# Restart services
docker compose restart
```

### Ollama Connection Issues

```bash
# Test Ollama
curl http://localhost:11434/api/tags

# Check if models are loaded
docker exec ollama ollama list

# Pull models again
docker exec ollama ollama pull gemma3:12b-instruct-q4_K_M
```

### Memory Issues

- Use smaller model: `gemma3:2b-instruct-q4_K_M`
- Reduce batch sizes in configuration
- Increase Docker memory limits in Docker Desktop settings

### Poor Answers

```bash
# Reprocess data
python process_data.py

# Check vector store
curl http://localhost:5000/api/admin/stats
```

### Clean Restart

```bash
docker compose down
docker volume rm capstoneproject_chroma_data
docker compose up -d
python process_data.py
```

### Windows Build Issues

If you encounter Docker build errors on Windows:

```batch
REM Run Flask locally
python api/app.py
```

### Audio Transcription Issues

If videos return empty transcriptions:

- Check ffmpeg is installed: `ffmpeg -version`
- Verify Whisper service: `curl http://localhost:9000/`
- Check Whisper logs: `docker logs whisper`

## Resources

### Documentation

- [IMPLEMENTATION.md](./IMPLEMENTATION.md) - Detailed implementation guide
- [PI5AI.md](./PI5AI.md) - Raspberry Pi 5 requirements
- [DOCKER_DEPLOYMENT.md](./DOCKER_DEPLOYMENT.md) - Complete Docker guide
- [WINDOWS_SETUP.md](./WINDOWS_SETUP.md) - Windows-specific instructions
- [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) - Common issues
- [TRANSCRIPTION_SUCCESS.md](./TRANSCRIPTION_SUCCESS.md) - Audio transcription solution

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

**Quick Links:**

- [Docker Deployment Guide](./DOCKER_DEPLOYMENT.md)
- [Troubleshooting](./TROUBLESHOOTING.md)
- [Implementation Details](./IMPLEMENTATION.md)
