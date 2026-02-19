# Implementation Plan: AI-Agentic RAG System

## Project Overview
Build an AI-Agentic system that extends a RAG chatbot with autonomous reasoning, tool-calling, self-reflection, and evaluation capabilities. The system will process multi-format knowledge bases (PDFs and audio) and generate intelligent responses with self-assessment.

## Deployment Architecture

### Containerized Approach with Podman/Docker

This implementation uses a fully containerized architecture with the following benefits:

**Why Containers?**
- ✅ Reproducible environment across different machines
- ✅ Easy deployment and scaling
- ✅ Isolated services with clear dependencies
- ✅ Simple orchestration with docker-compose/podman-compose
- ✅ No manual installation of complex dependencies
- ✅ Works on Linux, Windows, and macOS

**Why Ollama over LM Studio?**
- ✅ Built for server/container deployment (no GUI)
- ✅ Official Docker images available
- ✅ Simple API (OpenAI-compatible)
- ✅ Easy model management via CLI
- ✅ Better for production environments
- ✅ Supports multiple models simultaneously

**Service Architecture:**
```
┌──────────────────────────────────────────────────────────────┐
│                      User Interfaces                          │
│  ┌─────────────────────┐      ┌──────────────────────┐      │
│  │   Open WebUI        │      │   API Clients        │      │
│  │  (Web Chat UI)      │      │  (curl, Postman)     │      │
│  │  localhost:3000     │      │                      │      │
│  └──────────┬──────────┘      └──────────┬───────────┘      │
└─────────────┼─────────────────────────────┼──────────────────┘
              │                             │
              ▼                             ▼
    ┌─────────────────────────────────────────────────┐
    │         Flask API Backend (Port 5000)           │
    │  ┌──────────────────────────────────────────┐  │
    │  │  RAG Agent (Reasoning, Tools, Reflection)│  │
    │  └──────────────────────────────────────────┘  │
    └────────┬──────────────┬──────────────┬─────────┘
             │              │              │
             ▼              ▼              ▼
        ┌────────┐    ┌──────────┐   ┌──────────┐
        │ Ollama │    │ Whisper  │   │ ChromaDB │
        │ (LLM + │    │  (Audio  │   │ (Vector  │
        │ Embed) │    │  Trans.) │   │  Store)  │
        └────────┘    └──────────┘   └──────────┘
```

**Data Flow:**
1. User asks question via Open WebUI or API
2. Flask API receives request
3. RAG Agent:
   - Generates query embedding (Ollama)
   - Retrieves relevant context (ChromaDB)
   - Reasons about the query
   - Generates answer (Ollama + Gemma 3)
   - Reflects on answer quality
4. Response sent back to user with answer, confidence, and sources

## Phase 1: Environment Setup

### 1.1 Project Structure
```
capstone-project/
├── api/
│   ├── app.py                    # Flask application entry point
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── chat.py              # Chat endpoints
│   │   ├── rag.py               # RAG query endpoints
│   │   ├── admin.py             # Admin/management endpoints
│   │   └── health.py            # Health check endpoints
│   └── middleware/
│       ├── __init__.py
│       ├── auth.py              # Authentication middleware
│       └── logging.py           # Request logging
├── src/
│   ├── data_processing/
│   │   ├── pdf_loader.py
│   │   ├── audio_transcriber.py
│   │   └── text_chunker.py
│   ├── embeddings/
│   │   ├── embedding_generator.py
│   │   └── vector_store.py
│   ├── retrieval/
│   │   ├── retriever.py
│   │   └── hybrid_search.py
│   ├── agent/
│   │   ├── reasoning_engine.py
│   │   ├── tool_manager.py
│   │   └── reflection_module.py
│   ├── llm/
│   │   ├── llm_client.py
│   │   └── prompt_templates.py
│   └── evaluation/
│       ├── evaluator.py
│       └── metrics.py
├── data/
│   ├── raw/
│   ├── processed/
│   └── embeddings/
├── tools/
│   └── custom_tools.py
├── tests/
│   ├── test_api.py
│   └── test_agent.py
├── config/
│   └── config.yaml
├── docker-compose.yml
├── Dockerfile.flask
├── .env
├── requirements.txt
├── README.md
├── architecture.mmd
└── main.py
```

### 1.2 Container Setup with Podman/Docker

Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  # Ollama for LLM inference (Gemma 2 12B)
  ollama:
    image: ollama/ollama:latest
    container_name: ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    environment:
      - OLLAMA_HOST=0.0.0.0
    # CPU-only deployment (no GPU required)
    restart: unless-stopped

  # Whisper for audio transcription
  whisper:
    image: onerahmet/openai-whisper-asr-webservice:latest
    container_name: whisper
    ports:
      - "9000:9000"
    environment:
      - ASR_MODEL=base  # Options: tiny, base, small, medium, large
      - ASR_ENGINE=openai_whisper
    # CPU-only deployment (no GPU required)
    restart: unless-stopped

  # ChromaDB for vector storage
  chromadb:
    image: chromadb/chroma:latest
    container_name: chromadb
    ports:
      - "8000:8000"
    volumes:
      - chroma_data:/chroma/chroma
    environment:
      - IS_PERSISTENT=TRUE
      - ANONYMIZED_TELEMETRY=FALSE
    restart: unless-stopped

  # Flask API Backend for RAG Agent
  flask-api:
    build: 
      context: .
      dockerfile: Dockerfile.flask
    container_name: flask-api
    depends_on:
      - ollama
      - whisper
      - chromadb
    environment:
      - OLLAMA_BASE_URL=http://ollama:11434
      - WHISPER_BASE_URL=http://whisper:9000
      - CHROMA_HOST=chromadb
      - CHROMA_PORT=8000
      - FLASK_ENV=production
    volumes:
      - ./data:/app/data
      - ./resources:/app/resources
      - ./src:/app/src
    ports:
      - "5000:5000"
    restart: unless-stopped

  # Open WebUI - Modern Chat Interface
  open-webui:
    image: ghcr.io/open-webui/open-webui:main
    container_name: open-webui
    depends_on:
      - ollama
    ports:
      - "3000:8080"
    volumes:
      - open_webui_data:/app/backend/data
    environment:
      - OLLAMA_BASE_URL=http://ollama:11434
      - WEBUI_SECRET_KEY=your-secret-key-change-this
      - ENABLE_RAG_WEB_SEARCH=false
      - ENABLE_RAG_LOCAL_WEB_FETCH=false
    restart: unless-stopped
    extra_hosts:
      - "host.docker.internal:host-gateway"

volumes:
  ollama_data:
  chroma_data:
  open_webui_data:
```

Create `Dockerfile.flask` for Flask API:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose Flask port
EXPOSE 5000

# Run Flask application
CMD ["python", "api/app.py"]
```

Create `.env`:
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

### 1.3 Install Dependencies

Create `requirements.txt`:
```
# Flask Web Framework
flask>=3.0.0
flask-cors>=4.0.0
flask-restful>=0.3.10
gunicorn>=21.2.0

# Core ML/AI
langchain>=0.1.0
langchain-community>=0.0.20

# Ollama Integration
ollama>=0.1.0

# Vector Database
chromadb>=0.4.0

# Document Processing
pdfplumber>=0.10.0
pypdf2>=3.0.0

# HTTP Client
requests>=2.31.0
httpx>=0.25.0

# Utilities
python-dotenv>=1.0.0
pyyaml>=6.0
numpy>=1.24.0
pandas>=2.0.0
tqdm>=4.65.0

# Evaluation
ragas>=0.1.0
scikit-learn>=1.3.0

# Text Processing
nltk>=3.8.0

# API Documentation
flasgger>=0.9.7

# Validation
marshmallow>=3.20.0

# Caching
redis>=5.0.0
```

### 1.4 Deployment Steps

