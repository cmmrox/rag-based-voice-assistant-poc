# RAG-Based Voice Assistant POC

A web-based voice assistant application with Retrieval-Augmented Generation (RAG) integration, demonstrating real-time bidirectional voice interactions using OpenAI's Realtime API, WebRTC, and ChromaDB.

## Overview

This Proof of Concept (POC) demonstrates:
- Real-time voice interaction using WebRTC
- Speech-to-text and text-to-speech via OpenAI Realtime API
- Knowledge-grounded responses using ChromaDB-based RAG
- Single-user voice sessions with sub-2-second latency

## Architecture

- **Frontend**: Next.js 14+ with TypeScript
- **Backend**: FastAPI (Python 3.11+)
- **RAG Service**: FastAPI service with ChromaDB
- **Infrastructure**: Docker Compose orchestration

## Prerequisites

- **Docker and Docker Compose** (for Docker setup) OR **Python 3.11+ and Node.js 18+** (for local development)
- **OpenAI API key** with Realtime API access
- **Modern browser** with WebRTC support (Chrome, Firefox, Edge)
- **Git** (optional, for cloning the repository)

## Quick Start

### Using Docker (Fastest)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd "RAG-based Voice Assistant POC"
   ```

2. **Set up environment variables**
   ```bash
   # Create .env file in root directory
   echo OPENAI_API_KEY=sk-your-api-key-here > .env
   ```

3. **Start all services**
   ```bash
   docker-compose -f docker-compose.full.yml up
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8002
   - RAG Service: http://localhost:8001

5. **Ingest documents (optional)**
   ```bash
   curl -X POST http://localhost:8001/api/documents/ingest -F "file=@path/to/document.pdf"
   ```

### Using Local Development

