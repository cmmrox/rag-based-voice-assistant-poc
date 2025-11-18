# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a real-time voice assistant powered by OpenAI's Realtime API with RAG (Retrieval-Augmented Generation) and note-taking capabilities. The system consists of these services:

1. **Frontend** (Next.js 14 + TypeScript) - User interface with WebRTC voice communication
2. **Backend** (FastAPI + Python + PostgreSQL) - Proxies requests to OpenAI, handles function calling, and manages notes
3. **RAG Service** (FastAPI + Python + ChromaDB) - Document ingestion and semantic search
4. **PostgreSQL** - Persistent storage for user notes with full-text search

## Common Commands

### Frontend Development
```bash
cd frontend
npm install                 # Install dependencies
npm run dev                 # Start development server (http://localhost:3000)
npm run build              # Production build
npm run lint               # Run ESLint
npm start                  # Start production server
```

### Backend Service
```bash
cd backend
python -m venv venv        # Create virtual environment
venv\Scripts\activate      # Windows activation
source venv/bin/activate   # Unix/Mac activation
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8002 --host 0.0.0.0
```

### RAG Service
```bash
cd rag-service
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Unix/Mac
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001 --host 0.0.0.0
```

### PostgreSQL Database
```bash
# Start PostgreSQL (Docker)
docker-compose -f docker-compose.postgres.yml up -d

# Stop PostgreSQL
docker-compose -f docker-compose.postgres.yml down

# View logs
docker-compose -f docker-compose.postgres.yml logs -f

# Run database migrations (from backend directory)
cd backend
alembic upgrade head

# Create new migration after model changes
alembic revision --autogenerate -m "Description of changes"
```

### Testing
```bash
# Frontend tests
cd frontend && npm test

# Backend tests (when implemented)
cd backend && pytest

# RAG Service tests (when implemented)
cd rag-service && pytest
```

## Architecture

### Communication Flow

The system uses a two-channel architecture:

1. **WebRTC Direct Connection** (Frontend ↔ OpenAI)
   - SDP exchange via backend proxy (`POST /api/realtime/session`)
   - Audio streams directly between browser and OpenAI
   - Data channel for OpenAI events (transcriptions, function calls, errors)

2. **HTTP REST APIs** (Frontend ↔ Backend ↔ Services)
   - RAG function calls: `POST /api/rag/function-call` (Frontend → Backend)
   - RAG queries: `POST /api/rag/query` (Backend → RAG Service)
   - Document ingestion: `POST /api/documents/ingest` (Backend → RAG Service)
   - Notes function calls: `POST /api/notes/function-call` (Frontend → Backend → PostgreSQL)

### Function Calling Flow

**Critical**: Both RAG and Notes integration use OpenAI's function calling, NOT transcription-based parsing.

#### RAG Knowledge Function Flow

1. Frontend registers `rag_knowledge` function with OpenAI via data channel
2. User asks question requiring knowledge base
3. OpenAI decides to call `rag_knowledge` function
4. Function call sent via WebRTC data channel → Frontend
5. Frontend sends REST API request to Backend (`POST /api/rag/function-call`)
6. Backend queries RAG service via HTTP (`POST /api/rag/query`)
7. RAG service generates embeddings and searches ChromaDB
8. Results flow back: RAG → Backend → Frontend (as REST response)
9. Frontend sends function output to OpenAI via data channel
10. OpenAI formulates final answer and speaks to user

#### Notes Management Function Flow

1. Frontend registers `manage_notes` function with OpenAI via data channel
2. User requests note operation (create, list, search, update, delete)
3. OpenAI decides to call `manage_notes` function with appropriate action
4. Function call sent via WebRTC data channel → Frontend
5. Frontend sends REST API request to Backend (`POST /api/notes/function-call`)
6. Backend processes request and performs database operation (PostgreSQL)
7. Results flow back: PostgreSQL → Backend → Frontend (as REST response)
8. Frontend sends function output to OpenAI via data channel
9. OpenAI formulates response with note information and speaks to user

**Supported Note Actions**:
- **create**: Save new note with title and content
- **list**: Retrieve all notes or specific note by ID
- **search**: Find notes using PostgreSQL full-text search
- **update**: Modify existing note's title or content
- **delete**: Remove note by ID

### Session Management

**Important**: Sessions are client-side only. No server-side session storage.

- Backend is completely stateless
- `session_id` is generated client-side (`crypto.randomUUID()`)
- Used only for client-side tracking and logging

### WebRTC Data Channel Events

The frontend (`useVoiceSession.ts`) handles these OpenAI event types:

- `session.created` - Triggers function registration
- `response.function_call_arguments.done` - **PRIMARY** function call detection (critical!)
- `conversation.item.input_audio_transcription.completed` - User speech transcription
- `response.audio_transcript.delta` - Assistant speech transcription
- `response.done` - Response complete
- `error` - Error events

**CRITICAL**: Function call detection must happen at `response.function_call_arguments.done` to avoid "Tool call ID not found" errors. This event fires BEFORE `response.done`, ensuring the function output is sent while the item_id is still valid.

