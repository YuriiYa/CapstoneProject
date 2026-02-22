#!/bin/bash

# AI-Agentic RAG System - Docker Startup Script
# This script starts all services and initializes the models

set -e

echo "============================================================"
echo "AI-Agentic RAG System - Docker Startup"
echo "============================================================"
echo ""

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null && ! command -v docker &> /dev/null; then
    echo "Error: Neither docker-compose nor docker is installed"
    exit 1
fi

# Use docker compose (new) or docker-compose (old)
if docker compose version &> /dev/null; then
    DOCKER_COMPOSE="docker compose"
else
    DOCKER_COMPOSE="docker-compose"
fi

echo "Using: $DOCKER_COMPOSE"
echo ""

# Stop any existing containers
echo "Stopping existing containers..."
$DOCKER_COMPOSE down

# Start all services
echo ""
echo "Starting all services..."
echo "This may take a few minutes on first run..."
echo ""
$DOCKER_COMPOSE up -d

# Wait for services to be healthy
echo ""
echo "Waiting for services to be ready..."
echo ""

# Wait for Ollama
echo "Waiting for Ollama..."
until curl -s http://localhost:11434/api/tags > /dev/null 2>&1; do
    echo "  Ollama not ready yet, waiting..."
    sleep 5
done
echo "✓ Ollama is ready"

# Wait for Whisper
echo "Waiting for Whisper..."
until curl -s http://localhost:9000/ > /dev/null 2>&1; do
    echo "  Whisper not ready yet, waiting..."
    sleep 5
done
echo "✓ Whisper is ready"

# Wait for ChromaDB
echo "Waiting for ChromaDB..."
until curl -s http://localhost:8000/api/v1/heartbeat > /dev/null 2>&1; do
    echo "  ChromaDB not ready yet, waiting..."
    sleep 5
done
echo "✓ ChromaDB is ready"

# Wait for Open WebUI
echo "Waiting for Open WebUI..."
until curl -s http://localhost:3000/ > /dev/null 2>&1; do
    echo "  Open WebUI not ready yet, waiting..."
    sleep 5
done
echo "✓ Open WebUI is ready"

# Pull Ollama models
echo ""
echo "============================================================"
echo "Pulling Ollama Models"
echo "============================================================"
echo ""

echo "Pulling Gemma 3 12B model (this may take 10-20 minutes)..."
docker exec ollama ollama pull gemma3:12b-instruct-q4_K_M

echo ""
echo "Pulling nomic-embed-text model..."
docker exec ollama ollama pull nomic-embed-text

echo ""
echo "============================================================"
echo "All Services Ready!"
echo "============================================================"
echo ""
echo "Services:"
echo "  - Ollama:      http://localhost:11434"
echo "  - Whisper:     http://localhost:9000"
echo "  - ChromaDB:    http://localhost:8000"
echo "  - Flask API:   http://localhost:5000"
echo "  - Open WebUI:  http://localhost:3000"
echo ""
echo "Next steps:"
echo "  1. Process data: python process_data.py"
echo "  2. Open browser: http://localhost:3000"
echo ""
echo "To view logs: $DOCKER_COMPOSE logs -f"
echo "To stop:      $DOCKER_COMPOSE down"
echo ""