See [Development Setup](#development-setup) section below for detailed instructions.

## Development Setup

This section covers setting up and running the application in different environments. Choose the method that best fits your needs.

### Option 1: Docker Compose (Recommended for Quick Start)

Run all services together using Docker Compose:

```bash
# Run all services together
docker-compose -f docker-compose.full.yml up

# Or run in development mode with hot-reload
docker-compose -f docker-compose.dev.yml up

# See DOCKER_COMPOSE_GUIDE.md for more options
```

**Services will be available at:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8002
- RAG Service: http://localhost:8001
- ChromaDB: http://localhost:8000 (internal)

### Option 2: Local Development (Windows)

Set up and run services locally for development with hot-reload.

#### Prerequisites
- Python 3.11+ installed
- Node.js 18+ installed (for frontend)
- OpenAI API key

#### Step 1: Setup RAG Service

```bash
# Navigate to RAG service directory
cd rag-service

# Create virtual environment (Windows)
py -3.11 -m venv venv

# Activate virtual environment (Windows)
venv\Scripts\activate

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Run RAG service on port 8001
uvicorn app.main:app --reload --port 8001 --host 0.0.0.0
```

**RAG Service will be available at:** http://localhost:8001

#### Step 2: Test RAG Service (Optional)

In a new terminal, test the RAG service:

```bash
# Ingest a document
curl -X POST http://localhost:8001/api/documents/ingest -F "file=@ce-little-red-story-pcp-115014.pdf"

# Query the knowledge base
curl -X POST http://localhost:8001/api/rag/query -H "Content-Type: application/json" -d "{\"query\": \"What is the main topic?\"}"
```

#### Step 3: Setup Backend Service

```bash
# Navigate to backend directory (in a new terminal)
cd backend

# Create virtual environment (Windows)
py -3.11 -m venv venv

# Activate virtual environment (Windows)
venv\Scripts\activate

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Run backend service on port 8002
uvicorn app.main:app --reload --port 8002 --host 0.0.0.0
```

**Backend API will be available at:** http://localhost:8002

#### Step 4: Setup Frontend

```bash
# Navigate to frontend directory (in a new terminal)
cd frontend

# Install dependencies
npm install

# Run frontend development server
npm run dev
```

**Frontend will be available at:** http://localhost:3000

### Option 3: Local Development (Linux/Mac)

The setup is similar to Windows, but use different commands for virtual environment:

#### RAG Service Setup

```bash
cd rag-service
python3.11 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001 --host 0.0.0.0
```

#### Backend Setup

```bash
cd backend
python3.11 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8002 --host 0.0.0.0
```

#### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### Option 4: Mixed Setup (Docker + Local)

You can run some services in Docker and others locally:

**Example: Run ChromaDB in Docker, services locally**

```bash
# Terminal 1: Start ChromaDB in Docker
docker-compose -f docker-compose.chromadb.yml up

# Terminal 2: Run RAG service locally (connects to Docker ChromaDB)
cd rag-service
# ... setup and run as above

# Terminal 3: Run backend locally
cd backend
# ... setup and run as above

# Terminal 4: Run frontend locally
cd frontend
npm run dev
```

**Note:** When running services locally, ensure:
- RAG Service URL in backend config points to `http://localhost:8001`
- Backend URL in frontend config points to `http://localhost:8002`
- ChromaDB host in RAG service config points to `localhost` (if ChromaDB is in Docker)

### Testing the Setup

#### 1. Health Checks

```bash
# Check RAG service health
curl http://localhost:8001/health

# Check backend health
curl http://localhost:8002/health
```

#### 2. Ingest Documents

```bash
# Ingest a PDF document
curl -X POST http://localhost:8001/api/documents/ingest -F "file=@path/to/your/document.pdf"

# Ingest a text file
curl -X POST http://localhost:8001/api/documents/ingest -F "file=@path/to/your/document.txt"
```

#### 3. Test RAG Query

```bash
# Query the knowledge base
curl -X POST http://localhost:8001/api/rag/query \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"What is the main topic?\"}"
```

#### 4. Test Voice Assistant

1. Open http://localhost:3000 in your browser
2. Click the microphone button
3. Grant microphone permissions
4. Ask a question related to your ingested documents
5. The model will use function calling to search the knowledge base and respond

## Project Structure

```
voice-assistant-poc/
├── frontend/              # Next.js frontend application
├── backend/               # FastAPI backend service
├── rag-service/           # FastAPI RAG service
├── docker-compose.*.yml   # Docker Compose files (see DOCKER_COMPOSE_GUIDE.md)
├── .env.example          # Environment variables template
└── README.md             # This file
```

## Features

- ✅ Real-time voice interaction
- ✅ WebRTC-based audio streaming
- ✅ OpenAI Realtime API integration with **Function Calling**
- ✅ ChromaDB RAG pipeline
- ✅ Document ingestion (PDF, TXT, MD)
- ✅ Knowledge-grounded responses via intelligent function calling
- ✅ Basic web UI

### Function Calling for RAG

The application uses OpenAI Realtime API's native function calling feature to intelligently search the knowledge base. When users ask questions, the model decides when to call the `search_knowledge_base` function to retrieve relevant context, making responses more accurate and contextually aware.

## API Endpoints

### Backend
- `POST /api/realtime/session` - Create OpenAI Realtime session with function calling
- `WS /api/ws/events/{session_id}` - WebSocket for function call execution
- `GET /health` - Health check

### RAG Service
- `POST /api/documents/ingest` - Upload and ingest document
- `POST /api/rag/query` - Process query and retrieve context
- `GET /health` - Health check

## Environment Variables

Create a `.env` file in the root directory with:

```env
OPENAI_API_KEY=sk-your-api-key-here
BACKEND_PORT=8002
RAG_SERVICE_URL=http://localhost:8001
```

### For Local Development

**Backend** (uses root `.env`):
- `OPENAI_API_KEY` - OpenAI API key (required)
- `BACKEND_PORT` - Backend port (default: 8002)
- `RAG_SERVICE_URL` - RAG service URL (default: http://localhost:8001)

**RAG Service** (uses root `.env`):
- `OPENAI_API_KEY` - OpenAI API key (required)
- `CHROMADB_HOST` - ChromaDB host (default: localhost for local, chromadb for Docker)
- `CHROMADB_PORT` - ChromaDB port (default: 8000)

**Frontend** (uses root `.env`):
- `NEXT_PUBLIC_BACKEND_URL` - Backend URL (default: http://localhost:8002)
- `NEXT_PUBLIC_WS_URL` - WebSocket URL (default: ws://localhost:8002)

## Service Ports

| Service | Port | Description |
|---------|------|-------------|
| Frontend | 3000 | Next.js web application |
| Backend | 8002 | FastAPI backend service |
| RAG Service | 8001 | RAG query and document ingestion service |
| ChromaDB | 8000 | Vector database (internal) |

## Documentation

- [Setup Guide](./SETUP_GUIDE.md) - Detailed setup instructions
- [API Documentation](./API_DOCUMENTATION.md) - API endpoints and function calling
- [Docker Compose Guide](./DOCKER_COMPOSE_GUIDE.md) - Docker setup options
- [Development Task Plan](./DEVELOPMENT_TASK_PLAN.md) - Detailed task breakdown
- [PRD](./PRD_POC.md) - Product Requirements Document
- [Demo Script](./DEMO_SCRIPT.md) - Demo walkthrough

## How It Works

### Function Calling Flow

1. **User speaks** → Audio captured via microphone
2. **OpenAI Realtime API** → Transcribes speech to text
3. **Model analyzes** → Decides if knowledge base search is needed
4. **Function call** → Model calls `search_knowledge_base` function (if needed)
5. **RAG query** → Backend executes function, queries ChromaDB via RAG service
6. **Function result** → Context returned to model
7. **Response generation** → Model generates answer using retrieved context
8. **Audio response** → Response converted to speech and played to user

### Key Features

- **Intelligent Function Calling**: Model decides when to search knowledge base
- **Real-time Voice**: Sub-2-second latency for natural conversations
- **RAG Integration**: Knowledge-grounded responses from your documents
- **WebRTC Audio**: Direct peer-to-peer audio streaming
- **Function Execution**: Backend handles function calls via WebSocket

## Troubleshooting

### Port Conflicts

If ports are already in use:

```bash
# Windows - Check what's using the port
netstat -ano | findstr :8002

# Linux/Mac - Check what's using the port
lsof -i :8002
```

Change ports in `.env` file or stop conflicting services.

### Service Connection Issues

**Backend can't connect to RAG Service:**
- Ensure RAG service is running on port 8001
- Check `RAG_SERVICE_URL` in backend `.env` is correct
- Verify firewall isn't blocking connections

**Frontend can't connect to Backend:**
- Ensure backend is running on port 8002
- Check `NEXT_PUBLIC_BACKEND_URL` in frontend `.env` is correct
- Verify CORS settings in backend allow frontend origin

**RAG Service can't connect to ChromaDB:**
- Ensure ChromaDB is running (Docker or local)
- Check `CHROMADB_HOST` and `CHROMADB_PORT` in RAG service config
- Verify ChromaDB is accessible from RAG service

### Common Issues

**"Module not found" errors:**
```bash
# Ensure virtual environment is activated
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

**OpenAI API errors:**
- Verify API key is correct in `.env`
- Check API key has Realtime API access
- Verify API quota/credits available

**Function calling not working:**
- Ensure session configuration includes `tools` array
- Check function name matches: `search_knowledge_base`
- Verify WebSocket connection is established
- Check browser console and backend logs for errors

## Known Limitations

- Single-user sessions only
- In-memory session storage (lost on restart)
- Basic error handling
- No authentication/authorization
- Minimal UI styling
- Function calling requires OpenAI Realtime API access

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]

