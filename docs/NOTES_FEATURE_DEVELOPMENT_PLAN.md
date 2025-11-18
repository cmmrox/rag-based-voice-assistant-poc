# Notes Feature - Development Plan

## Overview

This document outlines the complete implementation plan for adding a note-taking feature to the RAG-based voice assistant. The feature allows users to create, retrieve, search, update, and delete notes through natural voice conversations with the AI agent.

## Architecture Decisions

### Service Architecture
- **Approach**: Extend existing backend service (not a separate microservice)
- **Rationale**: Simpler deployment, fewer containers, reduced complexity for CRUD operations

### Database
- **Technology**: PostgreSQL 16
- **Deployment**: Separate Docker Compose file (`docker-compose.postgres.yml`)
- **Storage**: Named volume `postgres_data` for persistence
- **Search**: PostgreSQL full-text search using `tsvector` and GIN indexes

### User Context
- **Scope**: Global/shared notes (no user isolation)
- **Rationale**: Simplifies initial implementation, no auth required

### Operations Supported
1. **Create**: Save new notes with title and content
2. **List**: Retrieve all notes or specific note by ID
3. **Search**: Find notes using PostgreSQL full-text search
4. **Update**: Modify existing note content
5. **Delete**: Remove notes by ID

---

## Database Schema

### Notes Table

```sql
CREATE TABLE notes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    search_vector TSVECTOR,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Full-text search index
CREATE INDEX notes_search_idx ON notes USING GIN(search_vector);

-- Trigger to automatically update search_vector
CREATE TRIGGER notes_search_vector_update
BEFORE INSERT OR UPDATE ON notes
FOR EACH ROW EXECUTE FUNCTION
tsvector_update_trigger(search_vector, 'pg_catalog.english', title, content);
```

### Schema Design Decisions
- **UUID**: Better for distributed systems, no auto-increment conflicts
- **search_vector**: Automatic full-text search indexing
- **Timestamps**: Track creation and modification times
- **NOT NULL constraints**: Ensure data integrity

---

## API Contracts

### Backend Function Call Endpoint

**Endpoint**: `POST /api/notes/function-call`

**Request Body** (`NotesFunctionRequest`):
```json
{
  "call_id": "string (UUID)",
  "function_name": "manage_notes",
  "arguments": {
    "action": "create|list|search|update|delete",
    "title": "string (optional, max 255 chars)",
    "content": "string (optional, max 10000 chars)",
    "note_id": "string (optional, UUID)",
    "query": "string (optional, for search)"
  }
}
```

**Response Body** (`NotesFunctionResponse`):
```json
{
  "call_id": "string (matches request)",
  "function_name": "manage_notes",
  "result": {
    "success": true,
    "message": "string",
    "data": {
      "notes": [
        {
          "id": "uuid",
          "title": "string",
          "content": "string",
          "created_at": "ISO 8601 timestamp",
          "updated_at": "ISO 8601 timestamp"
        }
      ],
      "count": "integer"
    },
    "error": null
  }
}
```

### Action-Specific Behaviors

#### Create Note
- **Required**: `action="create"`, `title`, `content`
- **Returns**: Single note object with generated ID
- **Errors**: Missing fields, title/content too long

#### List Notes
- **Required**: `action="list"`
- **Optional**: `note_id` (to get specific note)
- **Returns**: Array of notes (all notes if no ID provided)
- **Errors**: Note not found (if ID specified)

#### Search Notes
- **Required**: `action="search"`, `query`
- **Returns**: Array of matching notes (max 20 results)
- **Search**: Full-text search on title and content
- **Errors**: Empty query string

#### Update Note
- **Required**: `action="update"`, `note_id`
- **Optional**: `title`, `content` (at least one must be provided)
- **Returns**: Updated note object
- **Errors**: Note not found, no fields to update

#### Delete Note
- **Required**: `action="delete"`, `note_id`
- **Returns**: Success message with deleted note ID
- **Errors**: Note not found

---

## OpenAI Function Definition

### Frontend Tool Registration

File: `frontend/constants/tools.ts`

```typescript
export const NOTES_TOOL = {
  type: 'function',
  name: 'manage_notes',
  description: 'Create, retrieve, update, delete, or search notes from previous conversations. Use this when the user wants to save information for later, retrieve saved notes, or search through their notes.',
  parameters: {
    type: 'object',
    properties: {
      action: {
        type: 'string',
        enum: ['create', 'list', 'search', 'update', 'delete'],
        description: 'The action to perform on notes'
      },
      title: {
        type: 'string',
        description: 'Title of the note (required for create, optional for update)'
      },
      content: {
        type: 'string',
        description: 'Content of the note (required for create, optional for update)'
      },
      note_id: {
        type: 'string',
        description: 'ID of the note (required for update/delete, optional for list to get specific note)'
      },
      query: {
        type: 'string',
        description: 'Search query to find notes (required for search action)'
      }
    },
    required: ['action']
  }
};
```

