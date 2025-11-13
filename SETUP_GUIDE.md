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
cd voice-assistant
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
# Using curl
curl -X POST http://localhost:8001/api/documents/ingest \
  -F "file=@path/to/your/document.pdf"

# Or using Python
import requests

with open('document.pdf', 'rb') as f:
    response = requests.post(
        'http://localhost:8001/api/documents/ingest',
        files={'file': f}
    )
    print(response.json())
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

```bash
cd backend
python -m venv venv

# On Windows
venv\Scripts\activate

# On Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Backend will run on http://localhost:8000

### RAG Service Development

```bash
cd rag-service
python -m venv venv

# On Windows
venv\Scripts\activate

# On Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

RAG service will run on http://localhost:8001

## Troubleshooting

### Port Already in Use

If you get port conflicts:

1. Check what's using the port:
   ```bash
   # Windows
   netstat -ano | findstr :8000
   
   # Linux/Mac
   lsof -i :8000
   ```

2. Stop the conflicting service or change ports in `docker-compose.yml`

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

- `OPENAI_API_KEY` - OpenAI API key
- `BACKEND_PORT` - Backend port (default: 8000)
- `RAG_SERVICE_URL` - RAG service URL (default: http://rag-service:8000)

### RAG Service (uses root `.env`)

- `OPENAI_API_KEY` - OpenAI API key
- `CHROMADB_HOST` - ChromaDB host (default: chromadb)
- `CHROMADB_PORT` - ChromaDB port (default: 8000)

### Frontend (uses root `.env`)

- `NEXT_PUBLIC_BACKEND_URL` - Backend URL (default: http://localhost:8002)
- `NEXT_PUBLIC_WS_URL` - WebSocket URL (default: ws://localhost:8002)

## Common Issues

### Issue: "Module not found" errors

**Solution:** Ensure all dependencies are installed:
```bash
# Frontend
cd frontend && npm install

# Backend/RAG Service
pip install -r requirements.txt
```

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

## Next Steps

1. Ingest some documents into the knowledge base
2. Start a voice session
3. Ask questions related to your documents
4. Test multi-turn conversations

## Getting Help

- Check the logs: `docker-compose logs`
- Review the [API Documentation](./API_DOCUMENTATION.md)
- Check the [PRD](./PRD_POC.md) for architecture details