## Key Files and Responsibilities

### Frontend (`frontend/`)

**Core Hook**: `hooks/useVoiceSession.ts`
- Complete WebRTC lifecycle management
- Data channel event handling
- Function call detection (multi-strategy with deduplication)
- REST API communication with backend for RAG queries and notes operations
- State management for session status

**Important Patterns**:
- All OpenAI events sent via data channel MUST include `event_id: crypto.randomUUID()`
- Function call detection uses multiple fallback strategies (6 different event types checked)
- Deduplication prevents processing same `call_id` multiple times
- New response creation after function output (with 100ms delay)
- Supports multiple functions (`rag_knowledge`, `manage_notes`) with dynamic routing

**Utils Structure**:
- `utils/functionCalls.ts` - Function calling logic
- `utils/webrtc.ts` - WebRTC connection management
- `utils/ragClient.ts` - REST API client for RAG function calls
- `utils/notesClient.ts` - REST API client for notes function calls

**Constants**:
- `constants/api.ts` - Backend URL, OpenAI model
- `constants/tools.ts` - Function definitions (rag_knowledge, manage_notes)
- `constants/timing.ts` - Timeouts and delays

### Backend (`backend/app/`)

**Main Entry**: `main.py`
- CORS configuration for frontend
- Health check endpoint (checks RAG service AND PostgreSQL connectivity)
- Registers all routers (realtime, RAG, notes)

**Routes**:
- `routes/realtime.py` - SDP forwarding to OpenAI (`/api/realtime/session`)
  - Validates SDP format
  - Adds model and voice query parameters
  - Returns session config in `X-Session-Config` header
- `routes/rag_function.py` - REST API handler for RAG function calls (`/api/rag/function-call`)
  - Receives function call requests from frontend
  - Queries RAG service and returns results
  - Handles errors and formats responses
- `routes/notes_function.py` - REST API handler for notes function calls (`/api/notes/function-call`)
  - Receives note operation requests from frontend
  - Routes to appropriate CRUD operation based on action
  - Returns structured note data or error messages

**Services**:
- `services/rag_client.py` - HTTP client for RAG service
- `services/database.py` - Async SQLAlchemy engine and session management
- `services/notes_db.py` - CRUD operations for notes (create, get, list, update, delete, search)

**Models**:
- `models/database.py` - SQLAlchemy models (Note table with full-text search)
- `models/notes_schemas.py` - Pydantic schemas for request/response validation

**Constants & Utils** (centralized pattern):
- `constants/openai.py` - OpenAI API URLs and models
- `constants/timeouts.py` - HTTP timeouts
- `constants/notes.py` - Note limits (max title: 255, max content: 10000, search results: 20)
- `utils/errors.py` - Error handling
- `utils/validators.py` - Input validation

### RAG Service (`rag-service/app/`)

**Main Entry**: `main.py`
- ChromaDB initialization with fallback to in-memory mode
- Health check (works even if ChromaDB unavailable)

**Routes**:
- `routes/query.py` - Query endpoint (`POST /api/rag/query`)
  - Generates query embedding
  - Searches ChromaDB (5 results default)
  - Formats context with source attribution
- `routes/documents.py` - Document ingestion (`POST /api/documents/ingest`)

**Services**:
- `services/chromadb_service.py` - ChromaDB client (async, with graceful fallback)
- `services/embedding.py` - OpenAI embeddings (`text-embedding-3-small`)
- `services/document_parser.py` - Multi-format parser (PDF, TXT, MD, DOCX)

**Constants** (all magic numbers extracted):
- `constants/chunking.py` - Chunk size (500 tokens), overlap (100 tokens)
- `constants/embedding.py` - Model name, dimensions
- `constants/chromadb.py` - Collection name, distance metric

## Environment Configuration

### Frontend `.env.local`
```env
NEXT_PUBLIC_BACKEND_URL=http://localhost:8002
```

### Backend `.env`
```env
OPENAI_API_KEY=sk-...
RAG_SERVICE_URL=http://localhost:8001
FRONTEND_URL=http://localhost:3000
BACKEND_PORT=8002
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/notes_db
# For Docker: DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/notes_db
```

### RAG Service `.env`
```env
OPENAI_API_KEY=sk-...
CHROMADB_HOST=localhost
CHROMADB_PORT=8000
RAG_PORT=8001
```

## Code Quality Patterns

### Recent Refactoring (Important Context)
- **Backend**: Removed 350+ lines of unused code (old openai_gateway, session_manager)
- **All services**: Extracted magic numbers to constants modules
- **All services**: Centralized error handling and logging
- **Frontend**: Config object pattern for components, comprehensive TypeScript types

### When Making Changes

1. **Constants First**: Never use magic numbers. Add to appropriate constants file.
2. **Error Handling**: Use centralized error utilities (`utils/errors.py`)
3. **Type Safety**: Full TypeScript in frontend, type hints in Python
4. **Logging**: Use structured logging with clear prefixes (`[RAG]`, `[REST]`, etc.)
5. **Validation**: Use validation utilities before processing data

