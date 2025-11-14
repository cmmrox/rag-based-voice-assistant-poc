# Setup Guide

This guide will help you set up and run the RAG-Based Voice Assistant POC.

## Prerequisites

Before starting, ensure you have:

1. **Docker and Docker Compose**
   - Docker Desktop: https://www.docker.com/products/docker-desktop
   - Docker Compose is included with Docker Desktop

2. **OpenAI API Key**
   - Sign up at https://platform.openai.com/
   - Create an API key with Realtime API access
   - Note: Realtime API may require special access

3. **Modern Browser**
   - Chrome, Firefox, or Edge (latest versions)
   - WebRTC support required

4. **Git** (optional, for cloning)

## Step-by-Step Setup

### 1. Clone or Download the Repository

```bash
git clone <repository-url>
cd "RAG-based Voice Assistant POC"
```

### 2. Create Environment File

Create a `.env` file in the root directory:

```bash
# Copy the example (if available)
cp .env.example .env
```

Or create `.env` manually with:

```env
OPENAI_API_KEY=sk-your-api-key-here
```

### 3. Start Services with Docker Compose

```bash
# Run all services together
docker-compose -f docker-compose.full.yml up

# Or run in development mode with hot-reload
docker-compose -f docker-compose.dev.yml up

# See DOCKER_COMPOSE_GUIDE.md for more options
```

This will start:
- ChromaDB (port 8000)
- Backend service (port 8002)
- RAG service (port 8001)
- Frontend (port 3000)

### 4. Access the Application

Open your browser and navigate to:
- **Frontend**: http://localhost:3000

### 5. Ingest Sample Documents (Optional)

Before using the voice assistant, you may want to ingest some documents:

```bash
# Using curl - Ingest a document
curl -X POST http://localhost:8001/api/documents/ingest -F "file=@ce-little-red-story-pcp-115014.pdf"

# Query the knowledge base to test
curl -X POST http://localhost:8001/api/rag/query -H "Content-Type: application/json" -d "{\"query\": \"What is the main topic?\"}"
```

Or using Python:

```python
import requests

# Ingest a document
with open('document.pdf', 'rb') as f:
    response = requests.post(
        'http://localhost:8001/api/documents/ingest',
        files={'file': f}
    )
    print(response.json())

# Query the knowledge base
query_response = requests.post(
    'http://localhost:8001/api/rag/query',
    json={'query': 'What is the main topic?'}
)
print(query_response.json())
```

## Development Setup

### Frontend Development

```bash
cd frontend
npm install
npm run dev
```

Frontend will run on http://localhost:3000

### Backend Development

#### Windows Setup

```bash
cd backend

# Create virtual environment
py -3.11 -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Run backend service on port 8002
uvicorn app.main:app --reload --port 8002 --host 0.0.0.0
```

#### Linux/Mac Setup

```bash
cd backend

# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Run backend service on port 8002
uvicorn app.main:app --reload --port 8002 --host 0.0.0.0
```

Backend will run on http://localhost:8002

### RAG Service Development

#### Windows Setup

```bash
cd rag-service

# Create virtual environment
py -3.11 -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Run RAG service on port 8001
uvicorn app.main:app --reload --port 8001 --host 0.0.0.0
```

#### Linux/Mac Setup

```bash
cd rag-service

# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Run RAG service on port 8001
uvicorn app.main:app --reload --port 8001 --host 0.0.0.0
```

RAG service will run on http://localhost:8001

## Troubleshooting

### Port Already in Use

If you get port conflicts:

1. Check what's using the port:
   ```bash
   # Windows - Check backend port (8002)
   netstat -ano | findstr :8002
   
   # Windows - Check RAG service port (8001)
   netstat -ano | findstr :8001
   
   # Linux/Mac - Check backend port (8002)
   lsof -i :8002
   
   # Linux/Mac - Check RAG service port (8001)
   lsof -i :8001
   ```

2. Stop the conflicting service or change ports in `.env` file or `docker-compose.yml`

### ChromaDB Connection Issues

If ChromaDB fails to start:

1. Check Docker logs:
   ```bash
   docker-compose logs chromadb
   ```

2. Ensure port 8000 is available for ChromaDB

3. Try removing the volume and restarting:
   ```bash
   docker-compose down -v
   docker-compose up
   ```

### OpenAI API Errors

If you get OpenAI API errors:

1. Verify your API key is correct in `.env`
2. Check API key has Realtime API access
3. Check API quota/limits
4. Review backend logs:
   ```bash
   docker-compose logs backend
   ```

### WebRTC Connection Issues

If WebRTC fails to connect:

