# API Documentation

## Overview

This document describes the API endpoints for the RAG-Based Voice Assistant backend and RAG service.

## Architecture Summary

The current implementation uses the following architecture:

1. **Frontend ↔ OpenAI Realtime API**: Direct WebRTC connection with data channel for audio and events
2. **Frontend → Backend**: HTTP POST for SDP forwarding to OpenAI
3. **Frontend ↔ Backend**: REST API (HTTP POST) for RAG function call execution
4. **Backend ↔ RAG Service**: REST API (HTTP POST) for knowledge base queries

## Backend API

### HTTP Endpoints

#### `POST /api/realtime/session`

Creates an OpenAI Realtime API session by forwarding the SDP offer to OpenAI and returning the SDP answer.

**Request:**
- Method: `POST`
- Content-Type: `application/json`
- Body:
  ```json
  {
    "sdp": {
      "type": "offer",
      "sdp": "SDP string from browser"
    }
  }
  ```

**Example using curl:**
```bash
curl -X POST http://localhost:8002/api/realtime/session \
  -H "Content-Type: application/json" \
  -d '{"sdp": {"type": "offer", "sdp": "v=0..."}}'
```

**Response (Success):**
```json
{
  "type": "answer",
  "sdp": "SDP answer from OpenAI"
}
```

**Response (Error):**
```json
{
  "detail": "Error message"
}
```

**Implementation Notes:**
- Forwards client SDP offer to OpenAI Realtime API
- Returns OpenAI's SDP answer to establish WebRTC connection
- WebRTC connection is established directly between frontend and OpenAI
- Session timeout: 30 seconds

---

#### `GET /health`

Health check endpoint for backend service.

**Response:**
```json
{
  "status": "healthy",
  "service": "backend",
  "rag_service": {
    "status": "connected",
    "url": "http://localhost:8001"
  },
  "openai_api_key_configured": true
}
```

**Response (Degraded):**
```json
{
  "status": "degraded",
  "service": "backend",
  "rag_service": {
    "status": "error",
    "url": "http://localhost:8001",
    "details": {
      "error": "Connection refused"
    }
  },
  "openai_api_key_configured": true
}
```

---

#### `POST /api/rag/function-call`

REST API endpoint for executing RAG function calls.

**Request:**
- Method: `POST`
- Content-Type: `application/json`
- URL: `http://localhost:8002/api/rag/function-call`
- Body:
  ```json
  {
    "call_id": "call_abc123",
    "function_name": "rag_knowledge",
    "arguments": {
      "query": "What is the main topic?"
    }
  }
  ```

**Flow:**
1. OpenAI Realtime API calls `rag_knowledge` function via WebRTC data channel
2. Frontend receives function call event from OpenAI
3. Frontend sends REST API request to backend with function details
4. Backend executes RAG query and returns result
5. Frontend sends result back to OpenAI via data channel

**Response (Success):**
```json
{
  "call_id": "call_abc123",
  "function_name": "rag_knowledge",
  "result": {
    "success": true,
    "context": "[Document 1] Relevant text...\n\n[Document 2] More text...",
    "sources": [
      {
        "source": "document.pdf",
        "content": "chunk content",
        "metadata": {}
      }
    ],
    "message": ""
  }
}
```

**Response (Error):**
```json
{
  "call_id": "call_abc123",
  "function_name": "rag_knowledge",
  "result": {
    "success": false,
    "context": "",
    "sources": [],
    "message": "",
    "error": "Query parameter is required"
  }
}
```

**HTTP Status Codes:**
- `200 OK`: Function executed successfully (check result.success for actual status)
- `400 Bad Request`: Invalid function name or malformed request
- `500 Internal Server Error`: Server error during execution

---

## RAG Service API

### HTTP Endpoints

#### `POST /api/documents/ingest`

Upload and ingest a document into the knowledge base.

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body: File upload (PDF, TXT, or MD)

**Example using curl:**
```bash
curl -X POST http://localhost:8001/api/documents/ingest \
  -F "file=@document.pdf"
```

**Response (Success):**
```json
{
  "status": "success",
  "chunks": 10,
  "message": "Document ingested successfully with 10 chunks"
}
```

**Response (Error):**
```json
{
  "detail": "Error message"
}
```

---

#### `POST /api/rag/query`

Process a query and retrieve relevant context from the knowledge base.

**Request:**
- Method: `POST`
- Content-Type: `application/json`
- Body:
  ```json
  {
    "query": "What is the main topic of the document?"
  }
  ```

**Example using curl:**
```bash
curl -X POST http://localhost:8001/api/rag/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the main topic?"}'
```

**Response (Success):**
```json
{
  "context": "[Document 1 - Source: document.pdf]\nRelevant text...\n\n[Document 2 - Source: document.pdf]\nMore relevant text...",
  "sources": [
    {
      "source": "document.pdf",
      "chunk_id": 0,
      "chunk_index": 0
    }
  ],
  "message": "Retrieved 5 relevant documents"
}
```

**Response (Error):**
```json
{
  "detail": "Error message"
}
```

---

#### `GET /health`

Health check endpoint for RAG service.

**Response:**
```json
{
  "status": "healthy",
  "service": "rag-service",
  "chromadb_connected": true
}
```

---

## Function Calling (RAG Integration)

The application uses OpenAI Realtime API's native function calling feature to intelligently search the knowledge base when needed.

### Function: `rag_knowledge`

**Description**: Search and retrieve information from the knowledge base to answer user questions.

**Parameters**:
- `query` (string, required): The search query to find relevant information