### Testing Patterns (When Adding Tests)

- Frontend: Jest + React Testing Library
- Backend/RAG: pytest with async support
- Focus on integration tests for function calling flow

## Critical Implementation Notes

### Function Calling (Most Important)

**DO**:
- Always include `event_id` when sending events to OpenAI
- Use `response.function_call_arguments.done` as primary detection point
- Extract `call_id` (not `item_id`) for function outputs
- Create new response after sending function output
- Implement deduplication to prevent duplicate processing

**DON'T**:
- Don't rely only on `response.done` for function call detection (too late!)
- Don't confuse `call_id` with `item_id` (different purposes)
- Don't send function output without creating new response afterward
- Don't skip event_id generation (events will be silently ignored)

### WebRTC Setup

- No STUN servers needed (OpenAI handles it)
- SDP must be sent with `Content-Type: application/sdp`
- Model and voice are query parameters, not in SDP body
- Data channel name must be `'oai-events'`

### ChromaDB Integration

- Service gracefully falls back to in-memory mode if server unavailable
- Health checks work even when ChromaDB is down
- Document chunking: 500 tokens, 100 overlap (don't change without testing)

### Notes Feature (PostgreSQL Integration)

**Database Schema**:
- **Table**: `notes`
- **Columns**: id (UUID), title (VARCHAR 255), content (TEXT), search_vector (TSVECTOR), created_at, updated_at
- **Indexes**: GIN index on `search_vector` for full-text search
- **Trigger**: Auto-updates `search_vector` when title or content changes

**Key Features**:
- **Persistence**: Notes stored in PostgreSQL, survive restarts
- **Full-Text Search**: Uses PostgreSQL `tsvector` and `to_tsquery` for keyword search
- **Async Operations**: All database operations use SQLAlchemy async (asyncpg driver)
- **Graceful Degradation**: Health check works even if database is down

**Database Migrations (Alembic)**:
```bash
# Initialize database (first time only)
cd backend
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Create notes table"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```

**Voice Command Examples**:
- "Save a note that the meeting is tomorrow at 3 PM"
- "What notes do I have?"
- "Find my notes about meetings"
- "Update that note to say the meeting is at 4 PM"
- "Delete that note"

**Implementation Notes**:
- Notes are **global/shared** (no user isolation in current implementation)
- Title max: 255 characters, Content max: 10,000 characters
- Search returns max 20 results by default
- Function detection follows same patterns as RAG (early detection critical)

## Troubleshooting Common Issues

### "Tool call ID not found in conversation"
- Function call detected too late (at `response.done` instead of `response.function_call_arguments.done`)
- See `useVoiceSession.ts` lines 126-159 for correct early detection

### Function calling not working
1. Check function registration (should happen at `session.created`)
2. Verify data channel is open when registering
3. Confirm backend REST API endpoint is accessible (`/api/rag/function-call`)
4. Check RAG service is accessible from backend
5. Verify network connectivity between frontend and backend

### WebRTC connection fails
- Verify OpenAI API key has Realtime API access
- Check SDP validation in backend logs
- Ensure microphone permissions granted

### RAG returns no results
- Verify documents are ingested (`POST /api/documents/ingest`)
- Check ChromaDB is running or in-memory fallback active
- Ensure embeddings use same model (text-embedding-3-small)

### Notes feature not working
1. **PostgreSQL Connection Issues**:
   - Verify PostgreSQL is running: `docker ps | grep postgres`
   - Check DATABASE_URL format: `postgresql+asyncpg://user:password@host:port/db`
   - Test connection: Check backend health endpoint (`http://localhost:8002/health`)
   - View PostgreSQL logs: `docker-compose -f docker-compose.postgres.yml logs`

2. **Notes Function Call Not Detected**:
   - Check function registration includes `manage_notes` in `tools` array
   - Verify backend endpoint is accessible (`POST /api/notes/function-call`)
   - Check browser console for function call logs (`[Notes]` prefix)

3. **Database Migration Errors**:
   - Ensure PostgreSQL is running before running migrations
   - Verify `DATABASE_URL` in backend `.env` file
   - Check Alembic configuration in `backend/alembic.ini`
   - Ensure models are imported in `backend/alembic/env.py`

4. **Search Not Working**:
   - Verify `search_vector` column is populated (check migration includes trigger)
   - Test search query syntax in psql: `SELECT * FROM notes WHERE search_vector @@ to_tsquery('english', 'query');`
   - Check fallback to ILIKE search in logs if full-text search fails

5. **Notes Not Persisting**:
   - Verify PostgreSQL volume is created: `docker volume ls | grep postgres`
   - Ensure you're not using `-v` flag when stopping Docker (removes volumes)
   - Check database connection in health endpoint

## Windows-Specific Notes

This codebase is being developed on Windows. Use:
- `venv\Scripts\activate` (not `source venv/bin/activate`)
- PowerShell or Command Prompt for commands
- Use forward slashes in code, backslashes in shell commands
