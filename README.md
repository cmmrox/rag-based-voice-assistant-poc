# RAG-Based Voice Assistant - Proof of Concept

A real-time voice assistant powered by OpenAI's Realtime API with RAG (Retrieval-Augmented Generation) capabilities for knowledge-based conversations.

## Overview

This POC demonstrates a production-ready voice assistant that combines:
- **Real-time voice conversations** using OpenAI's GPT-4 Realtime API
- **RAG knowledge retrieval** for answering questions from custom documents
- **Function calling integration** to dynamically access knowledge base during conversations
- **WebRTC** for low-latency audio streaming
- **Vector search** using ChromaDB for efficient document retrieval

## System Architecture

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│             │         │              │         │             │
│  Frontend   │◄───────►│   Backend    │◄───────►│ RAG Service │
│  (Next.js)  │  HTTP   │   (FastAPI)  │  HTTP   │  (FastAPI)  │
│             │  REST   │              │         │             │
└──────┬──────┘         └───────┬──────┘         └──────┬──────┘
       │                        │                       │
       │ WebRTC                 │ HTTPS                 │
       │ Data Channel           │ SDP Forward           │
       │                        │                       │
       └────────────────────────┼───────────────────────┘
                                ▼
                    ┌────────────────────┐
                    │   OpenAI           │
                    │   Realtime API     │
                    │   (WebRTC + Audio) │
                    └────────────────────┘

                                ┌────────────────────┐
                                │   ChromaDB         │
                                │   Vector Database  │
                                └────────────────────┘
```

## Features

### Core Capabilities
- ✅ **Real-time voice conversations** - Low-latency audio streaming with OpenAI
- ✅ **RAG knowledge retrieval** - Query custom document knowledge base
- ✅ **Function calling** - Automatic knowledge base access during conversation
- ✅ **Multi-format document support** - PDF, TXT, Markdown
- ✅ **Real-time transcription** - See conversation as it happens
- ✅ **Session management** - Stateless backend with client-side session tracking

### Technical Features
- ✅ **WebRTC integration** - Direct browser-to-OpenAI audio connection
- ✅ **Vector embeddings** - OpenAI text-embedding-3-small for semantic search
- ✅ **Chunking strategy** - Intelligent document splitting (500 tokens, 100 overlap)
- ✅ **Error handling** - Comprehensive error recovery across all services
- ✅ **Type safety** - Full TypeScript frontend, type hints in Python backend
- ✅ **Code quality** - Centralized constants, utilities, standardized patterns

## Technology Stack

### Frontend
- **Framework**: Next.js 14.0.0 (App Router)
- **Language**: TypeScript 5.0.0
- **UI**: React 18.2.0, Tailwind CSS 3.3.0
- **Real-time**: WebRTC (native browser API), REST API

### Backend
- **Framework**: FastAPI 0.104.1
- **Language**: Python 3.11+
- **HTTP Client**: httpx 0.25.0
- **API**: REST API endpoints

### RAG Service
- **Framework**: FastAPI 0.104.1
- **Vector DB**: ChromaDB 1.3.0+
- **Embeddings**: OpenAI text-embedding-3-small
- **Document Parser**: PyPDF2 3.0.1

### External Services
- **OpenAI Realtime API**: gpt-4o-realtime-preview-2024-10-01
- **OpenAI Embeddings API**: text-embedding-3-small

## Quick Start

### Prerequisites
- **Node.js**: 18.x or higher
- **Python**: 3.11 or higher
- **OpenAI API Key**: With access to Realtime API
- **ChromaDB**: Running instance (or use in-memory mode)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd rag-based-voice-assistant-poc
```

2. **Set up Frontend**
```bash
cd frontend
npm install
cp .env.example .env.local
# Edit .env.local and add: NEXT_PUBLIC_BACKEND_URL=http://localhost:8002
npm run dev
```

