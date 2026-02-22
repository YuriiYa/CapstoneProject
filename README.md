# AI-Agentic RAG System - Capstone Project

## Project Overview
This is an AI-Agentic RAG (Retrieval-Augmented Generation) system built as part of the Ciklum AI Academy. The system processes multi-format knowledge bases (PDFs and audio) and generates intelligent responses with autonomous reasoning, tool-calling, and self-reflection capabilities.

## Features

### Core RAG Capabilities
- **Multi-format Data Processing**: Handles PDFs and audio/video files
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
- **Containerized Architecture**: Docker/Podman-based for easy deployment
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
- **Backend**: Flask + Python
- **Frontend**: Open WebUI
- **Containerization**: Docker/Podman

## Quick Start

### Automated Setup (Recommended)

**Linux/Mac:**
```bash
chmod +x quickstart.sh
./quickstart.sh
```

**Windows:**
```cmd
REM If you encounter Docker build errors, use the simplified version:
quickstart-windows.bat

REM This runs services in Docker and Flask locally
REM See WINDOWS_SETUP.md for details
```

This will:
1. Create .env configuration file
2. Start all services (Ollama, Whisper, ChromaDB, Open WebUI)
3. Pull required models (Gemma 3 12B + nomic-embed-text)
4. Verify all services are running

**Note for Windows users:** If you see Docker build errors, the simplified setup runs Flask locally instead of in Docker. This is actually easier for development! See [WINDOWS_SETUP.md](./WINDOWS_SETUP.md) for details.

### Manual Setup

### Prerequisites
- Docker or Podman installed
- 14GB+ RAM available
- 25GB+ disk space
- Python 3.9+ (for local development)

### Step 1: Start Services
```bash
# Using Docker
docker-compose up -d

# OR using Podman
podman-compose up -d
```

### Step 2: Pull Models
```bash
# Pull Gemma 3 12B
docker exec -it ollama ollama pull gemma3:12b-instruct-q4_K_M

# Pull embedding model
docker exec -it ollama ollama pull nomic-embed-text
```

### Step 3: Install Python Dependencies (for data processing)
```bash
pip install -r requirements.txt
```

### Step 4: Process Data
```bash
# Automated processing (recommended)
python process_data.py

# Or manual processing:
# Process PDFs from ./resources folder
python src/data_processing/pdf_loader.py --input ./resources --output ./data/processed/pdf_text

# Transcribe audio files
python src/data_processing/audio_transcriber.py --input ./resources --output ./data/processed/audio_transcripts
```

### Step 5: Access the System
- **Open WebUI**: http://localhost:3000
- **Flask API**: http://localhost:5000
- **CLI Interface**: `python main.py`

## Project Structure
```
capstone-project/
├── api/                    # Flask API
│   ├── app.py             # Main application
│   ├── routes/            # API endpoints
│   └── middleware/        # Auth & logging
├── src/                   # Core components
│   ├── data_processing/   # PDF & audio processing
│   ├── embeddings/        # Embedding generation & vector store
│   ├── retrieval/         # Retrieval strategies
│   ├── agent/             # Agentic components
│   ├── llm/               # LLM client
│   └── evaluation/        # Metrics & evaluation
├── data/                  # Data storage
│   ├── raw/              # Original files
│   ├── processed/        # Processed text
│   └── embeddings/       # Vector embeddings
├── resources/            # Knowledge base materials
├── tests/                # Test suite
├── docker-compose.yml    # Container orchestration
├── requirements.txt      # Python dependencies
└── README.md            # This file
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

## Development Status

### ✅ Completed Components
- [x] Project structure
- [x] Docker/Podman configuration
- [x] LLM client (Ollama + Gemma 3)
- [x] Embedding generator (nomic-embed-text)
- [x] Vector store (ChromaDB)
- [x] PDF loader (pdfplumber)
- [x] Audio transcriber (Whisper API)
- [x] Text chunking strategy
- [x] Retrieval system with hybrid search
- [x] Reasoning engine (query analysis, chain-of-thought)
- [x] Tool manager (tool registration & execution)
- [x] Reflection module (self-assessment)
- [x] Flask API with all endpoints
- [x] Evaluation system
- [x] CLI interface (main.py)
- [x] LinkedIn post generator
- [x] Architecture diagram (architecture.mmd)
- [x] Test questions suite
- [x] Prompt templates

### 📋 Next Steps
1. Start all services with docker-compose
2. Pull Ollama models (Gemma 3 + embeddings)
3. Process data from ./resources folder
4. Generate embeddings and populate vector store
5. Test with required questions
6. Run evaluation metrics
7. Create demo video
8. Generate and publish LinkedIn post

## Usage

### Using the CLI Interface
```bash
# Start the CLI
python main.py

