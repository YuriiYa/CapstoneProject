# Flask API Connection Fix for Open WebUI

## Problem Identified ✓

`podman exec open-webui cat /etc/hosts`
111.111.1.1     host.docker.internal
127.0.0.1       localhost
::1     localhost
111.111.1.1     host.containers.internal
11.11.1.11      29696462261a open-webui

`ipconfig | Select-String "IPv4" -Context 0,0`

- `host.docker.internal` resolves to `111.111.1.1` (doesn't work)
- Your actual host IP is `222.22.22.2` (doesn't work)

Check firewall 

`netsh advfirewall show allprofiles | Select-String "LogAllowedConnections|LogDroppedConnections"`
# Enable logging
`netsh advfirewall set allprofiles logging droppedconnections enable`

Check if Rule Exists
`netsh advfirewall firewall show rule name=all dir=in | Select-String -Context 5,5 "5000"`

Add firewall rule from administrator 

`netsh advfirewall firewall add rule name="Flask RAG API" dir=in action=allow protocol=TCP localport=5000`

To remove this rule later use command:
`netsh advfirewall firewall delete rule name="Flask RAG API"`

- Your actual host IP is `222.22.22.2` (works!)
- Container successfully connects to `http://222.22.22.2:5000/health` ✓

## Solution: Use Direct IP Address

### Step 1: Add Flask API to Open WebUI

1. Open Open WebUI at `http://localhost:3000`
2. Log in to your account
3. Click your **profile icon** (top right)
4. Go to **Settings** → **Connections**
5. Under **OpenAI API**, click **+ Add**
6. Configure:
   - **Name**: `RAG Agent` (or any name you prefer)
   - **API Base URL**: `http://222.22.22.2:5000/api`
   - **API Key**: `dummy-key` (any value works)
7. Click **Save** or **Verify Connection**

### Step 2: Test the Connection

In Open WebUI settings, after adding the connection, you should see:
- ✓ Connection successful
- Model: `rag-agent` should appear

### Step 3: Use RAG Agent

1. Go back to the chat interface
2. Click the **model selector** dropdown (top of chat)
3. Select **rag-agent** from the list
4. Ask a question: "What is RAG?"
5. The answer should come from your knowledge base!

## Why This Works

```
Container Network View:
┌─────────────────────────────────────────────┐
│ Open WebUI Container                        │
│                                             │
│ ❌ host.docker.internal → 111.111.1.1      │
│    (Podman's default, doesn't work)        │
│                                             │
│ ✓ 222.22.22.2 → Your actual host IP        │
│    (Direct connection, works!)             │
└─────────────────────────────────────────────┘
```

## Verification Commands

Test from container:
```powershell
# This works ✓
podman exec open-webui curl http://222.22.22.2:5000/health

# This fails ❌
podman exec open-webui curl http://host.docker.internal:5000/health
```

Test from host:
```powershell
# Both work on host
curl http://localhost:5000/health
curl http://222.22.22.2:5000/health
```

## Important Notes

### If Your IP Changes

Your host IP `222.22.22.2` might change if:
- You restart your computer
- You change networks
- Your network adapter resets

**To check your current IP:**
```powershell
ipconfig | Select-String "IPv4"
```

Look for the IP on your main network adapter (usually the one with `172.x.x.x` or `192.168.x.x`).

**If IP changes**, update the API Base URL in Open WebUI settings.

### Alternative: Use Static IP

To avoid IP changes, you can set a static IP for your network adapter:
1. Control Panel → Network and Sharing Center
2. Change adapter settings
3. Right-click your adapter → Properties
4. IPv4 → Properties
5. Set static IP: `222.22.22.2`

## Troubleshooting

### Issue: "Connection failed" in Open WebUI

**Check Flask is running:**
```powershell
netstat -ano | findstr ":5000"
```

Should show: `TCP    0.0.0.0:5000    LISTENING`

**Test from container:**
```powershell
podman exec open-webui curl http://222.22.22.2:5000/api/models
```

Should return:
```json
{"object":"list","data":[{"id":"rag-agent","object":"model","created":1700000000,"owned_by":"local","name":"RAG Agent"}]}
```

### Issue: Model doesn't appear in dropdown

1. Remove the API connection in Open WebUI settings
2. Re-add it with the correct URL
3. Refresh the page
4. Check the model selector again

### Issue: Answers are generic (not from your knowledge base)

This means Open WebUI is using Ollama directly instead of your RAG API. Make sure:
1. You selected **rag-agent** model (not gemma2:2b)
2. The model selector shows "RAG Agent" or "rag-agent"
3. Test with a specific question from your knowledge base

## Test Questions

Once connected, try these questions that should be answered from your knowledge base:

1. "What is RAG?"
2. "What are the benefits of using vector databases?"
3. "Explain the architecture of a RAG system"
4. "What is the difference between naive and advanced RAG?"
5. "How does embedding similarity search work?"

All answers should reference your 173 documents from 8 sources!