3. **Set up Backend**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
uvicorn app.main:app --reload --port 8002 --host 0.0.0.0
```

4. **Set up RAG Service**
```bash
cd rag-service
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY and ChromaDB settings
uvicorn app.main:app --reload --port 8001 --host 0.0.0.0
```

5. **Access the application**
- Open http://localhost:3000 in your browser
- Click "Start Voice" to begin conversation
- Upload documents via RAG service API (see [RAG Service API Documentation](rag-service/API_DOCUMENTATION.md))

## Environment Variables

### Frontend (.env.local)
```env
NEXT_PUBLIC_BACKEND_URL=http://localhost:8002
```

### Backend (.env)
```env
OPENAI_API_KEY=sk-your-key-here
RAG_SERVICE_URL=http://localhost:8001
FRONTEND_URL=http://localhost:3000
BACKEND_PORT=8002
```

### RAG Service (.env)
```env
OPENAI_API_KEY=sk-your-key-here
CHROMADB_HOST=localhost
CHROMADB_PORT=8000
RAG_PORT=8001
```

## Project Structure

```
rag-based-voice-assistant-poc/
├── frontend/                 # Next.js application
│   ├── app/                 # Next.js App Router pages
│   ├── components/          # React components
│   ├── hooks/               # Custom React hooks (useVoiceSession)
│   ├── constants/           # Frontend constants
│   ├── types/               # TypeScript type definitions
│   └── utils/               # Utility functions
│
├── backend/                 # FastAPI backend service
│   ├── app/
│   │   ├── routes/         # API endpoints
│   │   ├── services/       # Business logic services
│   │   ├── constants/      # Backend constants
│   │   └── utils/          # Utility functions
│   └── requirements.txt
│
├── rag-service/            # RAG knowledge base service
│   ├── app/
│   │   ├── routes/        # API endpoints
│   │   ├── services/      # Document processing, embeddings, ChromaDB
│   │   ├── models/        # Pydantic schemas
│   │   ├── constants/     # RAG service constants
│   │   └── utils/         # Utility functions
│   └── requirements.txt
│
└── docs/                  # Additional documentation
```

## Documentation

- **[Setup Guide](SETUP_GUIDE.md)** - Detailed setup instructions
- **[API Documentation](API_DOCUMENTATION.md)** - Complete API reference (Backend & RAG Service)
- **[PRD](PRD.md)** - Product requirements document
- **[PRD POC](PRD_POC.md)** - POC-specific requirements
- **[Development Task Plan](DEVELOPMENT_TASK_PLAN.md)** - Original planning document (archived)

## Key Workflows

### 1. Voice Conversation Flow
1. User clicks "Start Voice" button
2. Frontend creates WebRTC offer (SDP)
3. Backend forwards SDP to OpenAI Realtime API
4. OpenAI returns SDP answer
5. WebRTC peer connection established
6. User speaks → OpenAI transcribes and responds
7. Audio streams back to user in real-time

### 2. RAG Function Calling Flow
1. User asks question requiring knowledge base
2. OpenAI model decides to call `rag_knowledge` function
3. Function call sent via WebRTC data channel to frontend
4. Frontend sends REST API request to backend (`POST /api/rag/function-call`)
5. Backend receives function call, forwards to RAG service via HTTP
6. RAG service:
   - Generates embedding for query
   - Searches ChromaDB for similar documents
   - Returns relevant context
7. Backend sends context back to frontend as REST API response
8. Frontend sends function result to OpenAI via data channel
9. Model formulates answer using retrieved knowledge
10. Answer spoken to user

## API Endpoints

### Backend API
- **POST /api/realtime/session** - Create OpenAI Realtime session (SDP exchange)
- **POST /api/rag/function-call** - Execute RAG function calls and return results
- **GET /health** - Health check endpoint

### RAG Service API
- **POST /api/rag/query** - Query knowledge base
- **POST /api/documents/ingest** - Upload and ingest documents
- **GET /health** - Health check endpoint

## Service Ports

| Service | Port | Description |
|---------|------|-------------|
| Frontend | 3000 | Next.js web application |
| Backend | 8002 | FastAPI backend service |
| RAG Service | 8001 | RAG query and document ingestion service |
| ChromaDB | 8000 | Vector database (internal) |

## Development

### Running Tests
```bash
# Frontend tests
cd frontend
npm test