**Step 1: Start Services**
```bash
# Using Podman
podman-compose up -d

# OR using Docker
docker-compose up -d

# Check all services are running
podman-compose ps
```

**Step 2: Pull Models into Ollama**
```bash
# Pull Gemma 3 12B Instruct (quantized for efficiency)
podman exec -it ollama ollama pull gemma3:12b-instruct-q4_K_M

# Pull embedding model (nomic-embed-text is excellent for RAG)
podman exec -it ollama ollama pull nomic-embed-text

# Verify models are loaded
podman exec -it ollama ollama list
```

**Step 3: Test Services**
```bash
# Test Ollama
curl http://localhost:11434/api/tags

# Test Whisper (with an audio file)
curl -F "audio_file=@test.mp3" http://localhost:9000/asr

# Test ChromaDB
curl http://localhost:8000/api/v1/heartbeat

# Test Flask API
curl http://localhost:5000/health

# Test Open WebUI (should return HTML)
curl http://localhost:3000
```

**Step 4: Setup Open WebUI**
1. Open browser to http://localhost:3000
2. Create admin account (first user becomes admin)
3. Go to Settings → Connections
4. Verify Ollama connection: http://ollama:11434
5. Select Gemma 2 12B model from dropdown

**Step 5: Process Data and Build Knowledge Base**

The RAG system will index all materials from the `./resources` folder:
- **PDF Files**: RAG Intro.pdf, Databases for GenAI.pdf, Productized & Enterprise RAG.pdf, Architecture & Design Patterns.pdf
- **Audio/Video Files**: MP4 lecture recordings that will be transcribed

```bash
# Process PDFs from ./resources folder
python src/data_processing/pdf_loader.py --input ./resources --output ./data/processed/pdf_text

# Transcribe audio/video files from ./resources folder
python src/data_processing/audio_transcriber.py --input ./resources --output ./data/processed/audio_transcripts

# Chunk all processed text
python src/data_processing/text_chunker.py --input ./data/processed --output ./data/processed/chunks

# Generate embeddings and populate vector store
python src/embeddings/embedding_generator.py --input ./data/processed/chunks
```

**Note**: This data preparation step should be completed during application setup before the RAG system can answer questions.

**Step 6: Start Flask API (if not using container)**
```bash
# Development mode
python api/app.py

# Production mode with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 api.app:app
```

**Step 7: Test the Complete System**
```bash
# Test RAG query via API
curl -X POST http://localhost:5000/api/rag/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the production dos for RAG?", "include_reasoning": true}'

# Test chat endpoint
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Explain hybrid search"}'
```

**Step 8: Use Open WebUI**
1. Go to http://localhost:3000
2. Start a new chat
3. Ask questions about your knowledge base
4. The system will use RAG to retrieve context and generate answers

### 1.5 Resource Requirements

**Minimum Configuration (Laptop/Desktop):**
- RAM: 14GB (8GB Gemma 3 12B Q4, 2GB Whisper, 2GB ChromaDB, 2GB Open WebUI + Flask)
- Storage: 20GB (models + data + containers)
- CPU: 4+ cores (CPU-only deployment)
- OS: Windows, Linux, or macOS

**Recommended Configuration (Laptop/Desktop):**
- RAM: 20GB+
- Storage: 30GB+
- CPU: 8+ cores
- OS: Windows, Linux, or macOS

**Raspberry Pi 5 Configuration:**
- Model: Raspberry Pi 5 (8GB RAM)
- AI HAT+: Hailo-8L (26 TOPS NPU)
- Storage: 64GB+ microSD or NVMe SSD (recommended)
- Power: 27W USB-C PD supply or 52Pi PD Power HAT
- Cooling: Active cooling (fan) required
- Model: Gemma 3 2B quantized (instead of 12B)
- See `./PI5AI.md` for detailed Raspberry Pi 5 requirements

**Port Allocation:**
- 3000: Open WebUI (Web Interface)
- 5000: Flask API (REST endpoints)
- 8000: ChromaDB (Vector database)
- 9000: Whisper (Audio transcription)
- 11434: Ollama (LLM and embeddings)

**Lighter Alternative (for limited resources or Raspberry Pi 5):**
```bash
# Use smaller models
podman exec -it ollama ollama pull gemma3:2b-instruct-q4_K_M  # Only 1.6GB
podman exec -it ollama ollama pull nomic-embed-text            # 274MB

# Update .env
OLLAMA_MODEL=gemma3:2b-instruct-q4_K_M
```

**Note**: Gemma 3 2B is recommended for Raspberry Pi 5 deployment due to memory constraints.

**Network Configuration:**
All services communicate via Docker/Podman internal network. External access:
- Open WebUI: http://localhost:3000 (Web UI)
- Flask API: http://localhost:5000 (REST API)
- API Docs: http://localhost:5000/apidocs (Swagger UI)

## Phase 2: Data Preparation & Contextualization

### 2.1 PDF Text Extraction
**File**: `src/data_processing/pdf_loader.py`

Steps:
1. Implement PDF loader using `pdfplumber` (more reliable than PyPDF2)
2. Extract text with layout preservation
3. Handle tables, images, and special formatting
4. Clean extracted text (remove extra whitespace, fix encoding)
5. Save processed text to `data/processed/pdf_text.txt`

Key considerations:
- Handle multi-column layouts
- Preserve section headers
- Extract metadata (page numbers, sections)

### 2.2 Audio Transcription
**File**: `src/data_processing/audio_transcriber.py`

Implementation using containerized Whisper service:

```python
import requests
import os
from pathlib import Path
from typing import Dict, List

class WhisperTranscriber:
    def __init__(self, base_url: str = "http://localhost:9000"):
        self.base_url = base_url
        
    def transcribe_audio(self, audio_path: str) -> Dict:
        """Transcribe audio file using Whisper service"""
        with open(audio_path, 'rb') as audio_file:
            files = {'audio_file': audio_file}
            response = requests.post(
                f"{self.base_url}/asr",
                files=files,
                params={'task': 'transcribe', 'output': 'json'}
            )
            response.raise_for_status()
            return response.json()
    
    def transcribe_with_timestamps(self, audio_path: str) -> List[Dict]:
        """Transcribe with word-level timestamps"""
        with open(audio_path, 'rb') as audio_file:
            files = {'audio_file': audio_file}
            response = requests.post(
                f"{self.base_url}/asr",
                files=files,
                params={
                    'task': 'transcribe',
                    'output': 'json',
                    'word_timestamps': 'true'
                }
            )
            response.raise_for_status()
            return response.json()
    
    def process_audio_files(self, audio_dir: str, output_dir: str):
        """Process all audio files in directory"""
        audio_dir = Path(audio_dir)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        audio_extensions = ['.mp3', '.mp4', '.wav', '.m4a']
        audio_files = [
            f for f in audio_dir.iterdir() 
            if f.suffix.lower() in audio_extensions
        ]
        
        for audio_file in audio_files:
            print(f"Transcribing: {audio_file.name}")
            
            try:
                result = self.transcribe_with_timestamps(str(audio_file))
                
                # Save full JSON result
                json_output = output_dir / f"{audio_file.stem}_full.json"
                with open(json_output, 'w', encoding='utf-8') as f:
                    import json
                    json.dump(result, f, indent=2, ensure_ascii=False)
                
                # Save clean text
                text_output = output_dir / f"{audio_file.stem}.txt"
                with open(text_output, 'w', encoding='utf-8') as f:
                    f.write(result.get('text', ''))
                
                print(f"✓ Saved to: {text_output}")
                
            except Exception as e:
                print(f"✗ Error transcribing {audio_file.name}: {e}")

# Usage
if __name__ == "__main__":
    transcriber = WhisperTranscriber(base_url="http://localhost:9000")
    transcriber.process_audio_files(
        audio_dir="./resources",
        output_dir="./data/processed/audio_transcripts"
    )
```

Steps:
1. Load audio files (support MP4, MP3, WAV, M4A)
2. Send to containerized Whisper service via HTTP
3. Receive transcription with timestamps
4. Post-process transcription:
   - Add punctuation
   - Fix common transcription errors
   - Segment by timestamps
5. Save transcriptions to `data/processed/audio_transcripts/`

Whisper Model Options (configure in docker-compose.yml):
- **tiny**: Fastest, lowest accuracy (~1GB RAM)
- **base**: Good balance (~1GB RAM) - **Recommended**
- **small**: Better accuracy (~2GB RAM)
- **medium**: High accuracy (~5GB RAM)
- **large**: Best accuracy (~10GB RAM)

### 2.3 Text Chunking Strategy
**File**: `src/data_processing/text_chunker.py`

Implement multiple chunking strategies:

1. **Fixed-size chunking**:
   - Chunk size: 500-1000 tokens
   - Overlap: 100-200 tokens

2. **Semantic chunking**:
   - Split by paragraphs/sections
   - Preserve context boundaries
   - Use sentence transformers for similarity

3. **Hybrid approach**:
   - Combine fixed-size with semantic boundaries
   - Ensure chunks don't break mid-sentence

Metadata to preserve:
- Source (PDF page, audio timestamp)
- Section/topic
- Chunk ID
- Original context

## Phase 3: RAG Pipeline Design

### 3.1 Embedding Generation
**File**: `src/embeddings/embedding_generator.py`

Implementation using Ollama embeddings:

```python
import requests
from typing import List
import numpy as np

class OllamaEmbeddings:
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "nomic-embed-text"):
        self.base_url = base_url
        self.model = model
        self.dimension = 768  # nomic-embed-text dimension
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple documents"""
        embeddings = []
        for text in texts:
            embedding = self._generate_embedding(text)
            embeddings.append(embedding)
        return embeddings
    
    def embed_query(self, text: str) -> List[float]:
        """Generate embedding for a single query"""
        return self._generate_embedding(text)
    
    def _generate_embedding(self, text: str) -> List[float]:
        """Internal method to generate embedding"""
        response = requests.post(
            f"{self.base_url}/api/embeddings",
            json={
                "model": self.model,
                "prompt": text
            }
        )
        response.raise_for_status()
        return response.json()["embedding"]
    
    def embed_batch(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """Generate embeddings in batches for efficiency"""
        embeddings = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_embeddings = self.embed_documents(batch)
            embeddings.extend(batch_embeddings)
            print(f"Processed {min(i + batch_size, len(texts))}/{len(texts)} embeddings")
        return embeddings

# Usage
embeddings_generator = OllamaEmbeddings(
    base_url="http://localhost:11434",
    model="nomic-embed-text"
)
```

Steps:
1. Use Ollama's embedding API with `nomic-embed-text` model
   - Optimized for RAG and semantic search
   - 768-dimensional embeddings
   - Excellent quality-to-size ratio (~274MB)

2. Generate embeddings for all chunks
3. Store embeddings with metadata
4. Implement batch processing for efficiency

Alternative Embedding Models (via Ollama):
- **nomic-embed-text**: Best for RAG (768d, ~274MB) - **Recommended**
- **mxbai-embed-large**: High quality (1024d, ~670MB)
- **all-minilm**: Lightweight (384d, ~120MB)

### 3.2 Vector Database Setup
**File**: `src/embeddings/vector_store.py`

**ChromaDB Implementation (Containerized)**

```python
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional
import uuid

class ChromaVectorStore:
    def __init__(
        self,
        host: str = "localhost",
        port: int = 8000,
        collection_name: str = "rag_knowledge_base"
    ):
        # Connect to containerized ChromaDB
        self.client = chromadb.HttpClient(
            host=host,
            port=port,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Create or get collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
    
    def add_documents(
        self,
        documents: List[str],
        embeddings: List[List[float]],
        metadatas: List[Dict],
        ids: Optional[List[str]] = None
    ):
        """Add documents with embeddings to the vector store"""
        if ids is None:
            ids = [str(uuid.uuid4()) for _ in documents]
        
        self.collection.add(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
        print(f"Added {len(documents)} documents to vector store")
    
    def similarity_search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filter_dict: Optional[Dict] = None
    ) -> Dict:
        """Search for similar documents"""
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=filter_dict
        )
        return results
    
    def similarity_search_with_score(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        similarity_threshold: float = 0.7
    ) -> List[Dict]:
        """Search with similarity score filtering"""
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        
        # Filter by similarity threshold
        filtered_results = []
        for i, distance in enumerate(results['distances'][0]):
            similarity = 1 - distance  # Convert distance to similarity
            if similarity >= similarity_threshold:
                filtered_results.append({
                    'document': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'similarity': similarity,
                    'id': results['ids'][0][i]
                })
        
        return filtered_results
    
    def get_collection_stats(self) -> Dict:
        """Get statistics about the collection"""
        return {
            'name': self.collection.name,
            'count': self.collection.count(),
            'metadata': self.collection.metadata
        }

# Usage
vector_store = ChromaVectorStore(
    host="localhost",
    port=8000,
    collection_name="rag_knowledge_base"
)
```

Features implemented:
- Metadata filtering
- Similarity threshold
- Top-k retrieval
- Cosine similarity search
- Persistent storage (via container volume)

### 3.3 Retrieval System
**File**: `src/retrieval/retriever.py`

Implement retrieval strategies:

1. **Vector-only search**:
   - Cosine similarity
   - Top-k results

2. **Hybrid search** (recommended):
   - Combine vector search with keyword search (BM25)
   - Weighted fusion of results
   - Better for specific terms and concepts

3. **Contextual retrieval**:
   - Retrieve surrounding chunks
   - Expand context window
   - Deduplicate results

## Phase 4: LLM Integration

### 4.1 LLM Client
**File**: `src/llm/llm_client.py`

Implement Ollama client for Gemma 2 12B:

```python
import requests
from typing import List, Dict, Optional
import json

class OllamaClient:
    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "gemma3:12b-instruct-q4_K_M"
    ):
        self.base_url = base_url
        self.model = model
    
    def generate(
        self,
        prompt: str,
        max_tokens: int = 500,
        temperature: float = 0.7,
        stream: bool = False
    ) -> str:
        """Generate text using Ollama"""
        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": stream,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens,
                    "top_p": 0.9,
                    "top_k": 40
                }
            }
        )
        response.raise_for_status()
        
        if stream:
            return self._handle_stream(response)
        else:
            return response.json()["response"]
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 500,
        temperature: float = 0.7
    ) -> str:
        """Chat completion format (recommended for Gemma 2)"""
        response = requests.post(
            f"{self.base_url}/api/chat",
            json={
                "model": self.model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            }
        )
        response.raise_for_status()
        return response.json()["message"]["content"]
    
    def _handle_stream(self, response):
        """Handle streaming responses"""
        full_response = ""
        for line in response.iter_lines():
            if line:
                chunk = json.loads(line)
                if "response" in chunk:
                    full_response += chunk["response"]
                    print(chunk["response"], end="", flush=True)
        print()  # New line after streaming
        return full_response
    
    def test_connection(self) -> bool:
        """Test if Ollama is accessible"""
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            return response.status_code == 200
        except:
            return False

# Usage
llm_client = OllamaClient(
    base_url="http://localhost:11434",
    model="gemma3:12b-instruct-q4_K_M"
)

# Test connection
if llm_client.test_connection():
    print("✓ Connected to Ollama")
else:
    print("✗ Cannot connect to Ollama")
```

**Why Gemma 3 over Gemma 2:**
- **Multimodal**: Processes both text and images (future-proof for document analysis)
- **Extended Context**: 128K tokens vs 8K (better for long documents)
- **Better Reasoning**: Improved performance on complex queries
- **Multilingual**: Support for 140+ languages
- **Same Resource Requirements**: Similar memory footprint with quantization

Benefits of Ollama over LM Studio:
- Container-friendly (no GUI)
- OpenAI-compatible API
- Easy model management
- Better for production deployment
- Works seamlessly with Podman/Docker

### 4.2 Prompt Templates
**File**: `src/llm/prompt_templates.py`

Create templates for:

1. **RAG Query Template**:
```
Context: {retrieved_chunks}

Question: {user_question}

Instructions: Answer based on the provided context. If the answer isn't in the context, say so.

Answer:
```

2. **Reasoning Template**:
```
Task: {task_description}

Available Information: {context}

Think step-by-step:
1. What information do I have?
2. What information do I need?
3. What actions should I take?
4. What is my confidence level?

Reasoning:
```

3. **Reflection Template**:
```
Generated Answer: {answer}

Retrieved Context: {context}

Evaluate:
- Relevance: Does the answer address the question?
- Accuracy: Is the answer supported by the context?
- Completeness: Is anything missing?
- Confidence: How confident am I (0-100%)?

Reflection:
```

## Phase 5: Agentic Components

### 5.1 Reasoning Engine
**File**: `src/agent/reasoning_engine.py`

Implement:
1. **Query Analysis**:
   - Understand user intent
   - Identify required information
   - Plan retrieval strategy

2. **Chain-of-Thought Reasoning**:
   - Break down complex questions
   - Generate intermediate steps
   - Synthesize final answer

3. **Decision Making**:
   - Determine if tools are needed
   - Select appropriate tools
   - Evaluate results

### 5.2 Tool Manager
**File**: `src/agent/tool_manager.py`

Implement tool-calling system:

**Available Tools**:
1. `search_knowledge_base(query)` - RAG retrieval
2. `calculate(expression)` - Math operations
3. `summarize_section(section_name)` - Summarize specific content
4. `compare_concepts(concept1, concept2)` - Compare topics
5. `get_examples(concept)` - Find examples from knowledge base

Tool execution flow:
```python
class ToolManager:
    def register_tool(self, name, function, description):
        # Register available tools
        
    def execute_tool(self, tool_name, **kwargs):
        # Execute tool with error handling
        # Log execution
        # Return results
        
    def get_tool_descriptions(self):
        # Return tool descriptions for LLM
```

### 5.3 Reflection Module
**File**: `src/agent/reflection_module.py`

Implement self-reflection:

1. **Answer Quality Assessment**:
   - Check relevance to question
   - Verify context support
   - Identify gaps or uncertainties

2. **Confidence Scoring**:
   - Calculate confidence based on:
     - Retrieval similarity scores
     - Context coverage
     - Answer coherence

3. **Self-Correction**:
   - Identify potential errors
   - Suggest improvements
   - Trigger re-retrieval if needed

4. **Explanation Generation**:
   - Explain reasoning process
   - Cite sources
   - Acknowledge limitations

## Phase 6: Evaluation System

### 6.1 Evaluation Metrics
**File**: `src/evaluation/evaluator.py`

Implement metrics:

1. **Retrieval Metrics**:
   - Precision@k
   - Recall@k
   - MRR (Mean Reciprocal Rank)

2. **Generation Metrics**:
   - Relevance (LLM-as-judge)
   - Faithfulness (context adherence)
   - Answer completeness

3. **RAG-Specific Metrics** (using RAGAS):
   - Context relevance
   - Answer relevance
   - Faithfulness
   - Context recall

4. **Agent Metrics**:
   - Tool usage accuracy
   - Reasoning coherence
   - Reflection quality

### 6.2 Test Suite
**File**: `tests/test_questions.py`

Create test questions:
```python
TEST_QUESTIONS = [
    {
        "question": "What are the production 'Do's' for RAG?",
        "expected_topics": ["production", "best practices", "RAG"],
        "difficulty": "medium"
    },
    {
        "question": "What is the difference between standard retrieval and the ColPali approach?",
        "expected_topics": ["ColPali", "retrieval", "comparison"],
        "difficulty": "hard"
    },
    {
        "question": "Why is hybrid search better than vector-only search?",
        "expected_topics": ["hybrid search", "vector search", "advantages"],
        "difficulty": "medium"
    },
    # Add 5-10 more questions
]
```

## Phase 7: Main Application

### 7.1 Flask API Backend
**File**: `api/app.py`

Create Flask application with REST API endpoints:

```python
from flask import Flask, request, jsonify
from flask_cors import CORS
from flasgger import Swagger
import os
import sys

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.embeddings.vector_store import ChromaVectorStore
from src.embeddings.embedding_generator import OllamaEmbeddings
from src.retrieval.retriever import Retriever
from src.llm.llm_client import OllamaClient
from src.agent.reasoning_engine import ReasoningEngine
from src.agent.tool_manager import ToolManager
from src.agent.reflection_module import ReflectionModule
from src.evaluation.evaluator import Evaluator

app = Flask(__name__)
CORS(app)  # Enable CORS for Open WebUI

# Swagger API documentation
swagger = Swagger(app)

# Initialize RAG Agent components
class RAGAgent:
    def __init__(self):
        # Initialize all components
        self.vector_store = ChromaVectorStore(
            host=os.getenv("CHROMA_HOST", "localhost"),
            port=int(os.getenv("CHROMA_PORT", 8000)),
            collection_name="rag_knowledge_base"
        )
        self.embeddings = OllamaEmbeddings(
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            model="nomic-embed-text"
        )
        self.retriever = Retriever(self.vector_store, self.embeddings)
        self.llm_client = OllamaClient(
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            model="gemma3:12b-instruct-q4_K_M"
        )
        self.reasoning_engine = ReasoningEngine(self.llm_client)
        self.tool_manager = ToolManager()
        self.reflection_module = ReflectionModule(self.llm_client)
        self.evaluator = Evaluator()
        
    def process_query(self, question: str, include_reasoning: bool = True):
        """Process a query through the RAG pipeline"""
        # 1. Analyze query
        analysis = self.reasoning_engine.analyze_query(question)
        
        # 2. Retrieve context
        context = self.retriever.retrieve(question, top_k=5)
        
        # 3. Determine if tools needed
        if analysis.get('requires_tools', False):
            tool_results = self.tool_manager.execute_tools(analysis['tools'])
            context.extend(tool_results)
        
        # 4. Generate answer
        answer = self.llm_client.generate(
            prompt=self.create_prompt(question, context)
        )
        
        # 5. Reflect on answer
        reflection = self.reflection_module.reflect(
            question, context, answer
        )
        
        # 6. Self-correct if needed
        if reflection.get('confidence', 1.0) < 0.7:
            answer = self.self_correct(question, context, answer, reflection)
        
        result = {
            "answer": answer,
            "confidence": reflection.get('confidence', 1.0),
            "sources": [c.get('metadata', {}) for c in context]
        }
        
        if include_reasoning:
            result.update({
                "reasoning": analysis,
                "reflection": reflection,
                "context_count": len(context)
            })
        
        return result
    
    def create_prompt(self, question: str, context: list) -> str:
        """Create prompt for LLM"""
        context_text = "\n\n".join([
            f"[Source {i+1}]: {c.get('document', '')}"
            for i, c in enumerate(context)
        ])
        
        return f"""Context from knowledge base:
{context_text}

Question: {question}

Instructions: Answer the question based on the provided context. If the answer isn't in the context, say so. Cite sources when possible.

Answer:"""
    
    def self_correct(self, question, context, answer, reflection):
        """Self-correction mechanism"""
        # Implement self-correction logic
        return answer

# Initialize agent
agent = RAGAgent()

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    ---
    responses:
      200:
        description: Service is healthy
    """
    return jsonify({
        "status": "healthy",
        "services": {
            "ollama": agent.llm_client.test_connection(),
            "chromadb": True,  # Add actual check
        }
    })

# Chat endpoint (compatible with Open WebUI)
@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Chat endpoint for conversational queries
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            message:
              type: string
              description: User's question
            include_reasoning:
              type: boolean
              description: Include reasoning and reflection in response
    responses:
      200:
        description: Successful response
      400:
        description: Bad request
      500:
        description: Internal server error
    """
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({"error": "Missing 'message' in request"}), 400
        
        message = data['message']
        include_reasoning = data.get('include_reasoning', False)
        
        result = agent.process_query(message, include_reasoning)
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# RAG query endpoint
@app.route('/api/rag/query', methods=['POST'])
def rag_query():
    """
    RAG query endpoint with full agent capabilities
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            question:
              type: string
              description: User's question
            top_k:
              type: integer
              description: Number of context chunks to retrieve
            include_reasoning:
              type: boolean
              description: Include reasoning and reflection
    responses:
      200:
        description: Successful response with answer and metadata
    """
    try:
        data = request.get_json()
        question = data.get('question')
        include_reasoning = data.get('include_reasoning', True)
        
        if not question:
            return jsonify({"error": "Missing 'question' parameter"}), 400
        
        result = agent.process_query(question, include_reasoning)
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Retrieve context endpoint
@app.route('/api/rag/retrieve', methods=['POST'])
def retrieve_context():
    """
    Retrieve relevant context without generating answer
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            query:
              type: string
            top_k:
              type: integer
    responses:
      200:
        description: Retrieved context chunks
    """
    try:
        data = request.get_json()
        query = data.get('query')
        top_k = data.get('top_k', 5)
        
        if not query:
            return jsonify({"error": "Missing 'query' parameter"}), 400
        
        context = agent.retriever.retrieve(query, top_k=top_k)
        
        return jsonify({
            "context": context,
            "count": len(context)
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Evaluation endpoint
@app.route('/api/evaluate', methods=['POST'])
def evaluate():
    """
    Evaluate RAG system performance
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            test_questions:
              type: array
              items:
                type: object
    responses:
      200:
        description: Evaluation results
    """
    try:
        data = request.get_json()
        test_questions = data.get('test_questions', [])
        
        results = []
        for item in test_questions:
            question = item.get('question')
            result = agent.process_query(question)
            results.append({
                "question": question,
                "answer": result['answer'],
                "confidence": result['confidence']
            })
        
        return jsonify({
            "results": results,
            "total": len(results)
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Admin: Get collection stats
@app.route('/api/admin/stats', methods=['GET'])
def get_stats():
    """
    Get vector store statistics
    ---
    responses:
      200:
        description: Collection statistics
    """
    try:
        stats = agent.vector_store.get_collection_stats()
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Use Gunicorn in production
    app.run(host='0.0.0.0', port=5000, debug=False)
```

### 7.2 Open WebUI Integration

**Open WebUI** provides a modern, ChatGPT-like interface for your RAG agent.

**Features:**
- Beautiful chat interface
- Conversation history
- Model selection
- Document upload
- User authentication
- Mobile responsive

**Access:**
- Open WebUI: http://localhost:3000
- Flask API: http://localhost:5000
- API Docs: http://localhost:5000/apidocs

**Configuration:**

1. **Connect Open WebUI to Ollama:**
   - Open http://localhost:3000
   - Sign up (first user becomes admin)
   - Go to Settings → Connections
   - Ollama URL should be: http://ollama:11434

2. **Add Custom RAG Endpoint:**
   Create `api/routes/openwebui_integration.py`:
   ```python
   from flask import Blueprint, request, jsonify, stream_with_context, Response
   import json
   
   openwebui_bp = Blueprint('openwebui', __name__)
   
   @openwebui_bp.route('/api/openwebui/chat', methods=['POST'])
   def openwebui_chat():
       """
       OpenAI-compatible chat endpoint for Open WebUI
       """
       try:
           data = request.get_json()
           messages = data.get('messages', [])
           stream = data.get('stream', False)
           
           # Get last user message
           user_message = next(
               (m['content'] for m in reversed(messages) if m['role'] == 'user'),
               None
           )
           
           if not user_message:
               return jsonify({"error": "No user message found"}), 400
           
           # Process through RAG agent
           result = agent.process_query(user_message, include_reasoning=False)
           
           if stream:
               def generate():
                   # Simulate streaming
                   words = result['answer'].split()
                   for word in words:
                       chunk = {
                           "choices": [{
                               "delta": {"content": word + " "},
                               "index": 0,
                               "finish_reason": None
                           }]
                       }
                       yield f"data: {json.dumps(chunk)}\n\n"
                   
                   # Final chunk
                   final_chunk = {
                       "choices": [{
                           "delta": {},
                           "index": 0,
                           "finish_reason": "stop"
                       }]
                   }
                   yield f"data: {json.dumps(final_chunk)}\n\n"
                   yield "data: [DONE]\n\n"
               
               return Response(
                   stream_with_context(generate()),
                   mimetype='text/event-stream'
               )
           else:
               return jsonify({
                   "choices": [{
                       "message": {
                           "role": "assistant",
                           "content": result['answer']
                       },
                       "finish_reason": "stop",
                       "index": 0
                   }],
                   "model": "rag-agent",
                   "usage": {
                       "prompt_tokens": 0,
                       "completion_tokens": 0,
                       "total_tokens": 0
                   }
               })
           
       except Exception as e:
           return jsonify({"error": str(e)}), 500
   ```

3. **Register Blueprint in app.py:**
   ```python
   from api.routes.openwebui_integration import openwebui_bp
   app.register_blueprint(openwebui_bp)
   ```

### 7.3 CLI Interface (Optional)
**File**: `main.py`

Create interactive CLI for testing:
```python
import sys
import os
sys.path.append(os.path.dirname(__file__))

from src.embeddings.vector_store import ChromaVectorStore
from src.embeddings.embedding_generator import OllamaEmbeddings
from src.retrieval.retriever import Retriever
from src.llm.llm_client import OllamaClient
from src.agent.reasoning_engine import ReasoningEngine
from src.agent.tool_manager import ToolManager
from src.agent.reflection_module import ReflectionModule

class RAGAgentCLI:
    def __init__(self):
        print("Initializing RAG Agent...")
        self.vector_store = ChromaVectorStore()
        self.embeddings = OllamaEmbeddings()
        self.retriever = Retriever(self.vector_store, self.embeddings)
        self.llm_client = OllamaClient()
        self.reasoning_engine = ReasoningEngine(self.llm_client)
        self.tool_manager = ToolManager()
        self.reflection_module = ReflectionModule(self.llm_client)
        print("✓ RAG Agent initialized\n")
    
    def process_query(self, question: str):
        print(f"\n{'='*60}")
        print(f"Question: {question}")
        print(f"{'='*60}\n")
        
        # Retrieve context
        print("🔍 Retrieving context...")
        context = self.retriever.retrieve(question, top_k=5)
        print(f"✓ Retrieved {len(context)} relevant chunks\n")
        
        # Generate answer
        print("💭 Generating answer...")
        prompt = self.create_prompt(question, context)
        answer = self.llm_client.generate(prompt)
        print(f"\n📝 Answer:\n{answer}\n")
        
        # Reflect
        print("🤔 Reflecting on answer...")
        reflection = self.reflection_module.reflect(question, context, answer)
        print(f"✓ Confidence: {reflection.get('confidence', 0):.2%}\n")
        
        return answer
    
    def create_prompt(self, question: str, context: list) -> str:
        context_text = "\n\n".join([
            f"[Source {i+1}]: {c.get('document', '')}"
            for i, c in enumerate(context)
        ])
        
        return f"""Context from knowledge base:
{context_text}

Question: {question}

Instructions: Answer based on the provided context. If the answer isn't in the context, say so.

Answer:"""
    
    def run(self):
        print("AI-Agentic RAG System - CLI Mode")
        print("Type 'quit' to exit\n")
        
        while True:
            try:
                question = input("Question: ").strip()
                
                if question.lower() in ['quit', 'exit', 'q']:
                    print("Goodbye!")
                    break
                
                if not question:
                    continue
                
                self.process_query(question)
                
            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}\n")

if __name__ == "__main__":
    agent = RAGAgentCLI()
    agent.run()
```

## Phase 8: LinkedIn Post Generator

### 8.1 Post Generation Agent
**File**: `src/agent/post_generator.py`

Implement specialized agent for LinkedIn post:

```python
def generate_linkedin_post(agent_description, tech_stack, achievements):
    prompt = f"""
    Create a professional LinkedIn post about an AI agent I built.
    
    Agent Description: {agent_description}
    Technology Stack: {tech_stack}
    Key Achievements: {achievements}
    
    Context: This was built as part of the Ciklum AI Academy.
    
    Requirements:
    - 5-7 sentences
    - Professional but engaging tone
    - Mention Ciklum AI Academy
    - Highlight technical aspects
    - Include relevant hashtags
    
    Post:
    """
    
    return llm_client.generate(prompt)
```

## Phase 9: Documentation

### 9.1 README.md
Include:
- Project overview
- Installation instructions
- Usage examples
- Configuration guide
- Test results
- Architecture overview

### 9.2 architecture.mmd
Create Mermaid diagram showing:
- Data flow
- Component interactions
- Agent decision process
- Tool calling mechanism

### 9.3 Test Results Log
Document:
- Test questions
- Generated answers
- Evaluation metrics
- Reflection outputs
- Confidence scores

## Phase 10: Demo Video

### 10.1 Video Content (5 minutes)
1. **Introduction** (30s):
   - Project overview
   - Problem statement

2. **Architecture Walkthrough** (1m):
   - Show architecture diagram
   - Explain components

3. **Live Demo** (2m):
   - Run 3-4 test questions
   - Show reasoning process
   - Display reflection outputs
   - Demonstrate tool usage

4. **Technical Highlights** (1m):
   - RAG pipeline
   - Agentic features
   - Evaluation results

5. **Conclusion** (30s):
   - Key learnings
   - Future improvements

## Implementation Timeline

### Week 1: Foundation
- Day 1-2: Environment setup, data processing
- Day 3-4: Embedding generation, vector store
- Day 5-7: Basic RAG pipeline

### Week 2: Agentic Features
- Day 8-10: Reasoning engine, tool manager
- Day 11-12: Reflection module
- Day 13-14: Integration and testing

### Week 3: Evaluation & Polish
- Day 15-16: Evaluation system
- Day 17-18: LinkedIn post generator
- Day 19-20: Documentation, demo video
- Day 21: Final testing and submission

## Key Success Criteria

1. **Functionality**:
   - Successfully processes PDFs and audio
   - Retrieves relevant context
   - Generates accurate answers
   - Demonstrates reasoning and reflection

2. **Agentic Capabilities**:
   - Uses tools appropriately
   - Self-reflects on answers
   - Adjusts based on confidence
   - Explains reasoning

3. **Evaluation**:
   - Measurable metrics
   - Test suite with results
   - Performance analysis

4. **Documentation**:
   - Clear README
   - Architecture diagram
   - Well-commented code

5. **Presentation**:
   - Professional demo video
   - Coherent LinkedIn post
   - Accessible repository

## Troubleshooting Guide

### Common Issues:

1. **PDF extraction fails**:
   - Try pdfplumber instead of PyPDF2
   - Check for scanned PDFs (need OCR with pytesseract)
   - Verify file permissions

2. **Audio transcription slow**:
   - Use smaller Whisper model (tiny/base instead of medium/large)
   - Check if GPU is being utilized
   - Process shorter audio segments
   - Increase container resources

3. **Poor retrieval quality**:
   - Adjust chunk size (try 500-1000 tokens)
   - Implement hybrid search (vector + BM25)
   - Use better embedding model (nomic-embed-text recommended)
   - Add metadata filtering

4. **Ollama connection issues**:
   - Check if container is running: `podman ps`
   - Verify port mapping: `podman port ollama`
   - Test API: `curl http://localhost:11434/api/tags`
   - Check logs: `podman logs ollama`
   - Ensure models are pulled: `podman exec -it ollama ollama list`

5. **Whisper service errors**:
   - Check container status: `podman ps | grep whisper`
   - Verify audio file format (MP3, WAV, MP4 supported)
   - Check file size limits
   - Review logs: `podman logs whisper`

6. **ChromaDB connection issues**:
   - Verify container is running: `podman ps | grep chromadb`
   - Test endpoint: `curl http://localhost:8000/api/v1/heartbeat`
   - Check persistent volume: `podman volume inspect chroma_data`
   - Review logs: `podman logs chromadb`

7. **Low confidence scores**:
   - Improve chunking strategy (semantic boundaries)
   - Add more context to chunks (increase overlap)
   - Refine prompts for better reasoning
   - Adjust similarity threshold

8. **Out of memory errors**:
   - Use quantized models (Q4_K_M instead of full precision)
   - Switch to smaller model (gemma3:2b instead of 12b)
   - Reduce batch sizes
   - Increase container memory limits in docker-compose.yml

9. **Slow inference**:
   - Enable GPU support in docker-compose.yml
   - Use quantized models (Q4_K_M)
   - Reduce max_tokens parameter
   - Consider smaller model for faster responses

10. **Container networking issues**:
    - Use service names in URLs (e.g., `http://ollama:11434` not `localhost`)
    - Check if containers are on same network: `podman network inspect`
    - Verify port mappings in docker-compose.yml

## Next Steps

After completing the implementation:
1. Run full test suite
2. Generate evaluation report
3. Create demo video
4. Generate LinkedIn post
5. Prepare submission
6. Submit via official form

## Resources

### Documentation
- Ollama Documentation: https://ollama.ai/
- Ollama Python Library: https://github.com/ollama/ollama-python
- LangChain Documentation: https://python.langchain.com/
- ChromaDB Docs: https://docs.trychroma.com/
- Whisper ASR Webservice: https://github.com/ahmetoner/whisper-asr-webservice
- RAGAS: https://docs.ragas.io/
- Podman Compose: https://github.com/containers/podman-compose

### Model Information
- Gemma 3 Models: https://ollama.ai/library/gemma3
- Nomic Embed Text: https://ollama.ai/library/nomic-embed-text
- Ollama Model Library: https://ollama.ai/library

### Container Resources
- Ollama Docker Image: https://hub.docker.com/r/ollama/ollama
- ChromaDB Docker: https://hub.docker.com/r/chromadb/chroma
- Whisper ASR Docker: https://hub.docker.com/r/onerahmet/openai-whisper-asr-webservice

### Useful Commands

**Podman/Docker Management:**
```bash
# Start all services
podman-compose up -d

# Stop all services
podman-compose down

# View logs
podman-compose logs -f [service_name]

# Restart a service
podman-compose restart [service_name]

# Check resource usage
podman stats

# Clean up
podman-compose down -v  # Remove volumes too
```

**Ollama Management:**
```bash
# List available models
podman exec -it ollama ollama list

# Pull a model
podman exec -it ollama ollama pull gemma3:12b-instruct-q4_K_M

# Remove a model
podman exec -it ollama ollama rm [model_name]

# Show model info
podman exec -it ollama ollama show gemma3:12b-instruct-q4_K_M

# Test generation
podman exec -it ollama ollama run gemma3:12b-instruct-q4_K_M "Hello!"
```

**Debugging:**
```bash
# Enter container shell
podman exec -it [container_name] /bin/bash

# Check container health
podman inspect [container_name] | grep -A 10 Health

# View container resource limits
podman inspect [container_name] | grep -A 20 Resources
```


## Deployment Options

