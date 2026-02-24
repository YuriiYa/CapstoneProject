# Docker Deployment Guide

## Overview
This guide covers deploying the AI-Agentic RAG System using Docker containers with all dependencies included.

## Prerequisites

### Required Software
- **Docker** or **Podman** (latest version)
- **Docker Compose** (v2.0+) or **Podman Compose**
- **curl** (for health checks)

### System Requirements
- **RAM**: 16GB minimum (32GB recommended for Gemma 3 12B)
- **Storage**: 20GB free space
- **CPU**: 4+ cores recommended

## Quick Start

### Option 1: Full Docker Deployment (Recommended for Linux/Mac)

```bash
# Start all services and pull models
./docker-startup.sh

# Or manually:
docker compose up -d
```

### Option 2: Windows Deployment

```batch
# Start all services and pull models
docker-startup.bat

# Or manually:
docker compose up -d
```

### Option 3: Simplified Deployment (Windows with build issues)

If you encounter Docker build issues on Windows, use the simplified setup:

```batch
# Start services only (no Flask container)
docker compose -f docker-compose.simple.yml up -d

# Run Flask locally
python api/app.py
```

**Note**: For simplified deployment, you must have ffmpeg installed locally.

## Services

### 1. Ollama (LLM Inference)
- **Port**: 11434
- **Image**: ollama/ollama:latest
- **Models**: 
  - gemma3:12b-instruct-q4_K_M (main LLM)
  - nomic-embed-text (embeddings)
- **Health Check**: `curl http://localhost:11434/api/tags`

### 2. Whisper (Audio Transcription)
- **Port**: 9000
- **Image**: onerahmet/openai-whisper-asr-webservice:latest
- **Model**: base
- **Health Check**: `curl http://localhost:9000/`

### 3. ChromaDB (Vector Storage)
- **Port**: 8000
- **Image**: chromadb/chroma:latest
- **Persistent**: Yes (volume: chroma_data)
- **Health Check**: `curl http://localhost:8000/api/v1/heartbeat`

### 4. Flask API (RAG Backend)
- **Port**: 5000
- **Build**: Dockerfile.flask
- **Dependencies**: 
  - Python 3.11
  - ffmpeg (for audio processing)
  - All Python packages from requirements.txt
- **Health Check**: `curl http://localhost:5000/health`

### 5. Open WebUI (Chat Interface)
- **Port**: 3000
- **Image**: ghcr.io/open-webui/open-webui:main
- **Health Check**: `curl http://localhost:3000/health`

## Docker Compose Features

### Health Checks
All services include health checks to ensure proper startup order:
- Services wait for dependencies to be healthy before starting
- Automatic retries with configurable intervals
- Start period allows time for initial setup

### Volumes
Persistent data storage:
- `ollama_data`: Ollama models and cache
- `chroma_data`: Vector database storage
- `open_webui_data`: WebUI settings and history
- `./data`: Mounted for data processing
- `./resources`: Mounted for source files

### Environment Variables
Configured in docker-compose.yml:
```yaml
OLLAMA_BASE_URL=http://ollama:11434
WHISPER_BASE_URL=http://whisper:9000
CHROMA_HOST=chromadb
CHROMA_PORT=8000
OLLAMA_MODEL=gemma3:12b-instruct-q4_K_M
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
CHROMA_COLLECTION_NAME=rag_knowledge_base
CHUNK_SIZE=800
CHUNK_OVERLAP=150
```

## Dockerfile Details

### Dockerfile.flask
```dockerfile
FROM python:3.11-slim

# System dependencies including ffmpeg
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application code
COPY . .

# Create directories
RUN mkdir -p /app/data/processed/pdf_text \
    /app/data/processed/audio_transcripts \
    /app/data/processed/chunks \
    /app/data/embeddings

EXPOSE 5000
CMD ["python", "api/app.py"]
```

### Key Features
- **ffmpeg**: Required for MP4 to WAV audio extraction
- **Python 3.11**: Latest stable Python version
- **Slim base**: Minimal image size
- **Pre-created directories**: Ready for data processing

## Usage

### 1. Start Services

```bash
# Linux/Mac
./docker-startup.sh

# Windows
docker-startup.bat
```

This script will:
1. Stop any existing containers
2. Start all services
3. Wait for health checks
4. Pull Ollama models (Gemma 3 12B + nomic-embed-text)

### 2. Process Data

```bash
# Process PDFs and transcribe audio
python process_data.py

# Or transcribe videos only
python transcribe_videos.py
```

### 3. Access Services

- **Open WebUI**: http://localhost:3000
- **Flask API**: http://localhost:5000
- **API Docs**: http://localhost:5000/apidocs

### 4. Test System

```bash
# Test RAG system
python test_rag_system.py

# Run CLI interface
python main.py
```

## Management Commands