# Backend tests
cd backend
pytest

# RAG Service tests
cd rag-service
pytest
```

### Code Quality
```bash
# Frontend linting
cd frontend
npm run lint

# Backend linting
cd backend
flake8 app/
black app/
isort app/

# RAG Service linting
cd rag-service
flake8 app/
black app/
isort app/
```

## Troubleshooting

### Frontend won't connect to backend
- Check `NEXT_PUBLIC_BACKEND_URL` in `.env.local`
- Ensure backend is running on correct port (8002)
- Check browser console for CORS errors
- Verify CORS settings in backend allow frontend origin

### Backend can't connect to OpenAI
- Verify `OPENAI_API_KEY` is set correctly in `.env`
- Check API key has Realtime API access
- Review backend logs for detailed error messages
- Ensure network allows HTTPS connections to api.openai.com

### RAG service not returning results
- Ensure documents are uploaded first via `/api/documents/ingest`
- Check ChromaDB is running and accessible
- Verify `OPENAI_API_KEY` for embeddings is valid
- Check RAG service logs for errors

### WebRTC connection fails
- Check browser supports WebRTC (Chrome, Firefox, Edge recommended)
- Ensure microphone permissions are granted
- Check network firewall settings
- Review browser console for WebRTC errors

### Function calling not working
- Verify WebRTC connection to OpenAI is established (check browser console for data channel)
- Verify backend REST API is accessible: `curl -X POST http://localhost:8002/api/rag/function-call`
- Check backend logs for function call reception
- Ensure RAG service is accessible from backend (test: `curl http://localhost:8001/health`)
- Verify documents are ingested in ChromaDB via `/api/documents/ingest`
- Check that function `rag_knowledge` is registered in session tools configuration
- Check browser network tab for REST API request/response status

## Recent Improvements

### Frontend Refactoring
- ✅ Created constants, types, and utils structure
- ✅ Extracted magic values to configuration files
- ✅ Implemented config object pattern for components
- ✅ Added comprehensive TypeScript type definitions
- ✅ Improved code organization and modularity
- ✅ Added JSDoc documentation throughout

### Backend Refactoring
- ✅ Removed 350+ lines of unused code (openai_gateway, session_manager)
- ✅ Created constants and utils structure
- ✅ Centralized error handling
- ✅ Added input validation utilities
- ✅ Simplified health check endpoint
- ✅ Improved logging configuration

### RAG Service Refactoring
- ✅ Created constants for all magic numbers
- ✅ Added comprehensive error handling utilities
- ✅ Centralized logging configuration
- ✅ Improved code organization
- ✅ Better type hints throughout

## Known Limitations

- Single-user sessions only (concurrent users supported but not session persistence)
- Client-side session management (sessions not stored on server)
- Basic authentication (API key only, no user auth)
- In-memory ChromaDB fallback on connection failure
- Function calling requires OpenAI Realtime API access
- Microphone permission required for voice interaction

## Contributing

This is a proof-of-concept project. Contribution guidelines coming soon.

## License

This is a proof-of-concept project for demonstration purposes.

## Acknowledgments

- Built with [OpenAI Realtime API](https://platform.openai.com/docs/guides/realtime)
- Uses [ChromaDB](https://www.trychroma.com/) for vector storage
- Inspired by [OpenAI Realtime Console](https://github.com/openai/openai-realtime-console)

## Support

For issues and questions:
1. Check [Troubleshooting](#troubleshooting) section
2. Review [Setup Guide](SETUP_GUIDE.md)
3. Check [API Documentation](API_DOCUMENTATION.md) for endpoints and flows
4. Review [System Architecture](#system-architecture) diagram above
5. Create an issue with detailed information

---

**Last Updated**: January 2025
**Version**: 1.0.0 (POC)
**Status**: ✅ Working Implementation
**Code Quality**: ✅ Refactored and Production-Ready
