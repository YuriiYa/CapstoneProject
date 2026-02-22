# Quick Reference Card

## Essential Commands

### Start/Stop Services
```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Restart a service
docker-compose restart [service_name]

# View logs
docker-compose logs -f [service_name]

# Check status
docker-compose ps
```

### Pull Models
```bash
# Gemma 3 12B (Laptop/Desktop)
docker exec -it ollama ollama pull gemma3:12b-instruct-q4_K_M

# Gemma 3 2B (Raspberry Pi 5)
docker exec -it ollama ollama pull gemma3:2b-instruct-q4_K_M

# Embedding model
docker exec -it ollama ollama pull nomic-embed-text

# List models
docker exec -it ollama ollama list
```

### Process Data
```bash
# Automated (recommended)
python process_data.py

# Manual steps
python src/data_processing/pdf_loader.py --input ./resources
python src/data_processing/audio_transcriber.py --input ./resources
```

### Use the System
```bash
# CLI interface
python main.py

# Flask API
python api/app.py

# Open WebUI
# Navigate to http://localhost:3000
```

## Service URLs

| Service | URL | Purpose |
|---------|-----|---------|
| Open WebUI | http://localhost:3000 | Web chat interface |
| Flask API | http://localhost:5000 | REST API |
| Ollama | http://localhost:11434 | LLM service |
| ChromaDB | http://localhost:8000 | Vector database |
| Whisper | http://localhost:9000 | Audio transcription |

## API Endpoints

### Health Check
```bash
curl http://localhost:5000/health
```

### Chat
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Your question here"}'
```

### RAG Query
```bash
curl -X POST http://localhost:5000/api/rag/query \
  -H "Content-Type: application/json" \
  -d '{"question": "Your question", "include_reasoning": true}'
```

### Retrieve Context
```bash
curl -X POST http://localhost:5000/api/rag/retrieve \
  -H "Content-Type: application/json" \
  -d '{"query": "Your query", "top_k": 5}'
```

### Get Stats
```bash
curl http://localhost:5000/api/admin/stats
```

## CLI Commands

When running `python main.py`:

| Command | Action |
|---------|--------|
| `menu` | Show interactive menu |
| `test` | Run required test questions |
| `post` | Generate LinkedIn post |
| `stats` | Show vector store statistics |
| `quit` | Exit |
| Any text | Ask a question |

## Configuration (.env)

```bash
# LLM Configuration
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=gemma3:12b-instruct-q4_K_M
OLLAMA_EMBEDDING_MODEL=nomic-embed-text

# Whisper Configuration
WHISPER_BASE_URL=http://whisper:9000
WHISPER_MODEL=base

# ChromaDB Configuration
CHROMA_HOST=chromadb
CHROMA_PORT=8000
CHROMA_COLLECTION_NAME=rag_knowledge_base

# Application Configuration
MAX_TOKENS=500
TEMPERATURE=0.7
TOP_K_RETRIEVAL=5
CHUNK_SIZE=800
CHUNK_OVERLAP=150
```

## Required Test Questions

1. "What are the production 'Do's' for RAG?"
2. "What is the difference between standard retrieval and the ColPali approach?"
3. "Why is hybrid search better than vector-only search?"

## Project Structure

```
capstone-project/
├── api/                    # Flask API
│   └── app.py             # Main API file
├── src/                   # Core components
│   ├── data_processing/   # PDF & audio processing
│   ├── embeddings/        # Embeddings & vector store
│   ├── retrieval/         # Retrieval system
│   ├── agent/             # Agentic components
│   ├── llm/               # LLM client
│   └── evaluation/        # Evaluation system
├── tests/                 # Test suite
├── data/                  # Data storage
├── resources/             # Knowledge base materials
├── main.py               # CLI interface
├── process_data.py       # Data processing script
├── docker-compose.yml    # Container orchestration
└── requirements.txt      # Python dependencies
```

## Troubleshooting Quick Fixes

### Services not starting
```bash
docker-compose down
docker-compose up -d
```

### Models not loading
```bash
docker exec -it ollama ollama pull gemma3:12b-instruct-q4_K_M
```

### Out of memory
```bash
# Use smaller model
OLLAMA_MODEL=gemma3:2b-instruct-q4_K_M
```

### Poor answers
```bash
# Reprocess data
python process_data.py
```

### Clean restart
```bash
docker-compose down
docker volume rm chroma_data
docker-compose up -d
python process_data.py
```

## Resource Requirements

### Laptop/Desktop
- RAM: 14GB+
- Storage: 25GB+
- CPU: 4+ cores
- Model: gemma3:12b-instruct-q4_K_M

### Raspberry Pi 5
- RAM: 8GB
- Storage: 64GB+
- Power: 27W USB-C PD
- Model: gemma3:2b-instruct-q4_K_M

## Key Files

| File | Purpose |
|------|---------|
| `README.md` | Main documentation |
| `IMPLEMENTATION.md` | Detailed implementation guide |
| `PI5AI.md` | Raspberry Pi 5 requirements |
| `COMPLETION_SUMMARY.md` | Implementation summary |
| `TROUBLESHOOTING.md` | Troubleshooting guide |
| `architecture.mmd` | System architecture diagram |
| `quickstart.sh` | Linux/Mac setup script |
| `quickstart.bat` | Windows setup script |

## Python Client Example

```python
import requests

# Query the system
response = requests.post(
    'http://localhost:5000/api/chat',
    json={'message': 'What is hybrid search?'}
)

result = response.json()
print(f"Answer: {result['answer']}")
print(f"Confidence: {result['confidence']:.2%}")
```

## Useful Docker Commands

```bash
# View logs
docker-compose logs -f

# Check resource usage
docker stats

# Enter container
docker exec -it [container] /bin/bash

# Remove all containers
docker-compose down -v

# Rebuild containers
docker-compose up -d --build
```

## Next Steps

1. ✅ Start services: `./quickstart.sh` or `quickstart.bat`
2. ✅ Process data: `python process_data.py`
3. ✅ Test system: `python main.py` → type `test`
4. ⏳ Record demo video
5. ⏳ Generate LinkedIn post: `python main.py` → type `post`
6. ⏳ Submit project

## Support

- Check `TROUBLESHOOTING.md` for common issues
- Review `IMPLEMENTATION.md` for detailed setup
- See `README.md` for usage examples
- Refer to `COMPLETION_SUMMARY.md` for overview
