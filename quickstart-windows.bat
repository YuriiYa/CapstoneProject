@echo off
REM Quick Start Script for Windows (Simplified - No Flask Build)
REM This version runs Flask locally to avoid Docker build issues on Windows

echo ======================================================================
echo AI-Agentic RAG System - Quick Start (Windows Simplified)
echo ======================================================================
echo.

REM Check if docker-compose is available
where docker-compose >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: docker-compose not found!
    echo Please install Docker Desktop for Windows first.
    pause
    exit /b 1
)

echo Using: docker-compose
echo.

REM Step 1: Create .env file if it doesn't exist
if not exist .env (
    echo Step 1: Creating .env file...
    (
        echo # Ollama Configuration
        echo OLLAMA_BASE_URL=http://localhost:11434
        echo OLLAMA_MODEL=gemma3:12b-instruct-q4_K_M
        echo OLLAMA_EMBEDDING_MODEL=nomic-embed-text
        echo.
        echo # Whisper Configuration
        echo WHISPER_BASE_URL=http://localhost:9000
        echo WHISPER_MODEL=base
        echo.
        echo # ChromaDB Configuration
        echo CHROMA_HOST=localhost
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

REM Step 2: Start services (using simplified compose file)
echo Step 2: Starting services (Ollama, Whisper, ChromaDB, Open WebUI)...
echo Note: Flask API will run locally to avoid build issues
docker-compose -f docker-compose.simple.yml up -d

echo Waiting for services to be ready...
timeout /t 15 /nobreak >nul
echo.

REM Step 3: Check service status
echo Step 3: Checking service status...
docker-compose -f docker-compose.simple.yml ps
echo.

REM Step 4: Pull Ollama models
echo Step 4: Pulling Ollama models...
echo This may take a few minutes...
echo.

echo Pulling Gemma 3 12B model...
docker exec ollama ollama pull gemma3:12b-instruct-q4_K_M

echo.
echo Pulling nomic-embed-text model...
docker exec ollama ollama pull nomic-embed-text

echo.
echo Done: Models pulled successfully
echo.

REM Step 5: Verify models
echo Step 5: Verifying models...
docker exec ollama ollama list
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

echo.

REM Summary
echo ======================================================================
echo Setup Complete!
echo ======================================================================
echo.
echo Services are running at:
echo   - Ollama:      http://localhost:11434
echo   - Whisper:     http://localhost:9000
echo   - ChromaDB:    http://localhost:8000
echo   - Open WebUI:  http://localhost:3000
echo.
echo IMPORTANT: Flask API is NOT running in Docker
echo To start Flask API locally, open a new terminal and run:
echo   python api/app.py
echo.
echo Next steps:
echo   1. Install Python dependencies: pip install -r requirements.txt
echo   2. Process your data: python process_data.py
echo   3. Start Flask API: python api/app.py (in a new terminal)
echo   4. Start using the CLI: python main.py
echo   5. Or open the web UI: http://localhost:3000
echo.
echo For more information, see README.md
echo.

pause
