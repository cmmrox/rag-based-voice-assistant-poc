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

- Docker and Docker Compose installed
- OpenAI API key with Realtime API access
- Node.js 18+ (for local frontend development)
- Python 3.11+ (for local backend development)
- Modern browser with WebRTC support (Chrome, Firefox, Edge)

## Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd voice-assistant-poc
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your OPENAI_API_KEY
   ```

3. **Start services with Docker Compose**
   ```bash
   # Run all services together
   docker-compose -f docker-compose.full.yml up
   
   # Or run in development mode with hot-reload
   docker-compose -f docker-compose.dev.yml up
   
   # See DOCKER_COMPOSE_GUIDE.md for more options
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - RAG Service: http://localhost:8001
   - ChromaDB: http://localhost:8000 (internal)

## Development Setup

### Frontend Development

```bash
cd frontend
npm install
npm run dev
```

### Backend Development

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### RAG Service Development

```bash
cd rag-service
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

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

## Documentation

- [Development Task Plan](./DEVELOPMENT_TASK_PLAN.md) - Detailed task breakdown
- [PRD](./PRD_POC.md) - Product Requirements Document

## Known Limitations

- Single-user sessions only
- In-memory session storage (lost on restart)
- Basic error handling
- No authentication/authorization
- Minimal UI styling

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]