### View Logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f flask-api
docker compose logs -f ollama
docker compose logs -f whisper
```

### Restart Services
```bash
# All services
docker compose restart

# Specific service
docker compose restart flask-api
```

### Stop Services
```bash
# Stop all
docker compose down

# Stop and remove volumes
docker compose down -v
```

### Rebuild Flask Container
```bash
# Rebuild after code changes
docker compose build flask-api
docker compose up -d flask-api
```

### Pull Model Updates
```bash
# Pull latest Gemma 3 model
docker exec ollama ollama pull gemma3:12b-instruct-q4_K_M

# List installed models
docker exec ollama ollama list
```

## Troubleshooting

### Service Not Starting

Check logs:
```bash
docker compose logs <service-name>
```

Check health:
```bash
docker compose ps
```

### Port Already in Use

Change ports in docker-compose.yml:
```yaml
ports:
  - "11435:11434"  # Change 11434 to 11435
```

### Out of Memory

Reduce model size or increase Docker memory:
```bash
# Use smaller model
docker exec ollama ollama pull gemma3:2b

# Or increase Docker Desktop memory limit
# Settings → Resources → Memory
```

### Build Failures on Windows

Use simplified deployment:
```bash
docker compose -f docker-compose.simple.yml up -d
python api/app.py
```

### ffmpeg Not Found (Simplified Deployment)

Install ffmpeg locally:
- **Windows**: Download from https://ffmpeg.org/download.html
- **Mac**: `brew install ffmpeg`
- **Linux**: `sudo apt-get install ffmpeg`

### ChromaDB Connection Issues

Reset ChromaDB:
```bash
docker compose down
docker volume rm capstoneproject_chroma_data
docker compose up -d chromadb
```

### Ollama Model Not Loading

Check model status:
```bash
docker exec ollama ollama list
docker exec ollama ollama pull gemma3:12b-instruct-q4_K_M
```

## Performance Optimization

### For Raspberry Pi 5

Use smaller models:
```bash
# Pull Gemma 3 2B instead of 12B
docker exec ollama ollama pull gemma3:2b

# Update .env file
OLLAMA_MODEL=gemma3:2b
```

### For Production

1. **Use GPU acceleration** (if available):
   ```yaml
   ollama:
     deploy:
       resources:
         reservations:
           devices:
             - driver: nvidia
               count: 1
               capabilities: [gpu]
   ```

2. **Increase worker processes**:
   ```yaml
   flask-api:
     command: gunicorn -w 4 -b 0.0.0.0:5000 api.app:app
   ```

3. **Add Redis caching**:
   ```yaml
   redis:
     image: redis:alpine
     ports:
       - "6379:6379"
   ```

## Security Considerations

### Production Deployment

1. **Change default secrets**:
   ```yaml
   WEBUI_SECRET_KEY=your-secure-random-key-here
   ```

2. **Use environment file**:
   ```bash
   # Create .env.production
   docker compose --env-file .env.production up -d
   ```

3. **Enable authentication**:
   - Configure Open WebUI authentication
   - Add API key authentication to Flask

4. **Use reverse proxy**:
   - Nginx or Traefik for SSL/TLS
   - Rate limiting
   - IP whitelisting

## Monitoring

### Health Checks
```bash
# Check all services
curl http://localhost:11434/api/tags  # Ollama
curl http://localhost:9000/           # Whisper
curl http://localhost:8000/api/v1/heartbeat  # ChromaDB
curl http://localhost:5000/health     # Flask API
curl http://localhost:3000/health     # Open WebUI
```

### Resource Usage
```bash
# Docker stats
docker stats

# Specific container
docker stats ollama
```

## Backup and Restore

### Backup Volumes
```bash
# Backup ChromaDB
docker run --rm -v capstoneproject_chroma_data:/data -v $(pwd):/backup \
  alpine tar czf /backup/chroma_backup.tar.gz /data

# Backup Ollama models
docker run --rm -v capstoneproject_ollama_data:/data -v $(pwd):/backup \
  alpine tar czf /backup/ollama_backup.tar.gz /data
```

### Restore Volumes
```bash
# Restore ChromaDB
docker run --rm -v capstoneproject_chroma_data:/data -v $(pwd):/backup \
  alpine tar xzf /backup/chroma_backup.tar.gz -C /

# Restore Ollama models
docker run --rm -v capstoneproject_ollama_data:/data -v $(pwd):/backup \
  alpine tar xzf /backup/ollama_backup.tar.gz -C /
```

## Next Steps

1. **Process your data**: `python process_data.py`
2. **Open the UI**: http://localhost:3000
3. **Start chatting** with your RAG system!

For more information, see:
- [IMPLEMENTATION.md](IMPLEMENTATION.md) - System architecture
- [WINDOWS_SETUP.md](WINDOWS_SETUP.md) - Windows-specific setup
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues
