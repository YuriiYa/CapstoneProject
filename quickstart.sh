#!/bin/bash

# Quick Start Script for AI-Agentic RAG System
# This script sets up and starts all services

echo "======================================================================"
echo "AI-Agentic RAG System - Quick Start"
echo "======================================================================"
echo ""

# Check if docker-compose or podman-compose is available
if command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
    EXEC_CMD="docker"
elif command -v podman-compose &> /dev/null; then
    COMPOSE_CMD="podman-compose"
    EXEC_CMD="podman"
else
    echo "Error: Neither docker-compose nor podman-compose found!"
    echo "Please install Docker or Podman first."
    exit 1
fi

echo "Using: $COMPOSE_CMD"
echo ""

# Step 1: Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Step 1: Creating .env file..."
    cat > .env << EOF
# Ollama Configuration
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
FLASK_ENV=production
EOF
    echo "✓ .env file created"
else
    echo "Step 1: .env file already exists"
fi
echo ""

# Step 2: Start services
echo "Step 2: Starting services..."
$COMPOSE_CMD up -d

echo "Waiting for services to be ready..."
sleep 10
echo ""

# Step 3: Check service status
echo "Step 3: Checking service status..."
$COMPOSE_CMD ps
echo ""

# Step 4: Pull Ollama models
echo "Step 4: Pulling Ollama models..."
echo "This may take a few minutes..."
echo ""

echo "Pulling Gemma 3 12B model..."
$EXEC_CMD exec ollama ollama pull gemma3:12b-instruct-q4_K_M

echo ""
echo "Pulling nomic-embed-text model..."
$EXEC_CMD exec ollama ollama pull nomic-embed-text

echo ""
echo "✓ Models pulled successfully"
echo ""

# Step 5: Verify models
echo "Step 5: Verifying models..."
$EXEC_CMD exec ollama ollama list
echo ""

# Step 6: Test services
echo "Step 6: Testing services..."
echo ""

echo "Testing Ollama..."
curl -s http://localhost:11434/api/tags > /dev/null && echo "✓ Ollama is running" || echo "✗ Ollama is not responding"

echo "Testing Whisper..."
curl -s http://localhost:9000/health > /dev/null && echo "✓ Whisper is running" || echo "✗ Whisper is not responding"

echo "Testing ChromaDB..."
curl -s http://localhost:8000/api/v1/heartbeat > /dev/null && echo "✓ ChromaDB is running" || echo "✗ ChromaDB is not responding"

echo "Testing Flask API..."
curl -s http://localhost:5000/health > /dev/null && echo "✓ Flask API is running" || echo "✗ Flask API is not responding"

echo ""

# Summary
echo "======================================================================"
echo "Setup Complete!"
echo "======================================================================"
echo ""
echo "Services are running at:"
echo "  - Open WebUI:  http://localhost:3000"
echo "  - Flask API:   http://localhost:5000"
echo "  - Ollama:      http://localhost:11434"
echo "  - ChromaDB:    http://localhost:8000"
echo "  - Whisper:     http://localhost:9000"
echo ""
echo "Next steps:"
echo "  1. Process your data: python process_data.py"
echo "  2. Start using the CLI: python main.py"
echo "  3. Or open the web UI: http://localhost:3000"
echo ""
echo "For more information, see README.md"
echo ""
