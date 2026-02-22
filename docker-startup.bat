@echo off
REM AI-Agentic RAG System - Docker Startup Script (Windows)
REM This script starts all services and initializes the models

echo ============================================================
echo AI-Agentic RAG System - Docker Startup
echo ============================================================
echo.

REM Check if docker or podman is available
where docker >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    set DOCKER_CMD=docker
    set COMPOSE_CMD=docker compose
    echo Using: Docker
) else (
    where podman >nul 2>nul
    if %ERRORLEVEL% EQU 0 (
        set DOCKER_CMD=podman
        set COMPOSE_CMD=podman-compose
        echo Using: Podman
    ) else (
        echo Error: Neither Docker nor Podman is installed
        exit /b 1
    )
)
echo.

REM Stop any existing containers
echo Stopping existing containers...
%COMPOSE_CMD% down

REM Start all services
echo.
echo Starting all services...
echo This may take a few minutes on first run...
echo.
%COMPOSE_CMD% up -d

REM Wait for services to be ready
echo.
echo Waiting for services to be ready...
echo.

REM Wait for Ollama
echo Waiting for Ollama...
:wait_ollama
curl -s http://localhost:11434/api/tags >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo   Ollama not ready yet, waiting...
    timeout /t 5 /nobreak >nul
    goto wait_ollama
)
echo √ Ollama is ready

REM Wait for Whisper
echo Waiting for Whisper...
:wait_whisper
curl -s http://localhost:9000/ >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo   Whisper not ready yet, waiting...
    timeout /t 5 /nobreak >nul
    goto wait_whisper
)
echo √ Whisper is ready

REM Wait for ChromaDB
echo Waiting for ChromaDB...
:wait_chroma
curl -s http://localhost:8000/api/v1/heartbeat >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo   ChromaDB not ready yet, waiting...
    timeout /t 5 /nobreak >nul
    goto wait_chroma
)
echo √ ChromaDB is ready

REM Wait for Open WebUI
echo Waiting for Open WebUI...
:wait_webui
curl -s http://localhost:3000/ >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo   Open WebUI not ready yet, waiting...
    timeout /t 5 /nobreak >nul
    goto wait_webui
)
echo √ Open WebUI is ready

REM Pull Ollama models
echo.
echo ============================================================
echo Pulling Ollama Models
echo ============================================================
echo.

echo Pulling Gemma 3 12B model (this may take 10-20 minutes)...
%DOCKER_CMD% exec ollama ollama pull gemma3:12b-instruct-q4_K_M

echo.
echo Pulling nomic-embed-text model...
%DOCKER_CMD% exec ollama ollama pull nomic-embed-text

echo.
echo ============================================================
echo All Services Ready!
echo ============================================================
echo.
echo Services:
echo   - Ollama:      http://localhost:11434
echo   - Whisper:     http://localhost:9000
echo   - ChromaDB:    http://localhost:8000
echo   - Flask API:   http://localhost:5000
echo   - Open WebUI:  http://localhost:3000
echo.
echo Next steps:
echo   1. Process data: python process_data.py
echo   2. Open browser: http://localhost:3000
echo.
echo To view logs: %COMPOSE_CMD% logs -f
echo To stop:      %COMPOSE_CMD% down
echo.
pause