# Commands:
# - Type any question to get an answer
# - 'menu' - Show interactive menu
# - 'test' - Run required test questions
# - 'post' - Generate LinkedIn post
# - 'stats' - Show vector store statistics
# - 'quit' - Exit
```

### Using the Flask API
```bash
# Start the API (if not using docker-compose)
python api/app.py

# Example API calls:

# Chat endpoint
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What are the production dos for RAG?", "include_reasoning": true}'

# RAG query endpoint
curl -X POST http://localhost:5000/api/rag/query \
  -H "Content-Type: application/json" \
  -d '{"question": "Explain hybrid search", "include_reasoning": true}'

# Retrieve context only
curl -X POST http://localhost:5000/api/rag/retrieve \
  -H "Content-Type: application/json" \
  -d '{"query": "ColPali approach", "top_k": 3}'

# Health check
curl http://localhost:5000/health

# Get stats
curl http://localhost:5000/api/admin/stats
```

### Using Open WebUI
1. Navigate to http://localhost:3000
2. Create an account (first user becomes admin)
3. Select "gemma3:12b-instruct-q4_K_M" from model dropdown
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
# Run required test questions via CLI
python main.py
# Then type: test

# Or run via Python
python tests/test_questions.py
```

## Deployment Options

### Option 1: Laptop/Desktop (Development)
- Model: gemma3:12b-instruct-q4_K_M
- RAM: 14GB+
- Best for development and testing

### Option 2: Raspberry Pi 5 (Edge Deployment)
- Model: gemma3:2b-instruct-q4_K_M
- RAM: 8GB
- See PI5AI.md for detailed setup

## Resources

### Documentation
- [Ollama Documentation](https://ollama.ai/)
- [ChromaDB Docs](https://docs.trychroma.com/)
- [Whisper ASR](https://github.com/ahmetoner/whisper-asr-webservice)
- [IMPLEMENTATION.md](./IMPLEMENTATION.md) - Detailed implementation guide
- [PI5AI.md](./PI5AI.md) - Raspberry Pi 5 requirements

### Knowledge Base Materials
All materials are located in `./resources/`:
- RAG Intro.pdf
- Databases for GenAI.pdf
- Productized & Enterprise RAG.pdf
- Architecture & Design Patterns.pdf
- Video lectures (MP4 files)

## Troubleshooting

### Services Not Starting
```bash
# Check service status
docker-compose ps

# View logs
docker-compose logs -f [service_name]

# Restart services
docker-compose restart
```

### Ollama Connection Issues
```bash
# Test Ollama
curl http://localhost:11434/api/tags

# Check if models are loaded
docker exec -it ollama ollama list
```

### Memory Issues
- Use smaller model: gemma3:2b-instruct-q4_K_M
- Reduce batch sizes
- Increase Docker memory limits

## Contributing
This is a capstone project for the Ciklum AI Academy. For questions or issues, please refer to the course materials or contact your mentor.

## License
Educational project - Ciklum AI Academy

## Acknowledgments
- Built as part of the Ciklum AI Academy Engineering Track
- Uses Gemma 3 by Google
- Powered by Ollama, ChromaDB, and Whisper