### Example Voice Interactions

**Create Note:**
- User: "Save a note that the meeting is tomorrow at 3 PM"
- AI calls: `manage_notes(action="create", title="Meeting Reminder", content="Meeting is tomorrow at 3 PM")`

**List Notes:**
- User: "What notes do I have?"
- AI calls: `manage_notes(action="list")`

**Search Notes:**
- User: "Find my notes about meetings"
- AI calls: `manage_notes(action="search", query="meetings")`

**Update Note:**
- User: "Update that note to say the meeting is at 4 PM instead"
- AI calls: `manage_notes(action="update", note_id="<id>", content="Meeting is tomorrow at 4 PM")`

**Delete Note:**
- User: "Delete that note"
- AI calls: `manage_notes(action="delete", note_id="<id>")`

---

## Implementation Phases

### Phase 0: Documentation & Infrastructure Setup ✓

#### Task 0.1: Create Documentation
- [x] Create `docs/` folder
- [x] Create `docs/notes-feature-development-plan.md` (this file)

#### Task 0.2: Create PostgreSQL Docker Compose
- [ ] Create `docker-compose.postgres.yml`
- [ ] Define postgres service configuration
- [ ] Add volume for data persistence
- [ ] Include health checks

**Files to create:**
- `docker-compose.postgres.yml`

---

### Phase 1: Database Infrastructure

#### Task 1.1: Backend Dependencies
- [ ] Add `sqlalchemy[asyncio]>=2.0.23` to `backend/requirements.txt`
- [ ] Add `asyncpg>=0.29.0` (PostgreSQL async driver)
- [ ] Add `alembic>=1.13.0` (database migrations)

**Files to update:**
- `backend/requirements.txt`

#### Task 1.2: Database Configuration
- [ ] Create async database engine and session factory
- [ ] Create SQLAlchemy Base and models
- [ ] Add DATABASE_URL to config settings

**Files to create:**
- `backend/app/services/database.py` - Connection management
- `backend/app/models/database.py` - SQLAlchemy models

**Files to update:**
- `backend/app/config.py` - Add DATABASE_URL setting

#### Task 1.3: Database Migrations
- [ ] Initialize Alembic: `cd backend && alembic init alembic`
- [ ] Configure `alembic.ini` with async database URL
- [ ] Update `alembic/env.py` for async operations and import models
- [ ] Create initial migration: `alembic revision --autogenerate -m "Create notes table"`
- [ ] Apply migration: `alembic upgrade head`

**Files to create:**
- `backend/alembic/` (entire directory structure)
- `backend/alembic/versions/xxxx_create_notes_table.py`

**Files to update:**
- `backend/alembic.ini`
- `backend/alembic/env.py`

---

### Phase 2: Backend Implementation

#### Task 2.1: Pydantic Schemas
- [ ] Create request/response models for notes operations
- [ ] Create function calling specific models
- [ ] Add validation rules (max lengths, required fields)

**Files to create:**
- `backend/app/models/notes_schemas.py`

**Models to define:**
- `NoteBase` - Common fields
- `NoteCreate` - For creation
- `NoteUpdate` - For updates (all fields optional)
- `NoteResponse` - API response
- `NoteSearchRequest` - Search parameters
- `NotesData` - Data wrapper for function results
- `NotesFunctionRequest` - Function call request
- `NotesFunctionResult` - Function call result
- `NotesFunctionResponse` - Function call response

#### Task 2.2: Database Service Layer
- [ ] Implement CRUD operations with async SQLAlchemy
- [ ] Add full-text search using PostgreSQL `to_tsvector`
- [ ] Add error handling and logging
- [ ] Implement connection pooling

**Files to create:**
- `backend/app/services/notes_db.py`

**Functions to implement:**
- `create_note(title, content) -> Note`
- `get_note(note_id) -> Note | None`
- `list_notes() -> List[Note]`
- `update_note(note_id, title?, content?) -> Note | None`
- `delete_note(note_id) -> bool`
- `search_notes(query, limit=20) -> List[Note]`

#### Task 2.3: Function Call Handler Route
- [ ] Create FastAPI router for function calling endpoint
- [ ] Implement action routing logic
- [ ] Format responses according to function calling contract
- [ ] Add comprehensive error handling

**Files to create:**
- `backend/app/routes/notes_function.py`

**Endpoint:**
- `POST /api/notes/function-call` - Main function call handler

**Logic flow:**
1. Validate request (call_id, function_name, arguments)
2. Extract action from arguments
3. Route to appropriate database operation
4. Format result into function response
5. Handle errors gracefully

#### Task 2.4: Constants and Validation
- [ ] Define constants for limits and defaults
- [ ] Add validation functions for note operations

