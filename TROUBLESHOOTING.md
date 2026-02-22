# Troubleshooting Guide

## Common Issues and Solutions

### 1. Services Not Starting

**Problem**: Docker/Podman services fail to start

**Solutions**:
```bash
# Check if ports are already in use
netstat -tulpn | grep -E '3000|5000|8000|9000|11434'

# Stop conflicting services
docker-compose down
docker-compose up -d

# Check logs
docker-compose logs -f

# Restart specific service
docker-compose restart [service_name]
```

### 2. Ollama Connection Issues

**Problem**: Cannot connect to Ollama or models not loading

**Solutions**:
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Check Ollama logs
docker logs ollama

# Restart Ollama
docker-compose restart ollama

# Verify models are pulled
docker exec -it ollama ollama list

# Pull models manually
docker exec -it ollama ollama pull gemma3:12b-instruct-q4_K_M
docker exec -it ollama ollama pull nomic-embed-text

# Test model generation
docker exec -it ollama ollama run gemma3:12b-instruct-q4_K_M "Hello"
```

### 3. Whisper Service Errors

**Problem**: Audio transcription fails

**Solutions**:
```bash
# Check Whisper status
curl http://localhost:9000/health

# Check Whisper logs
docker logs whisper

# Restart Whisper
docker-compose restart whisper

# Verify audio file format (MP3, WAV, MP4 supported)
file ./resources/your_audio.mp4

# Try with smaller audio file first
# Large files may timeout
```

### 4. ChromaDB Connection Issues

**Problem**: Cannot connect to vector store

**Solutions**:
```bash
# Check ChromaDB status
curl http://localhost:8000/api/v1/heartbeat

# Check ChromaDB logs
docker logs chromadb

# Restart ChromaDB
docker-compose restart chromadb

# Check persistent volume
docker volume inspect chroma_data

# If corrupted, recreate (WARNING: deletes data)
docker-compose down
docker volume rm chroma_data
docker-compose up -d
```

### 5. Flask API Not Responding

**Problem**: API returns errors or doesn't start

**Solutions**:
```bash
# Check Flask logs
docker logs flask-api

# Check if all dependencies are installed
pip install -r requirements.txt

# Test API health
curl http://localhost:5000/health

# Run Flask locally for debugging
python api/app.py

# Check environment variables
cat .env
```

### 6. Out of Memory Errors

**Problem**: System runs out of memory

**Solutions**:

**Option A: Use Smaller Model**
```bash
# Stop services
docker-compose down

# Update .env
# Change: OLLAMA_MODEL=gemma3:12b-instruct-q4_K_M
# To: OLLAMA_MODEL=gemma3:2b-instruct-q4_K_M

# Restart and pull smaller model
docker-compose up -d
docker exec -it ollama ollama pull gemma3:2b-instruct-q4_K_M
```

**Option B: Increase Docker Memory**
```bash
# Edit docker-compose.yml
# Add under services -> ollama:
deploy:
  resources:
    limits:
      memory: 10G
    reservations:
      memory: 8G
```

**Option C: Reduce Batch Sizes**
Edit `process_data.py` and change:
```python
chunk_embeddings = embeddings.embed_batch(texts, batch_size=16)  # Was 32
```

### 7. Data Processing Fails

**Problem**: PDF or audio processing errors

**Solutions**:

**PDF Issues**:
```bash
# Check if PDFs are readable
python -c "import pdfplumber; pdf = pdfplumber.open('./resources/your.pdf'); print(len(pdf.pages))"

# Try alternative PDF library
pip install PyPDF2
# Modify pdf_loader.py to use PyPDF2 if needed

# Check file permissions
ls -la ./resources/
```

**Audio Issues**:
```bash
# Verify Whisper is running
curl http://localhost:9000/health

# Test with small audio file first
# Large files (>100MB) may timeout

# Check audio format
ffmpeg -i ./resources/your_audio.mp4

# Convert to supported format if needed
ffmpeg -i input.mp4 -ar 16000 output.wav
```

### 8. Slow Inference

**Problem**: Responses take too long

**Solutions**:

**Option A: Use Smaller Model**
```bash
# Switch to Gemma 3 2B
docker exec -it ollama ollama pull gemma3:2b-instruct-q4_K_M