1. Check browser console for errors
2. Ensure microphone permissions are granted
3. Try a different browser
4. Check firewall settings
5. Review backend logs for WebSocket errors

### Frontend Build Issues

If frontend fails to build:

```bash
cd frontend
rm -rf node_modules .next
npm install
npm run build
```

## Environment Variables

### Root `.env`

```env
OPENAI_API_KEY=sk-...
```

### Backend (uses root `.env`)

- `OPENAI_API_KEY` - OpenAI API key (required)
- `BACKEND_PORT` - Backend port (default: 8002 for local, 8000 inside Docker)
- `RAG_SERVICE_URL` - RAG service URL (default: http://localhost:8001 for local, http://rag-service:8000 for Docker)

### RAG Service (uses root `.env`)

- `OPENAI_API_KEY` - OpenAI API key (required)
- `CHROMADB_HOST` - ChromaDB host (default: `localhost` for local development, `chromadb` for Docker)
- `CHROMADB_PORT` - ChromaDB port (default: 8000)

### Frontend (uses root `.env`)

- `NEXT_PUBLIC_BACKEND_URL` - Backend URL (default: http://localhost:8002)
- `NEXT_PUBLIC_WS_URL` - WebSocket URL (default: ws://localhost:8002)

## Common Issues

### Issue: "Module not found" errors

**Solution:** Ensure virtual environment is activated and dependencies are installed:
```bash
# Windows - Activate virtual environment
venv\Scripts\activate

# Linux/Mac - Activate virtual environment
source venv/bin/activate

# Frontend
cd frontend && npm install

# Backend/RAG Service
pip install -r requirements.txt
```

### Issue: Port conflicts

**Solution:** 
- Backend should run on port 8002 (not 8000, which is used by ChromaDB)
- RAG service runs on port 8001
- Frontend runs on port 3000
- ChromaDB runs on port 8000

If ports are in use, check with:
```bash
# Windows
netstat -ano | findstr :8002

# Linux/Mac
lsof -i :8002
```

### Issue: Function calling not working

**Solution:**
- Ensure session configuration includes `tools` array with `search_knowledge_base` function
- Check WebSocket connection is established (check browser console)
- Verify RAG service is running and accessible
- Check backend logs for function call execution errors
- Ensure documents are ingested before querying

### Issue: Docker build fails

**Solution:** 
1. Ensure Docker is running
2. Check Docker has enough resources allocated
3. Try rebuilding:
   ```bash
   docker-compose -f docker-compose.full.yml build --no-cache
   ```

### Issue: Services can't communicate

**Solution:**
1. Ensure all services are on the same Docker network
2. Check service names match in the compose files
3. Use service names (not localhost) for inter-service communication
4. If using separate compose files, ensure network is created: `docker network create voice-assistant-network`

## Testing the Setup

### 1. Health Checks

Verify all services are running:

```bash
# Check RAG service health
curl http://localhost:8001/health

# Check backend health
curl http://localhost:8002/health
```

### 2. Test Document Ingestion

```bash
# Ingest a PDF document
curl -X POST http://localhost:8001/api/documents/ingest -F "file=@path/to/your/document.pdf"

# Ingest a text file
curl -X POST http://localhost:8001/api/documents/ingest -F "file=@path/to/your/document.txt"
```

### 3. Test RAG Query

```bash
# Query the knowledge base
curl -X POST http://localhost:8001/api/rag/query \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"What is the main topic?\"}"
```

### 4. Test Voice Assistant

1. Open http://localhost:3000 in your browser
2. Click the microphone button
3. Grant microphone permissions when prompted
4. Ask a question related to your ingested documents
5. The model will use function calling to search the knowledge base and respond

## How Function Calling Works

The application uses OpenAI Realtime API's native function calling feature:

1. **User speaks** → Audio captured via microphone
2. **OpenAI Realtime API** → Transcribes speech to text
3. **Model analyzes** → Decides if knowledge base search is needed
4. **Function call** → Model calls `search_knowledge_base` function (if needed)
5. **RAG query** → Backend executes function, queries ChromaDB via RAG service
6. **Function result** → Context returned to model
7. **Response generation** → Model generates answer using retrieved context
8. **Audio response** → Response converted to speech and played to user

## Next Steps

1. Ingest some documents into the knowledge base
2. Start a voice session
3. Ask questions related to your documents
4. Test multi-turn conversations
5. Experiment with different types of questions to see when function calling is triggered

## Getting Help

- Check the logs: `docker-compose logs`
- Review the [API Documentation](./API_DOCUMENTATION.md)
- Check the [PRD](./PRD_POC.md) for architecture details