**Function Definition (registered in session configuration)**:
```json
{
  "type": "function",
  "name": "rag_knowledge",
  "description": "Search and retrieve information from the knowledge base to answer user questions. Use this function when you need specific information from documents that might be in the knowledge base.",
  "parameters": {
    "type": "object",
    "properties": {
      "query": {
        "type": "string",
        "description": "The search query to find relevant information from the knowledge base"
      }
    },
    "required": ["query"]
  }
}
```

---

### Complete Flow

1. **User speaks** → Frontend captures audio via microphone
2. **Frontend → OpenAI** → Audio sent via WebRTC connection
3. **OpenAI Realtime API** → Transcribes speech to text
4. **Model analyzes query** → Decides if knowledge base search is needed
5. **Model calls function** → If needed, calls `rag_knowledge` function
6. **OpenAI → Frontend** → Function call event sent via WebRTC data channel (`conversation.item.completed`)
7. **Frontend → Backend** → REST API POST to `/api/rag/function-call` with function details
8. **Backend → RAG Service** → HTTP POST to `/api/rag/query`
9. **RAG Service** → Generates embedding, queries ChromaDB, assembles context
10. **RAG Service → Backend** → Returns context and sources
11. **Backend → Frontend** → Function result returned as REST API response
12. **Frontend → OpenAI** → Function call output sent via data channel (`conversation.item.create`)
13. **OpenAI generates response** → Uses retrieved context to generate informed answer
14. **OpenAI → Frontend** → Response audio stream via WebRTC
15. **Frontend plays audio** → User hears the answer

---

## Complete Request/Response Examples

### Example 1: Create Realtime Session

**Request:**
```bash
curl -X POST http://localhost:8002/api/realtime/session \
  -H "Content-Type: application/json" \
  -d '{
    "sdp": {
      "type": "offer",
      "sdp": "v=0\r\no=- 123456789 2 IN IP4 127.0.0.1\r\ns=-\r\nt=0 0..."
    }
  }'
```

**Response:**
```json
{
  "type": "answer",
  "sdp": "v=0\r\no=- 987654321 2 IN IP4 10.0.0.1\r\ns=-\r\nt=0 0..."
}
```

---

### Example 2: Ingest Document

**Request:**
```bash
curl -X POST http://localhost:8001/api/documents/ingest \
  -F "file=@product_manual.pdf"
```

**Response:**
```json
{
  "status": "success",
  "chunks": 25,
  "message": "Document ingested successfully with 25 chunks"
}
```

---

### Example 3: Query Knowledge Base

**Request:**
```bash
curl -X POST http://localhost:8001/api/rag/query \
  -H "Content-Type: application/json" \
  -d '{"query": "How do I reset the device?"}'
```

**Response:**
```json
{
  "context": "[Document 1 - Source: product_manual.pdf]\nTo reset the device, press and hold the power button for 10 seconds...\n\n[Document 2 - Source: product_manual.pdf]\nFactory reset: Navigate to Settings > System > Reset...",
  "sources": [
    {
      "source": "product_manual.pdf",
      "chunk_id": 5,
      "chunk_index": 5
    },
    {
      "source": "product_manual.pdf",
      "chunk_id": 12,
      "chunk_index": 12
    }
  ],
  "message": "Retrieved 2 relevant documents"
}
```

---

### Example 4: REST API Function Call Execution

**Request (Frontend → Backend):**
```bash
curl -X POST http://localhost:8002/api/rag/function-call \
  -H "Content-Type: application/json" \
  -d '{
    "call_id": "call_TZj4KqW3e8",
    "function_name": "rag_knowledge",
    "arguments": {
      "query": "What are the key features?"
    }
  }'
```

**Response (Backend → Frontend):**
```json
{
  "call_id": "call_TZj4KqW3e8",
  "function_name": "rag_knowledge",
  "result": {
    "success": true,
    "context": "[Document 1] The key features include: voice recognition, RAG integration, and real-time responses...",
    "sources": [
      {
        "source": "overview.pdf",
        "content": "chunk content...",
        "metadata": {}
      }
    ],
    "message": ""
  }
}
```

---

## Error Handling

All HTTP endpoints return appropriate HTTP status codes:
- `200` - Success
- `400` - Bad Request (invalid input)
- `422` - Unprocessable Entity (validation error)
- `500` - Internal Server Error

REST API errors include detailed error messages in the response body for debugging.

---

## Rate Limiting

No rate limiting implemented in POC version.

---

## Authentication

No authentication implemented in POC version. API key management handled via environment variables.

---

## Service Ports

| Service | Port | Description |
|---------|------|-------------|
| Frontend | 3000 | Next.js web application |
| Backend | 8002 | FastAPI backend service |
| RAG Service | 8001 | RAG query and document ingestion service |
| ChromaDB | 8000 | Vector database (internal, not exposed) |

---

## Implementation Notes

### Session Management
- Sessions are managed client-side
- Backend is completely stateless
- Session ID generated by frontend for tracking only
- No persistent connections maintained on backend

### WebRTC Connection
- Direct connection between frontend and OpenAI
- No backend involvement in audio streaming
- Backend only forwards SDP for connection establishment
- WebRTC data channel used for events and function calls

### Function Calling
- Native OpenAI Realtime API function calling
- Model decides when to call `rag_knowledge`
- Execution happens via REST API POST to backend
- Results sent back via WebRTC data channel to OpenAI

---

**Last Updated**: January 2025
**Version**: 1.0.0 (POC)
**Status**: ✅ Current with Working Implementation
