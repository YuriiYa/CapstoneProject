# Start Here - Windows Quick Setup

## Your Current Situation

You're on Windows and got a Docker build error. This is normal! Here's the fix:

## Solution: 3 Simple Steps

### Step 1: Start Services (Without Flask)

```cmd
docker-compose -f docker-compose.simple.yml up -d
```

Wait about 30 seconds for services to start.

### Step 2: Pull Models

```cmd
# gemma-3-12b-it-Q4_K_M:latest
podman exec ollama ollama pull kwangsuklee/gemma-3-12b-it-Q4_K_M
podman exec ollama ollama pull nomic-embed-text
```

This will take 5-10 minutes (downloading ~8GB).

### Step 3: Verify Everything Works

```cmd
podman exec ollama ollama list
```

You should see both models listed.

## That's It for Docker!

Now you have:
- ✅ Ollama running (http://localhost:11434)
- ✅ Whisper running (http://localhost:9000)
- ✅ ChromaDB running (http://localhost:8000)
- ✅ Open WebUI running (http://localhost:3000)

## Next: Install Python Dependencies

```cmd
pip install -r requirements.txt
```

## Next: Process Your Data

```cmd
python process_data.py
```

This will:
- Extract text from PDFs in ./resources
- Transcribe audio files in ./resources
- Create embeddings
- Populate ChromaDB

## Next: Run Flask API Locally

Open a **NEW terminal window** and run:

```cmd
python api/app.py
```

Keep this terminal open. You should see:
```
Flask API running on http://0.0.0.0:5000
```

## Now Use the System!

### Option 1: CLI Interface (Recommended for Testing)

Open **another new terminal** and run:

```cmd
python main.py
```

Then type:
```
test
```

This will run the 3 required test questions!

### Option 2: Web Interface

Open browser to: http://localhost:3000

1. Create an account (first user = admin)
2. Select model: "gemma3:12b-instruct-q4_K_M"
3. Start asking questions!

### Option 3: API Calls

```cmd
curl -X POST http://localhost:5000/api/chat ^
  -H "Content-Type: application/json" ^
  -d "{\"message\": \"What are the production dos for RAG?\"}"
```

## Summary of What's Running

| Component | Where | URL |
|-----------|-------|-----|
| Ollama | Docker | http://localhost:11434 |
| Whisper | Docker | http://localhost:9000 |
| ChromaDB | Docker | http://localhost:8000 |
| Open WebUI | Docker | http://localhost:3000 |
| Flask API | **Local Python** | http://localhost:5000 |

## Why Flask Runs Locally?

Docker build has issues on Windows. Running Flask locally:
- ✅ Avoids the build error
- ✅ Easier to debug
- ✅ Faster to edit code
- ✅ Same functionality

## Troubleshooting

### "pip not found"
```cmd
python -m pip install -r requirements.txt
```

### "python not found"
Install Python 3.9+ from python.org

### "Port 5000 already in use"
```cmd
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### Services not starting
```cmd
REM Restart Docker Desktop
REM Then try again
docker-compose -f docker-compose.simple.yml restart
```

## Complete Command Sequence

Here's everything in order:

```cmd
REM 1. Start Docker services
docker-compose -f docker-compose.simple.yml up -d

REM 2. Pull models (wait 5-10 minutes)
docker exec ollama ollama pull gemma3:12b-instruct-q4_K_M
docker exec ollama ollama pull nomic-embed-text

REM 3. Install Python dependencies
pip install -r requirements.txt

REM 4. Process data
python process_data.py

REM 5. Start Flask (in NEW terminal)
python api/app.py

REM 6. Use the system (in ANOTHER NEW terminal)
python main.py
```

## Need More Help?

- See [WINDOWS_SETUP.md](./WINDOWS_SETUP.md) for detailed guide
- See [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) for common issues
- See [QUICK_REFERENCE.md](./QUICK_REFERENCE.md) for command reference

## You're All Set!

Once you complete these steps, you'll have a fully functional AI-Agentic RAG system running on Windows! 🚀