**Files to create:**
- `backend/app/constants/notes.py`

**Constants to define:**
- `MAX_TITLE_LENGTH = 255`
- `MAX_CONTENT_LENGTH = 10000`
- `MAX_SEARCH_RESULTS = 20`
- `DEFAULT_SEARCH_LIMIT = 10`

**Files to update:**
- `backend/app/utils/validators.py`

**Validators to add:**
- `validate_note_create(title, content)`
- `validate_note_update(note_id, title?, content?)`
- `validate_note_search(query)`

#### Task 2.5: Backend Integration
- [ ] Register notes router in main application
- [ ] Update health check to verify PostgreSQL connection
- [ ] Add DATABASE_URL to .env.example
- [ ] Update CORS if needed

**Files to update:**
- `backend/app/main.py` - Register router, update health check
- `backend/.env.example` - Add DATABASE_URL

---

### Phase 3: Frontend Implementation

#### Task 3.1: Function Definition
- [ ] Add NOTES_TOOL to tools constants
- [ ] Ensure proper TypeScript typing

**Files to update:**
- `frontend/constants/tools.ts`

#### Task 3.2: REST Client
- [ ] Create notes client mirroring RAG client pattern
- [ ] Implement executeNotesFunction
- [ ] Add TypeScript interfaces

**Files to create:**
- `frontend/utils/notesClient.ts`

**Functions to implement:**
- `executeNotesFunction(callId, functionName, args) -> NotesFunctionResponse`

**Interfaces to define:**
- `NotesArguments`
- `NotesFunctionResponse`
- `Note`

#### Task 3.3: Function Registration and Handling
- [ ] Add NOTES_TOOL to function registration in useVoiceSession
- [ ] Add notes function handling in function call detection
- [ ] Implement call to notesClient.executeNotesFunction
- [ ] Add error handling and logging

**Files to update:**
- `frontend/hooks/useVoiceSession.ts`

**Changes:**
1. Import NOTES_TOOL and notesClient
2. Add NOTES_TOOL to registerFunctions() call
3. Add case for 'manage_notes' in function execution logic
4. Call executeNotesFunction and send result back to OpenAI

---

### Phase 4: Testing & Documentation

#### Task 4.1: Docker Setup Validation
- [ ] Test standalone PostgreSQL: `docker-compose -f docker-compose.postgres.yml up`
- [ ] Verify volume persistence (stop/start container)
- [ ] Verify health check passes
- [ ] Test connection from backend

**Testing checklist:**
- [ ] PostgreSQL container starts successfully
- [ ] Database `notes_db` is created
- [ ] Volume persists data across restarts
- [ ] Health check returns healthy status
- [ ] Backend can connect using DATABASE_URL

#### Task 4.2: Integration Testing
- [ ] Start all services (ChromaDB, PostgreSQL, Backend, Frontend)
- [ ] Test each operation via voice commands
- [ ] Verify database persistence
- [ ] Test error scenarios

**Test scenarios:**

**Create Note:**
- [ ] "Save a note that Python is awesome"
- [ ] Verify note appears in database
- [ ] Test with very long content (near limit)
- [ ] Test with empty title/content (should fail)

**List Notes:**
- [ ] "Show me all my notes"
- [ ] "What notes do I have?"
- [ ] Verify all notes returned

**Search Notes:**
- [ ] "Find notes about Python"
- [ ] "Search for meeting notes"
- [ ] Test with no results
- [ ] Test relevance ranking

**Update Note:**
- [ ] "Update that note to say Python is really awesome"
- [ ] Verify only content changes
- [ ] Test updating non-existent note (should fail)

**Delete Note:**
- [ ] "Delete that note"
- [ ] Verify note removed from database
- [ ] Test deleting non-existent note (should fail)

**Error Handling:**
- [ ] PostgreSQL down during operation
- [ ] Invalid note ID format
- [ ] Missing required fields
- [ ] Content exceeds max length

#### Task 4.3: Documentation Finalization
- [ ] Update CLAUDE.md with notes feature section
- [ ] Document environment variables
- [ ] Add troubleshooting section
- [ ] Create usage examples

**Files to update:**
- `CLAUDE.md`

**Sections to add:**
1. Notes Feature Overview
2. Database Setup (PostgreSQL)
3. Environment Configuration
4. Function Calling Flow for Notes
5. Troubleshooting Notes Feature
6. Example Voice Commands

---

## Docker Compose Configuration

### PostgreSQL Service (docker-compose.postgres.yml)

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:16-alpine
    container_name: voice-assistant-postgres
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: notes_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - voice-assistant-network

volumes:
  postgres_data:
    driver: local

networks:
  voice-assistant-network:
    external: true