### Option 1: Full Stack on Laptop/Desktop (Recommended for Development)
All services containerized including the RAG application:
```bash
podman-compose up -d
```

### Option 2: Hybrid Approach
Services in containers, RAG app runs locally for development:
```bash
# Start only infrastructure services
podman-compose up -d ollama whisper chromadb

# Run app locally
python main.py
```

### Option 3: Raspberry Pi 5 Deployment

**Hardware Requirements:**
- Raspberry Pi 5 (8GB RAM)
- AI HAT+ with Hailo-8L NPU (26 TOPS)
- 64GB+ microSD or NVMe SSD (recommended)
- 27W USB-C PD power supply or 52Pi PD Power HAT
- Active cooling (fan)

**Software Setup:**

1. **Install Raspberry Pi OS (64-bit)**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Podman (Docker alternative for ARM)
sudo apt install -y podman podman-compose
```

2. **Install Hailo Software Stack**
```bash
# Install Hailo drivers and runtime
# Follow official Hailo installation guide for Raspberry Pi 5
# https://github.com/hailo-ai/hailort

# Verify Hailo device
ls /dev/hailo*  # Should show /dev/hailo0
```

3. **Clone Repository and Configure**
```bash
git clone <your-repo>
cd capstone-project

# Create .env for Raspberry Pi 5
cat > .env << EOF
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=gemma3:2b-instruct-q4_K_M
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
WHISPER_BASE_URL=http://whisper:9000
WHISPER_MODEL=tiny
CHROMA_HOST=chromadb
CHROMA_PORT=8000
FLASK_ENV=production
WEBUI_SECRET_KEY=$(openssl rand -hex 32)
EOF
```

4. **Modify docker-compose.yml for ARM Architecture**
```yaml
# Use ARM-compatible images
services:
  ollama:
    image: ollama/ollama:latest  # Supports ARM64
    # ... rest of config

  whisper:
    image: onerahmet/openai-whisper-asr-webservice:latest-arm64
    environment:
      - ASR_MODEL=tiny  # Use tiny model for Pi 5
    # ... rest of config
```

5. **Start Services**
```bash
# Pull ARM-compatible images
podman-compose pull

# Start all services
podman-compose up -d

# Monitor startup
podman-compose logs -f
```

6. **Pull Optimized Models for Raspberry Pi 5**
```bash
# Pull Gemma 3 2B (optimized for edge devices)
podman exec -it ollama ollama pull gemma3:2b-instruct-q4_K_M

# Pull embedding model
podman exec -it ollama ollama pull nomic-embed-text

# Verify models
podman exec -it ollama ollama list
```

7. **Process Data and Build Knowledge Base**
```bash
# Process resources folder
python src/data_processing/pdf_loader.py --input ./resources
python src/data_processing/audio_transcriber.py --input ./resources
python src/data_processing/text_chunker.py
python src/embeddings/embedding_generator.py
```

8. **Access the System**
- Open WebUI: http://raspberrypi.local:3000 (or http://<pi-ip>:3000)
- Flask API: http://raspberrypi.local:5000
- API Docs: http://raspberrypi.local:5000/apidocs

**Raspberry Pi 5 Performance Expectations:**
- **Gemma 3 2B Inference**: 5-15 tokens/second (CPU + NPU acceleration)
- **Whisper Tiny**: Real-time transcription for short audio clips
- **Memory Usage**: ~6GB under load (leaves 2GB for OS)
- **Storage**: 15GB for models + data
- **Power Consumption**: 8-12W under load

**Optimization Tips for Raspberry Pi 5:**

1. **Use NVMe SSD instead of microSD**
   - 5-10x faster I/O
   - Better for database operations
   - Longer lifespan

2. **Enable Hailo NPU Acceleration**
   - Convert models to Hailo HEF format for maximum performance
   - See `./PI5AI.md` for detailed instructions

3. **Reduce Context Window**
   - Use smaller chunk sizes (500 tokens instead of 1000)
   - Retrieve fewer chunks (top_k=3 instead of 5)

4. **Optimize Whisper**
   - Use `tiny` model for real-time performance
   - Process audio in smaller segments

5. **Monitor Thermals**
```bash
# Check CPU temperature
vcgencmd measure_temp

# Monitor system resources
htop
```

6. **Persistent Storage Configuration**
```bash
# Mount NVMe SSD (if using)
sudo mkdir -p /mnt/nvme
sudo mount /dev/nvme0n1p1 /mnt/nvme

# Move data directory to NVMe
sudo mv ./data /mnt/nvme/
ln -s /mnt/nvme/data ./data
```

**Raspberry Pi 5 Limitations:**
- Slower inference than desktop (5-15 tok/s vs 30-50 tok/s)
- Limited to smaller models (2B-7B range)
- Cannot run multiple large models simultaneously
- Requires active cooling for sustained workloads

**When to Use Raspberry Pi 5:**
- Edge deployment scenarios
- Portable AI assistant
- Low-power always-on system
- Learning edge AI deployment
- Cost-effective production prototype

**When to Use Laptop/Desktop:**
- Development and testing
- Larger models (12B+)
- Faster iteration cycles
- Multiple concurrent users
- Higher throughput requirements

For complete Raspberry Pi 5 hardware specifications and setup details, see `./PI5AI.md`.

### Option 4: Cloud Deployment
Deploy to cloud platforms:
- **AWS**: ECS/Fargate with ECR
- **Azure**: Container Instances
- **GCP**: Cloud Run
- **Self-hosted**: Any VM with Podman/Docker

## Performance Optimization

### CPU Optimization
For CPU-only deployment (laptop, desktop, or Raspberry Pi 5):
1. Use quantized models (Q4_K_M or Q4_0)
2. Reduce batch sizes
3. Optimize chunk sizes for faster retrieval
4. Consider smaller models for faster inference
5. Enable multi-threading where possible

**Model Selection by Platform:**
- **Laptop/Desktop (16GB+ RAM)**: gemma3:12b-instruct-q4_K_M
- **Laptop/Desktop (8-16GB RAM)**: gemma3:4b-instruct-q4_K_M
- **Raspberry Pi 5 (8GB RAM)**: gemma3:2b-instruct-q4_K_M

### Memory Management
Adjust container memory limits based on your hardware:
```yaml
services:
  ollama:
    deploy:
      resources:
        limits:
          memory: 10G  # Laptop/Desktop
          # memory: 4G  # Raspberry Pi 5
        reservations:
          memory: 8G   # Laptop/Desktop
          # memory: 3G  # Raspberry Pi 5
```

### Storage Optimization
- **Laptop/Desktop**: SSD recommended
- **Raspberry Pi 5**: NVMe SSD strongly recommended over microSD
- Use volume mounts for persistent data
- Regular cleanup of unused models

## Production Considerations

### Security
- Use environment variables for sensitive config
- Implement API authentication
- Use private container registry
- Enable TLS/SSL for external access
- Regular security updates

### Monitoring
- Add health checks to docker-compose.yml
- Implement logging (ELK stack, Loki)
- Monitor resource usage
- Track inference latency
- Set up alerts

### Scaling
- Use Kubernetes for orchestration
- Implement load balancing
- Add caching layer (Redis)
- Consider model serving frameworks (vLLM, TGI)

### Backup & Recovery
- Regular backups of ChromaDB volume
- Version control for models
- Document restore procedures
- Test disaster recovery

## Cost Optimization

### Model Selection
- **Development**: gemma3:2b-instruct-q4_K_M (1.6GB)
- **Production**: gemma3:12b-instruct-q4_K_M (7GB)

### Resource Allocation
- Start with minimal resources
- Monitor actual usage
- Scale based on demand
- Use spot instances for non-critical workloads

## Quick Start Guide

### Prerequisites
- Podman or Docker installed
- 14GB+ RAM available
- 25GB+ disk space

### 5-Minute Setup (Laptop/Desktop)
```bash
# 1. Clone repository
git clone <your-repo>
cd capstone-project

