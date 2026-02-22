@echo off
REM Quick Start Script for AI-Agentic RAG System (Windows)

echo ======================================================================
echo AI-Agentic RAG System - Quick Start
echo ======================================================================
echo.

REM Check if docker-compose is available
where docker-compose >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    set COMPOSE_CMD=docker-compose
    set EXEC_CMD=docker
    echo Using: docker-compose
) else (
    where podman-compose >nul 2>nul
    if %ERRORLEVEL% EQU 0 (
        set COMPOSE_CMD=podman-compose
        set EXEC_CMD=podman
        echo Using: podman-compose
    ) else (
        echo Error: Neither docker-compose nor podman-compose found!
        echo Please install Docker or Podman first.
        pause
        exit /b 1
    )
)
echo.

REM Step 1: Create .env file if it doesn't exist
if not exist .env (
    echo Step 1: Creating .env file...
    (
        echo # Ollama Configuration
        echo OLLAMA_BASE_URL=http://ollama:11434
        echo OLLAMA_MODEL=gemma3:12b-instruct-q4_K_M
        echo OLLAMA_EMBEDDING_MODEL=nomic-embed-text
        echo.
        echo # Whisper Configuration
        echo WHISPER_BASE_URL=http://whisper:9000
        echo WHISPER_MODEL=base
        echo.
        echo # ChromaDB Configuration
        echo CHROMA_HOST=chromadb
        echo CHROMA_PORT=8000
        echo CHROMA_COLLECTION_NAME=rag_knowledge_base
        echo.
        echo # Application Configuration
        echo MAX_TOKENS=500
        echo TEMPERATURE=0.7
        echo TOP_K_RETRIEVAL=5
        echo CHUNK_SIZE=800
        echo CHUNK_OVERLAP=150
        echo FLASK_ENV=production
    ) > .env
    echo Done: .env file created
) else (
    echo Step 1: .env file already exists
)
echo.

REM Step 2: Start services
echo Step 2: Starting services...
%COMPOSE_CMD% up -d

echo Waiting for services to be ready...
timeout /t 10 /nobreak >nul
echo.

REM Step 3: Check service status
echo Step 3: Checking service status...
%COMPOSE_CMD% ps
echo.

REM Step 4: Pull Ollama models
echo Step 4: Pulling Ollama models...
echo This may take a few minutes...
echo.

echo Pulling Gemma 3 12B model...
%EXEC_CMD% exec ollama ollama pull gemma3:12b-instruct-q4_K_M

echo.
echo Pulling nomic-embed-text model...
%EXEC_CMD% exec ollama ollama pull nomic-embed-text

echo.
echo Done: Models pulled successfully
echo.

REM Step 5: Verify models
echo Step 5: Verifying models...
%EXEC_CMD% exec ollama ollama list
echo.

REM Step 6: Test services
echo Step 6: Testing services...
echo.

echo Testing Ollama...
curl -s http://localhost:11434/api/tags >nul 2>&1 && echo Done: Ollama is running || echo Error: Ollama is not responding

echo Testing Whisper...
curl -s http://localhost:9000/health >nul 2>&1 && echo Done: Whisper is running || echo Error: Whisper is not responding

echo Testing ChromaDB...
curl -s http://localhost:8000/api/v1/heartbeat >nul 2>&1 && echo Done: ChromaDB is running || echo Error: ChromaDB is not responding

echo Testing Flask API...
curl -s http://localhost:5000/health >nul 2>&1 && echo Done: Flask API is running || echo Error: Flask API is not responding

echo.

REM Summary
echo ======================================================================
echo Setup Complete!
echo ======================================================================
echo.
echo Services are running at:
echo   - Open WebUI:  http://localhost:3000
echo   - Flask API:   http://localhost:5000
echo   - Ollama:      http://localhost:11434
echo   - ChromaDB:    http://localhost:8000
echo   - Whisper:     http://localhost:9000
echo.
echo Next steps:
echo   1. Process your data: python process_data.py
echo   2. Start using the CLI: python main.py
echo   3. Or open the web UI: http://localhost:3000
echo.
echo For more information, see README.md
echo.

pause
