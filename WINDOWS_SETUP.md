# Windows Setup Guide

## Issue with Docker Build on Windows

If you're seeing this error:
```
Error response from daemon: crun: creating cgroup directory
```

This is a known issue with Docker buildx on Windows. Here's the solution:

## Solution: Use Simplified Setup

Instead of building Flask in Docker, we'll run it locally on Windows. This is actually easier and works better for development!

### Step 1: Use the Simplified Docker Compose

```cmd
REM Stop any running containers
docker-compose down

REM Start services without Flask
docker-compose -f docker-compose.simple.yml up -d
```

This starts:
- ✅ Ollama (LLM)
- ✅ Whisper (Audio transcription)
- ✅ ChromaDB (Vector database)
- ✅ Open WebUI (Web interface)

### Step 2: Install Python Dependencies

```cmd
pip install -r requirements.txt
```

### Step 3: Pull Ollama Models

```cmd
docker exec ollama ollama pull gemma3:12b-instruct-q4_K_M
docker exec ollama ollama pull nomic-embed-text
```

### Step 4: Process Your Data

```cmd
python process_data.py
```

### Step 5: Run Flask API Locally

Open a **new terminal** and run:

```cmd
python api/app.py
```

Keep this terminal open - Flask will run here.

### Step 6: Use the System

Now you can use the system in multiple ways:

**Option A: CLI Interface**
```cmd
REM In another terminal
python main.py
```

**Option B: Web UI**
- Open browser to http://localhost:3000
- Create account and start chatting

**Option C: API Calls**
```cmd
curl -X POST http://localhost:5000/api/chat ^
  -H "Content-Type: application/json" ^
  -d "{\"message\": \"What are the production dos for RAG?\"}"
```

## Automated Setup (Recommended)

We've created a simplified script for Windows:

```cmd
quickstart-windows.bat
```

This will:
1. Create .env file
2. Start all services (except Flask)
3. Pull Ollama models
4. Verify everything is working

Then you just need to:
1. Install Python dependencies: `pip install -r requirements.txt`
2. Process data: `python process_data.py`
3. Start Flask: `python api/app.py` (in new terminal)
4. Use the system: `python main.py`

## Service URLs

| Service | URL | Status |
|---------|-----|--------|
| Ollama | http://localhost:11434 | ✅ In Docker |
| Whisper | http://localhost:9000 | ✅ In Docker |
| ChromaDB | http://localhost:8000 | ✅ In Docker |
| Open WebUI | http://localhost:3000 | ✅ In Docker |
| Flask API | http://localhost:5000 | ⚠️ Run locally |

## Why This Approach?

**Advantages:**
- ✅ No Docker build issues
- ✅ Easier to debug Flask code
- ✅ Faster development cycle
- ✅ Can edit code without rebuilding
- ✅ Better error messages

**Disadvantages:**
- ⚠️ Need to run Flask manually
- ⚠️ Need Python installed on Windows

## Troubleshooting

### Python not found
```cmd
REM Install Python 3.9+ from python.org
REM Or use Microsoft Store
```

### pip not found
```cmd
python -m pip install -r requirements.txt
```

### Port already in use
```cmd
REM Check what's using the port
netstat -ano | findstr :5000

REM Kill the process (replace PID)
taskkill /PID <PID> /F
```

### Docker services not starting
```cmd
REM Restart Docker Desktop
REM Then try again
docker-compose -f docker-compose.simple.yml up -d
```

### Cannot connect to services
```cmd
REM Make sure Docker Desktop is running
REM Check services are up
docker-compose -f docker-compose.simple.yml ps

REM Check logs
docker-compose -f docker-compose.simple.yml logs
```

## Alternative: Fix Docker Build (Advanced)

If you really want to use the full docker-compose with Flask in Docker:

### Option 1: Use Docker Desktop with WSL2
1. Install WSL2: `wsl --install`
2. Install Docker Desktop with WSL2 backend
3. Use the regular docker-compose.yml

### Option 2: Build Flask Image Manually
```cmd
REM Build the image
docker build -t flask-api -f Dockerfile.flask .

REM Update docker-compose.yml to use the image
REM Change:
REM   build:
REM     context: .
REM     dockerfile: Dockerfile.flask
REM To:
REM   image: flask-api
```

### Option 3: Use Podman Instead
```cmd
REM Install Podman Desktop for Windows
REM Use podman-compose instead of docker-compose
podman-compose -f docker-compose.simple.yml up -d
```

## Recommended Workflow for Windows

1. **Start services once:**
   ```cmd
   quickstart-windows.bat
   ```

2. **Process data once:**
   ```cmd
   python process_data.py
   ```

3. **During development:**
   - Keep services running in Docker
   - Run Flask locally: `python api/app.py`
   - Edit code and restart Flask as needed
   - Use CLI: `python main.py`

4. **When done:**
   ```cmd
   docker-compose -f docker-compose.simple.yml down
   ```

## Summary

The simplified approach (services in Docker, Flask local) is:
- ✅ Easier to set up on Windows
- ✅ Better for development
- ✅ Avoids Docker build issues
- ✅ Fully functional

You get the same functionality, just with Flask running locally instead of in Docker!