# Update .env
OLLAMA_MODEL=gemma3:2b-instruct-q4_K_M
```

**Option B: Reduce Token Limit**
```bash
# Update .env
MAX_TOKENS=300  # Was 500
```

**Option C: Reduce Context**
```bash
# Update .env
TOP_K_RETRIEVAL=3  # Was 5
```

### 9. Poor Answer Quality

**Problem**: Answers are not relevant or accurate

**Solutions**:

**Option A: Improve Chunking**
```bash
# Update .env
CHUNK_SIZE=1000  # Was 800
CHUNK_OVERLAP=200  # Was 150
```

**Option B: Use Hybrid Search**
Edit retriever call in `api/app.py`:
```python
context = self.retriever.retrieve(question, top_k=5, use_hybrid=True)
```

**Option C: Adjust Temperature**
```bash
# Update .env
TEMPERATURE=0.5  # Was 0.7 (lower = more focused)
```

**Option D: Reprocess Data**
```bash
# Delete and recreate vector store
docker-compose down
docker volume rm chroma_data
docker-compose up -d

# Reprocess data
python process_data.py
```

### 10. Open WebUI Issues

**Problem**: Cannot access or login to Open WebUI

**Solutions**:
```bash
# Check if Open WebUI is running
curl http://localhost:3000

# Check logs
docker logs open-webui

# Restart Open WebUI
docker-compose restart open-webui

# Reset Open WebUI (WARNING: deletes users)
docker-compose down
docker volume rm open_webui_data
docker-compose up -d

# First user to sign up becomes admin
```

### 11. Import Errors in Python

**Problem**: ModuleNotFoundError or ImportError

**Solutions**:
```bash
# Install all dependencies
pip install -r requirements.txt

# Verify Python version (need 3.9+)
python --version

# Check if src is in path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Or add to your script
import sys
sys.path.append('.')
```

### 12. Container Networking Issues

**Problem**: Containers cannot communicate

**Solutions**:
```bash
# Check if containers are on same network
docker network ls
docker network inspect [network_name]

# Use service names in URLs (not localhost)
# Good: http://ollama:11434
# Bad: http://localhost:11434

# Restart all services
docker-compose down
docker-compose up -d
```

### 13. Permission Errors

**Problem**: Cannot write to directories

**Solutions**:
```bash
# Fix directory permissions
chmod -R 755 ./data
chmod -R 755 ./resources

# Check ownership
ls -la ./data

# Fix ownership if needed
sudo chown -R $USER:$USER ./data
```

### 14. Windows-Specific Issues

**Problem**: Scripts don't work on Windows

**Solutions**:
```cmd
REM Use Windows batch file
quickstart.bat

REM Use backslashes in paths
python src\data_processing\pdf_loader.py

REM Or use forward slashes
python src/data_processing/pdf_loader.py

REM Install Windows-specific dependencies
pip install windows-curses
```

### 15. Raspberry Pi 5 Issues

**Problem**: System too slow or crashes on Pi 5

**Solutions**:
```bash
# Use Gemma 3 2B (not 12B)
OLLAMA_MODEL=gemma3:2b-instruct-q4_K_M

# Use tiny Whisper model
WHISPER_MODEL=tiny

# Reduce context
TOP_K_RETRIEVAL=3
CHUNK_SIZE=500

# Monitor temperature
vcgencmd measure_temp

# Add active cooling if overheating
# See PI5AI.md for details
```

## Getting Help

### Check Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f ollama
docker-compose logs -f whisper
docker-compose logs -f chromadb
docker-compose logs -f flask-api
```

### Verify Configuration
```bash
# Check .env file
cat .env

# Check docker-compose.yml
cat docker-compose.yml

# Check service status
docker-compose ps
```

### Test Individual Components
```bash
# Test Ollama
curl http://localhost:11434/api/tags

# Test Whisper
curl http://localhost:9000/health

# Test ChromaDB
curl http://localhost:8000/api/v1/heartbeat

# Test Flask API
curl http://localhost:5000/health
```

### Clean Restart
```bash
# Stop everything
docker-compose down

# Remove volumes (WARNING: deletes data)
docker volume rm chroma_data open_webui_data ollama_data

# Restart
docker-compose up -d

# Reprocess data
python process_data.py
```

## Still Having Issues?

1. Check the logs for specific error messages
2. Verify all prerequisites are installed
3. Ensure you have enough RAM and disk space
4. Try the clean restart procedure above
5. Refer to IMPLEMENTATION.md for detailed setup instructions
6. Check README.md for configuration options

## Useful Commands

```bash
# Check system resources
docker stats

# Check disk space
df -h

# Check memory
free -h

# Check running processes
docker-compose ps

# Enter container shell
docker exec -it [container_name] /bin/bash

# View container details
docker inspect [container_name]

# Remove all stopped containers
docker container prune

# Remove unused volumes
docker volume prune

# Remove unused images
docker image prune
```