```

### Usage Commands

**Start PostgreSQL only:**
```bash
docker-compose -f docker-compose.postgres.yml up -d
```

**Stop PostgreSQL:**
```bash
docker-compose -f docker-compose.postgres.yml down
```

**View logs:**
```bash
docker-compose -f docker-compose.postgres.yml logs -f
```

**Reset database (CAUTION - deletes all data):**
```bash
docker-compose -f docker-compose.postgres.yml down -v
```

---

## Environment Variables

### Backend (.env)

```env
# Existing
OPENAI_API_KEY=sk-your-api-key-here
BACKEND_PORT=8002
RAG_SERVICE_URL=http://localhost:8001

# New for Notes Feature
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/notes_db
```

**For Docker:**
```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/notes_db
```

---

## Migration Commands

### Initial Setup

```bash
# Navigate to backend
cd backend

# Install dependencies (if not already done)
pip install -r requirements.txt

# Initialize Alembic (first time only)
alembic init alembic

# Configure alembic.ini and env.py (manual step)
# See Phase 1, Task 1.3

# Create initial migration
alembic revision --autogenerate -m "Create notes table"

# Apply migration
alembic upgrade head
```

### Future Migrations

```bash
# Create new migration after model changes
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history

# View current version
alembic current
```

---

## Troubleshooting

### PostgreSQL Connection Issues

**Symptom**: Backend cannot connect to PostgreSQL

**Solutions:**
1. Verify PostgreSQL is running: `docker ps | grep postgres`
2. Check DATABASE_URL format matches driver (asyncpg)
3. Verify network connectivity: `docker network inspect voice-assistant-network`
4. Check PostgreSQL logs: `docker-compose -f docker-compose.postgres.yml logs`

### Migration Errors

**Symptom**: `alembic upgrade head` fails

**Solutions:**
1. Ensure PostgreSQL is running and accessible
2. Verify DATABASE_URL is correct in alembic.ini
3. Check migration file for syntax errors
4. Ensure models are imported in alembic/env.py

### Full-Text Search Not Working

**Symptom**: Search returns no results despite matching content

**Solutions:**
1. Verify search_vector column is populated: `SELECT title, search_vector FROM notes;`
2. Check trigger is installed: `\d notes` in psql
3. Test search query syntax: `SELECT * FROM notes WHERE search_vector @@ to_tsquery('english', 'query');`
4. Ensure content is in English (or adjust language in trigger)

### Notes Not Persisting

**Symptom**: Notes disappear after container restart

**Solutions:**
1. Verify volume is created: `docker volume ls | grep postgres`
2. Check volume mount in docker-compose.postgres.yml
3. Ensure you're not using `-v` flag when stopping (removes volumes)

---

## Performance Considerations

### Database Indexing
- GIN index on search_vector for fast full-text search
- Consider adding index on created_at if sorting by date frequently
- UUID primary key is indexed by default

### Connection Pooling
- SQLAlchemy async engine uses connection pooling by default
- Default pool size: 5 connections
- Adjust in `database.py` if needed: `pool_size=10, max_overflow=20`

### Search Query Optimization
- Limit search results (default 20)
- Use `LIMIT` clause in all list queries
- Consider pagination for large result sets (future enhancement)

---

## Future Enhancements

### Phase 2 Features (Not in Current Scope)
- [ ] User authentication and note isolation
- [ ] Note categories/tags
- [ ] Semantic search using embeddings (RAG-style)
- [ ] Note sharing between users
- [ ] Export notes (JSON, Markdown, PDF)
- [ ] Note attachments (files, images)
- [ ] Note versioning/history
- [ ] Pagination for large note collections
- [ ] Bulk operations (delete multiple, update multiple)

---

## Estimated Effort

**Total**: 6-8 hours for experienced developer

**Breakdown:**
- Phase 0 (Documentation): 1 hour
- Phase 1 (Database Setup): 1.5 hours
- Phase 2 (Backend): 2.5 hours
- Phase 3 (Frontend): 1.5 hours
- Phase 4 (Testing): 1.5 hours

---

## Success Criteria

- [ ] User can create notes via voice command
- [ ] User can list all notes via voice command
- [ ] User can search notes via voice command
- [ ] User can update notes via voice command
- [ ] User can delete notes via voice command
- [ ] Notes persist across application restarts
- [ ] Full-text search returns relevant results
- [ ] All error cases handled gracefully
- [ ] Documentation is complete and accurate
- [ ] Code follows existing project patterns

---

## References

- Existing RAG implementation: `backend/app/routes/rag_function.py`
- Function calling pattern: `frontend/hooks/useVoiceSession.ts`
- Docker patterns: `docker-compose.chromadb.yml`
- PostgreSQL full-text search: https://www.postgresql.org/docs/current/textsearch.html
- SQLAlchemy async: https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html

---

**Document Version**: 1.0
**Last Updated**: 2025-11-18
**Status**: Ready for Implementation
