# API Documentation

## Backend API

### WebSocket Endpoint

#### `/ws/signaling`

WebSocket endpoint for WebRTC signaling.

**Connection:** `ws://localhost:8002/ws/signaling`

**Message Types:**

##### Client → Server

1. **Session Request**
   ```json
   {
     "type": "session_request",
     "session_id": "optional-uuid"
   }
   ```

2. **Answer**
   ```json
   {
     "type": "answer",
     "sdp": "SDP string",
     "type": "answer",
     "session_id": "uuid"
   }
   ```

3. **ICE Candidate**
   ```json
   {
     "type": "ice_candidate",
     "candidate": {
       "candidate": "candidate string",
       "sdpMid": "mid",
       "sdpMLineIndex": 0
     },
     "session_id": "uuid"
   }
   ```

4. **End Session**
   ```json
   {
     "type": "end_session",
     "session_id": "uuid"
   }
   ```

##### Server → Client

1. **Offer**
   ```json
   {
     "type": "offer",
     "sdp": "SDP string",
     "type": "offer",
     "session_id": "uuid"
   }
   ```

2. **ICE Candidate**
   ```json
   {
     "type": "ice_candidate",
     "candidate": {
       "candidate": "candidate string",
       "sdpMid": "mid",
       "sdpMLineIndex": 0
     },
     "session_id": "uuid"
   }
   ```

3. **Session Ready**
   ```json
   {
     "type": "session_ready",
     "session_id": "uuid"
   }
   ```

4. **Transcription**
   ```json
   {
     "type": "transcription",
     "text": "transcribed text",
     "session_id": "uuid"
   }
   ```

5. **Response Text**
   ```json
   {
     "type": "response_text",
     "text": "response text",
     "session_id": "uuid"
   }
   ```

6. **Session Ended**
   ```json
   {
     "type": "session_ended",
     "session_id": "uuid"
   }
   ```

### HTTP Endpoints

#### `GET /health`

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "backend"
}
```

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

**Response:**
```json
{
  "status": "success",
  "chunks": 10,
  "message": "Document ingested successfully with 10 chunks"
}
```

**Error Response:**
```json
{
  "detail": "Error message"
}
```

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

**Response:**
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

**Error Response:**
```json
{
  "detail": "Error message"
}
```

#### `GET /health`

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "rag-service"
}
```

---

## Function Calling (RAG Integration)

The application uses OpenAI Realtime API function calling to intelligently search the knowledge base when needed.

### Function: `search_knowledge_base`

**Description**: Searches the knowledge base for relevant information to answer user questions.

**Parameters**:
- `query` (string, required): The search query to find relevant information

**Flow**:
1. User asks a question via voice
2. OpenAI Realtime API transcribes the question
3. Model decides if knowledge base search is needed
4. If needed, model calls `search_knowledge_base` function
5. Frontend receives function call event via WebRTC data channel
6. Frontend sends function call request to backend via WebSocket (`/api/ws/events/{session_id}`)
7. Backend executes RAG query and returns results
8. Frontend sends function call output back to OpenAI via data channel
9. Model generates response using retrieved context

### WebSocket Endpoint: `/api/ws/events/{session_id}`

**Connection**: `ws://localhost:8002/api/ws/events/{session_id}`

#### Client → Server Messages

**Function Call Request**:
```json
{
  "type": "function_call",
  "call_id": "call_abc123",
  "function_name": "search_knowledge_base",
  "arguments": {
    "query": "What is the main topic?"
  }
}
```

#### Server → Client Messages

**Function Call Result**:
```json
{
  "type": "function_call_result",
  "call_id": "call_abc123",
  "function_name": "search_knowledge_base",
  "result": {
    "success": true,
    "context": "[Document 1] Relevant text...",
    "sources": [
      {
        "source": "document.pdf",
        "chunk_id": 0,
        "chunk_index": 0
      }
    ]
  }
}
```

**Function Call Error**:
```json
{
  "type": "function_call_result",
  "call_id": "call_abc123",
  "function_name": "search_knowledge_base",
  "result": {
    "success": false,
    "error": "Error message"
  }
}
```

## WebSocket Protocol Flow

1. Client connects to `/ws/signaling`
2. Client sends `session_request`
3. Server creates session and sends `offer`
4. Client receives offer, creates answer, sends `answer`
5. Client and server exchange `ice_candidate` messages
6. Server sends `session_ready` when connection established
7. Audio streams bidirectionally via WebRTC
8. **With Function Calling**: Model calls `search_knowledge_base` when needed
9. Function call executed via WebSocket `/api/ws/events/{session_id}`
10. Model generates response using retrieved context
11. Server sends `response_text` when assistant responds
12. Client sends `end_session` to terminate session

---

## Error Handling

All endpoints return appropriate HTTP status codes:
- `200` - Success
- `400` - Bad Request (invalid input)
- `500` - Internal Server Error

WebSocket errors are sent as error messages and the connection may be closed.

---

## Rate Limiting

No rate limiting implemented in POC version.

---

## Authentication

No authentication implemented in POC version.