# 2. Create .env file
cat > .env << EOF
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=gemma3:12b-instruct-q4_K_M
WHISPER_BASE_URL=http://whisper:9000
CHROMA_HOST=chromadb
CHROMA_PORT=8000
FLASK_ENV=production
WEBUI_SECRET_KEY=$(openssl rand -hex 32)
EOF

# 3. Start all services
podman-compose up -d

# 4. Wait for services to be ready (30-60 seconds)
podman-compose logs -f

# 5. Pull models
podman exec -it ollama ollama pull gemma3:12b-instruct-q4_K_M
podman exec -it ollama ollama pull nomic-embed-text

# 6. Process data from ./resources folder
python src/data_processing/pdf_loader.py --input ./resources
python src/data_processing/audio_transcriber.py --input ./resources
python src/data_processing/text_chunker.py

# 7. Generate embeddings and populate vector store
python src/embeddings/embedding_generator.py

# 8. Access the system
# Open WebUI: http://localhost:3000
# Flask API: http://localhost:5000
# API Docs: http://localhost:5000/apidocs
```

### Quick Setup for Raspberry Pi 5
```bash
# 1. Clone repository
git clone <your-repo>
cd capstone-project

# 2. Create .env file (optimized for Pi 5)
cat > .env << EOF
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=gemma3:2b-instruct-q4_K_M
WHISPER_BASE_URL=http://whisper:9000
WHISPER_MODEL=tiny
CHROMA_HOST=chromadb
CHROMA_PORT=8000
FLASK_ENV=production
WEBUI_SECRET_KEY=$(openssl rand -hex 32)
EOF

# 3. Start all services
podman-compose up -d

# 4. Pull optimized models
podman exec -it ollama ollama pull gemma3:2b-instruct-q4_K_M
podman exec -it ollama ollama pull nomic-embed-text

# 5. Process data from ./resources folder
python src/data_processing/pdf_loader.py --input ./resources
python src/data_processing/audio_transcriber.py --input ./resources
python src/data_processing/text_chunker.py

# 6. Generate embeddings and populate vector store
python src/embeddings/embedding_generator.py

# 7. Access the system
# Open WebUI: http://raspberrypi.local:3000
# Flask API: http://raspberrypi.local:5000
```

### Verification
```bash
# Check all services are running
podman-compose ps

# Expected output:
# NAME         STATUS    PORTS
# ollama       Up        0.0.0.0:11434->11434/tcp
# whisper      Up        0.0.0.0:9000->9000/tcp
# chromadb     Up        0.0.0.0:8000->8000/tcp
# flask-api    Up        0.0.0.0:5000->5000/tcp
# open-webui   Up        0.0.0.0:3000->8080/tcp

# Test Ollama
curl http://localhost:11434/api/tags

# Test Whisper
curl http://localhost:9000/health

# Test ChromaDB
curl http://localhost:8000/api/v1/heartbeat

# Test Flask API
curl http://localhost:5000/health

# Test RAG query
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What are the production dos for RAG?"}'
```

### Using Open WebUI

1. **First Time Setup:**
   - Navigate to http://localhost:3000
   - Create an account (first user becomes admin)
   - Login with your credentials

2. **Configure Connection:**
   - Click Settings (gear icon)
   - Go to "Connections" tab
   - Verify Ollama URL: `http://ollama:11434`
   - Click "Verify Connection"

3. **Start Chatting:**
   - Select "gemma3:12b-instruct-q4_K_M" from model dropdown
   - Type your question in the chat box
   - The system will use RAG to answer based on your knowledge base

4. **Advanced Features:**
   - Upload documents directly in chat
   - View conversation history
   - Export conversations
   - Customize system prompts
   - Manage multiple conversations

### Using Flask API

**Example API Calls:**

```bash
# Simple chat
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is hybrid search?",
    "include_reasoning": false
  }'

# RAG query with full details
curl -X POST http://localhost:5000/api/rag/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the production dos for RAG?",
    "include_reasoning": true
  }'

# Retrieve context only
curl -X POST http://localhost:5000/api/rag/retrieve \
  -H "Content-Type: application/json" \
  -d '{
    "query": "ColPali approach",
    "top_k": 3
  }'

# Get system stats
curl http://localhost:5000/api/admin/stats
```

**Python Client Example:**

```python
import requests

# Chat endpoint
response = requests.post(
    'http://localhost:5000/api/chat',
    json={
        'message': 'Explain vector databases',
        'include_reasoning': True
    }
)

result = response.json()
print(f"Answer: {result['answer']}")
print(f"Confidence: {result['confidence']:.2%}")
```

## Migration from LM Studio

If you have existing LM Studio setup:

1. **Export your data**: Ensure all processed data is saved
2. **Update configuration**: Change base URLs from LM Studio to Ollama
3. **Pull equivalent models**: Find Ollama equivalents of your LM Studio models
4. **Test compatibility**: Verify API responses match expected format
5. **Update code**: Replace LMStudioClient with OllamaClient

**API Compatibility:**
Both use OpenAI-compatible APIs, so migration is straightforward:
```python
# LM Studio
base_url = "http://localhost:1234/v1"

# Ollama
base_url = "http://localhost:11434"
```

## Platform Comparison

### Laptop/Desktop vs Raspberry Pi 5

| Feature | Laptop/Desktop | Raspberry Pi 5 |
|---------|---------------|----------------|
| **Model Size** | Up to 12B+ | 2B-7B (2B recommended) |
| **Inference Speed** | 30-50 tok/s | 5-15 tok/s |
| **Memory** | 16GB+ | 8GB |
| **Storage** | SSD | NVMe SSD (recommended) |
| **Power** | 50-150W | 8-12W |
| **Cost** | $800-2000+ | $150-200 |
| **Portability** | Moderate | High |
| **Use Case** | Development, Production | Edge, Portable, Learning |
| **Cooling** | Usually adequate | Active cooling required |

### Switching Between Platforms

The containerized architecture makes it easy to switch between laptop and Raspberry Pi 5:

1. **Same codebase**: No code changes needed
2. **Different .env**: Just update model names and resource limits
3. **Same docker-compose.yml**: Works on both x86_64 and ARM64
4. **Portable data**: Copy `./data` and `./resources` folders

**Quick Switch:**
```bash
# On Laptop
OLLAMA_MODEL=gemma3:12b-instruct-q4_K_M

# On Raspberry Pi 5
OLLAMA_MODEL=gemma3:2b-instruct-q4_K_M
```

## Data Sources

All RAG knowledge base materials are located in `./resources/`:

**PDF Documents:**
- `RAG Intro.pdf` - Introduction to RAG concepts
- `Databases for GenAI.pdf` - Database considerations for GenAI
- `Productized & Enterprise RAG.pdf` - Production RAG systems
- `Architecture & Design Patterns.pdf` - RAG architecture patterns

**Video/Audio Files:**
- `1 part. RAG Intro.mp4` - RAG introduction lecture
- `1st Part_Productized Enterprise RAG.mp4` - Enterprise RAG lecture
- `2 part Databases for GenAI.mp4` - Databases lecture
- `2nd Part_Architecture & Design Patterns.mp4` - Architecture lecture

**Processing Pipeline:**
1. PDFs → Text extraction → Chunking → Embeddings
2. Audio/Video → Whisper transcription → Chunking → Embeddings
3. All embeddings → ChromaDB vector store
4. Ready for RAG queries

**Data Preparation Checklist:**
- [ ] Place all materials in `./resources/` folder
- [ ] Run PDF loader on all PDF files
- [ ] Run audio transcriber on all MP4 files
- [ ] Run text chunker on all processed text
- [ ] Generate embeddings and populate vector store
- [ ] Verify ChromaDB collection has documents
- [ ] Test retrieval with sample queries
