# Product Requirements Document (PRD) - Proof of Concept (POC)
## Web-Based Voice Assistant Application - POC Version

**Version:** 1.0-POC  
**Date:** 2024  
**Status:** Draft  
**Document Owner:** Development Team  
**Purpose:** Proof of Concept Implementation

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Technology Stack](#2-technology-stack)
3. [POC Scope & Limitations](#3-poc-scope--limitations)
4. [Architecture Overview](#4-architecture-overview)
5. [Functional Requirements](#5-functional-requirements)
6. [Technical Implementation Details](#6-technical-implementation-details)
7. [UI/UX Requirements](#7-uiux-requirements)
8. [Success Criteria](#8-success-criteria)
9. [Implementation Phases](#9-implementation-phases)
10. [Appendices](#10-appendices)

---

## 1. Executive Summary

### 1.1 Overview

This document outlines the requirements for developing a **Proof of Concept (POC)** of a web-based voice assistant application. The POC demonstrates real-time, bidirectional voice interactions between users and an AI-powered service using OpenAI's Realtime API, WebRTC for peer-to-peer communication, and ChromaDB-based Retrieval-Augmented Generation (RAG) for knowledge-grounded responses.

### 1.2 POC Objectives

The primary objectives of this POC are:

1. **Validate Core Architecture**: Prove the feasibility of integrating WebRTC, OpenAI Realtime API, and ChromaDB RAG in a single application
2. **Demonstrate Real-Time Voice Interaction**: Show end-to-end voice conversation flow with sub-second latency
3. **Validate RAG Integration**: Prove that knowledge retrieval enhances response quality
4. **Test Technology Stack**: Validate Python/FastAPI backend and Next.js frontend integration
5. **Identify Technical Challenges**: Surface any integration or performance issues early

### 1.3 POC Scope

**In Scope:**
- Single-user voice sessions
- WebRTC-based audio streaming
- OpenAI Realtime API integration (STT/TTS)
- ChromaDB RAG pipeline with document ingestion
- Basic web UI with microphone control
- Real-time transcription display
- Knowledge-grounded responses

**Out of Scope:**
- Multi-user concurrent sessions
- User authentication and authorization
- Persistent session storage (Redis/PostgreSQL)
- Advanced admin features
- Mobile app development
- Production-grade security hardening
- Comprehensive monitoring and analytics
- Multi-tenancy support

### 1.4 Success Criteria

The POC will be considered successful if:
- End-to-end voice interaction works (user speaks → system responds)
- Response latency is < 2 seconds (relaxed from production target)
- RAG retrieval successfully enhances responses with knowledge base context
- System handles at least 5 consecutive conversation turns
- Basic error handling prevents complete system failures

---

## 2. Technology Stack

### 2.1 Frontend

**Framework:** Next.js 14+ (App Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS (minimal styling for POC)
- **Audio:** Web Audio API + MediaRecorder API
- **WebRTC:** Native WebRTC API
- **HTTP Client:** Fetch API for REST API communication
- **State Management:** React Context API + useState/useEffect hooks

**Key Libraries:**
- `next` - Next.js framework
- `react` - React library
- `react-dom` - React DOM rendering
- `tailwindcss` - Utility-first CSS framework (optional, minimal)

### 2.2 Backend

**Framework:** FastAPI (Python 3.11+)
- **Language:** Python 3.11+
- **HTTP Server:** FastAPI REST API endpoints
- **HTTP Client:** `httpx` for async HTTP requests
- **OpenAI Integration:** `openai` Python SDK
- **WebRTC Signaling:** REST API endpoints for SDP exchange using FastAPI

**Key Libraries:**
- `fastapi` - Modern Python web framework
- `uvicorn` - ASGI server
- `httpx` - Async HTTP client
- `openai` - OpenAI Python SDK
- `python-dotenv` - Environment variable management
- `pydantic` - Data validation

### 2.3 RAG Service

**Framework:** FastAPI (Python 3.11+)
- **Language:** Python 3.11+
- **Vector Database:** ChromaDB
- **Embeddings:** OpenAI Embeddings API
- **Document Processing:** PDF, TXT, MD support

**Key Libraries:**
- `fastapi` - API framework
- `chromadb` - Vector database client
- `openai` - Embeddings API
- `pypdf2` or `pdfplumber` - PDF processing
- `python-docx` - DOCX processing (optional)
- `markdown` - Markdown parsing

### 2.4 Infrastructure

**Containerization:**
- **Docker** - Container runtime
- **Docker Compose** - Multi-container orchestration

**Services:**
- **ChromaDB** - Vector database (Docker container)
- **STUN Server** - Public STUN servers (e.g., Google STUN)
- **TURN Server** - Self-hosted or cloud TURN (optional for POC)

**Development Tools:**
- **Git** - Version control
- **Python Virtual Environment** - Python dependency isolation
- **npm/pnpm** - Node.js package management

### 2.5 External Services

- **OpenAI Realtime API** - Voice STT/TTS and response generation
- **OpenAI Embeddings API** - Text embeddings for RAG
- **Public STUN Servers** - WebRTC NAT traversal

---

## 3. POC Scope & Limitations

### 3.1 Included Features

#### 3.1.1 Core Voice Interaction
- ✅ Single-user voice session initiation
- ✅ Real-time audio capture from browser microphone
- ✅ WebRTC peer connection establishment
- ✅ Audio streaming to backend
- ✅ Speech-to-text transcription (OpenAI Realtime API)
- ✅ Text-to-speech audio response
- ✅ Audio playback in browser

#### 3.1.2 RAG Integration
- ✅ Document upload (PDF, TXT, MD)
- ✅ Document chunking and embedding generation
- ✅ ChromaDB vector storage
- ✅ Query embedding generation
- ✅ Vector similarity search
- ✅ Function calling for intelligent RAG integration

#### 3.1.3 User Interface
- ✅ Microphone button (start/stop)
- ✅ Status indicator (idle, listening, processing, speaking)
- ✅ Conversation transcript display
- ✅ Basic error messages

#### 3.1.4 Backend Services
- ✅ WebRTC signaling server
- ✅ OpenAI Realtime API gateway
- ✅ RAG service integration
- ✅ Session management (in-memory)

### 3.2 Excluded Features

#### 3.2.1 Not in POC Scope
- ❌ User authentication/authorization
- ❌ Multi-user concurrent sessions
- ❌ Persistent session storage (Redis/PostgreSQL)
- ❌ Conversation history persistence
- ❌ User preferences and settings
- ❌ Advanced admin dashboard
- ❌ Document management UI
- ❌ Analytics and monitoring dashboard
- ❌ Mobile app
- ❌ Production-grade security (beyond basic API key management)
- ❌ Load balancing and horizontal scaling
- ❌ Comprehensive error recovery
- ❌ Rate limiting and quota management
- ❌ Multi-language support
- ❌ Voice customization options

### 3.3 Known Limitations

1. **Session Persistence**: Sessions are stored in-memory and lost on server restart
2. **Concurrent Users**: Only one active session at a time (can be extended to 5-10 for testing)
3. **Error Recovery**: Basic error handling; no automatic retry for all failure scenarios
4. **Security**: Basic API key management; no advanced security features
5. **Performance**: Not optimized for production-scale performance
6. **Monitoring**: Basic logging only; no metrics dashboard
7. **Document Management**: Manual document upload via API; no UI

### 3.4 Assumptions

1. Development environment with Docker installed
2. OpenAI API key available with Realtime API access
3. Modern browser with WebRTC support (Chrome, Firefox, Edge)
4. Microphone permissions granted by user
5. Stable internet connection for testing
6. Basic knowledge base documents available for ingestion

---

## 4. Architecture Overview

### 4.1 System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Next.js)                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Components:                                          │   │
│  │  - MicrophoneButton                                    │   │
│  │  - Transcript                                         │   │
│  │  - StatusIndicator                                    │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  WebRTC Client:                                       │   │
│  │  - Audio capture (MediaRecorder)                     │   │
│  │  - Audio playback (Web Audio API)                    │   │
│  │  - Peer connection management                        │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  HTTP Client (Fetch API):                            │   │
│  │  - REST API calls for WebRTC signaling              │   │
│  │  - Function call execution via POST                  │   │
│  └──────────────┬────────────────────────────────────────┘   │
└─────────────────┼────────────────────────────────────────────┘
                  │ REST API (signaling + function calls)
                  │ WebRTC (audio stream)
                  │
┌─────────────────▼────────────────────────────────────────────┐
│              Backend (FastAPI)                                 │
│  ┌──────────────────────────────────────────────────────┐     │
│  │  REST API Signaling Endpoints                        │     │
│  │  - SDP exchange via POST /api/realtime/session      │     │
│  │  - Function call handling via POST                   │     │
│  │  - Stateless session coordination                    │     │
│  └──────────────┬───────────────────────────────────────┘     │
│                 │                                              │
│  ┌──────────────▼───────────────────────────────────────┐     │
│  │  OpenAI Realtime API Gateway                        │     │
│  │  - SDP forwarding to OpenAI Realtime API            │     │
│  │  - Session configuration management                  │     │
│  │  - Model and voice parameter handling               │     │
│  └──────────────┬───────────────────────────────────────┘     │
│                 │                                              │
│  ┌──────────────▼───────────────────────────────────────┐     │
│  │  RAG Service Client                                  │     │
│  │  - HTTP client to RAG service                       │     │
│  │  - Context retrieval coordination                    │     │
│  └──────────────┬───────────────────────────────────────┘     │
└─────────────────┼──────────────────────────────────────────────┘
                  │ HTTP/REST
                  │
┌─────────────────▼────────────────────────────────────────────┐
│            RAG Service (FastAPI)                             │
│  ┌──────────────────────────────────────────────────────┐    │
│  │  Query Processing:                                    │    │
│  │  - Query embedding generation (OpenAI API)           │    │
│  │  - ChromaDB vector search                            │    │
│  │  - Context assembly                                  │    │
│  └──────────────┬───────────────────────────────────────┘    │
│                 │                                             │
│  ┌──────────────▼───────────────────────────────────────┐    │
│  │  Document Ingestion:                                 │    │
│  │  - Document parsing (PDF, TXT, MD)                   │    │
│  │  - Text chunking                                     │    │
│  │  - Embedding generation                              │    │
│  │  - ChromaDB storage                                  │    │
│  └──────────────────────────────────────────────────────┘    │
└─────────────────┼──────────────────────────────────────────────┘
                  │
┌─────────────────▼────────────────────────────────────────────┐
│              ChromaDB (Docker)                               │
│  - Vector storage                                            │
│  - Similarity search                                          │
│  - Metadata management                                        │
└──────────────────────────────────────────────────────────────┘

External Services:
┌─────────────────────────────────────────────────────────────┐
│  OpenAI Realtime API (POST https://api.openai.com/v1/...)  │
│  - WebRTC session creation via REST POST endpoint          │
│  OpenAI Embeddings API (https://api.openai.com/v1/...)     │
│  STUN Servers (public)                                      │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 Component Responsibilities

#### 4.2.1 Frontend (Next.js)
- **Audio Capture**: Use MediaRecorder API to capture microphone audio
- **WebRTC Client**: Establish peer connection with OpenAI Realtime API
- **Audio Playback**: Play received audio using Web Audio API
- **UI Rendering**: Display microphone button, transcript, status
- **HTTP Client**: Handle WebRTC signaling and function calls via REST API
- **State Management**: Manage session state, transcript, status

#### 4.2.2 Backend (FastAPI)
- **REST API Signaling Endpoints**: Handle SDP exchange for WebRTC setup
- **OpenAI Gateway**: Forward SDP to OpenAI Realtime API
- **Function Call Execution**: Execute RAG function calls via REST endpoint
- **Stateless Coordination**: No persistent connections or session storage

#### 4.2.3 RAG Service (FastAPI)
- **Document Ingestion**: Parse and chunk documents
- **Embedding Generation**: Generate embeddings via OpenAI API
- **ChromaDB Management**: Store and query vectors
- **Query Processing**: Generate query embeddings and search
- **Context Assembly**: Format retrieved context for LLM

#### 4.2.4 ChromaDB
- **Vector Storage**: Store document embeddings
- **Similarity Search**: Perform vector similarity queries
- **Metadata Storage**: Store document metadata

### 4.3 Data Flow

#### 4.3.1 Voice Query Flow (with Function Calling)

```
1. User clicks microphone button
   ↓
2. Frontend requests microphone access
   ↓
3. Frontend → Backend: POST /api/realtime/session with SDP offer
   ↓
4. Backend → OpenAI API: Forward SDP to establish WebRTC session
   ↓
5. Backend → Frontend: Return SDP answer
   ↓
6. Frontend establishes WebRTC connection to OpenAI Realtime API
   ↓
7. User speaks → Frontend captures audio
   ↓
8. Frontend → WebRTC Data Channel → OpenAI Realtime API: Audio stream
   ↓
9. OpenAI API transcribes audio → Transcription event
   ↓
10. Model analyzes query and decides to call rag_knowledge function
    ↓
11. OpenAI API → Frontend: Function call event (via WebRTC data channel)
    ↓
12. Frontend → Backend: POST /api/rag/function-call with query
    ↓
13. Backend → RAG Service: HTTP POST with query text
    ↓
14. RAG Service → OpenAI Embeddings API: Generate query embedding
    ↓
15. RAG Service → ChromaDB: Vector similarity search
    ↓
16. RAG Service → Backend: Return retrieved context
    ↓
17. Backend → Frontend: HTTP response with function result context
    ↓
18. Frontend → OpenAI Realtime API: Function call output via data channel
    ↓
19. OpenAI API generates response using function result context
    ↓
20. OpenAI API → Frontend: Response audio stream via WebRTC
    ↓
21. Frontend: Play audio and display transcript
```

#### 4.3.2 Document Ingestion Flow

```
1. Admin uploads document via API endpoint
   ↓
2. RAG Service receives document
   ↓
3. Parse document (PDF/TXT/MD) → Extract text
   ↓
4. Chunk text into 500-1000 token chunks
   ↓
5. Generate embeddings for each chunk (OpenAI API)
   ↓
6. Store chunks + embeddings in ChromaDB
   ↓
7. Document available for queries
```

---

## 5. Functional Requirements

### 5.1 Voice Interaction

#### FR-POC-1: Session Initiation
- **FR-POC-1.1**: User can initiate a voice session by clicking microphone button
- **FR-POC-1.2**: System requests microphone permission if not granted
- **FR-POC-1.3**: System establishes WebRTC connection upon permission grant
- **FR-POC-1.4**: System displays "Ready" or "Listening" status

#### FR-POC-2: Audio Capture and Transmission
- **FR-POC-2.1**: System captures audio from user's microphone
- **FR-POC-2.2**: System streams audio to OpenAI Realtime API via WebRTC
- **FR-POC-2.3**: System displays audio input level indicator (optional)
- **FR-POC-2.4**: System detects end-of-speech (silence detection or manual stop)

#### FR-POC-3: Speech-to-Text
- **FR-POC-3.1**: System transcribes user speech to text using OpenAI Realtime API
- **FR-POC-3.2**: System displays transcription in real-time
- **FR-POC-3.3**: System handles transcription errors gracefully

#### FR-POC-4: Response Generation
- **FR-POC-4.1**: System retrieves relevant context from knowledge base via RAG
- **FR-POC-4.2**: System generates response using OpenAI API with context
- **FR-POC-4.3**: System displays response text in transcript
- **FR-POC-4.4**: System converts response to speech and plays audio

#### FR-POC-5: Session Management
- **FR-POC-5.1**: User can end session by clicking stop button
- **FR-POC-5.2**: System closes WebRTC connection on session end
- **FR-POC-5.3**: System clears session state (in-memory)

### 5.2 RAG Integration

#### FR-POC-6: Document Ingestion
- **FR-POC-6.1**: System accepts document uploads via REST API (PDF, TXT, MD)
- **FR-POC-6.2**: System parses documents and extracts text
- **FR-POC-6.3**: System chunks text into appropriate sizes
- **FR-POC-6.4**: System generates embeddings and stores in ChromaDB

#### FR-POC-7: Knowledge Retrieval
- **FR-POC-7.1**: System generates query embedding from user question
- **FR-POC-7.2**: System performs vector similarity search in ChromaDB
- **FR-POC-7.3**: System retrieves top-K relevant documents (K=5)
- **FR-POC-7.4**: System assembles context from retrieved documents
- **FR-POC-7.5**: System injects context into OpenAI prompt

### 5.3 User Interface

#### FR-POC-8: Core UI Components
- **FR-POC-8.1**: Microphone button (start/stop voice interaction)
- **FR-POC-8.2**: Status indicator (idle, listening, processing, speaking, error)
- **FR-POC-8.3**: Conversation transcript (user queries and system responses)
- **FR-POC-8.4**: Basic error messages displayed to user

#### FR-POC-9: User Feedback
- **FR-POC-9.1**: Visual feedback when system is listening
- **FR-POC-9.2**: Visual feedback when system is processing
- **FR-POC-9.3**: Visual feedback when system is speaking
- **FR-POC-9.4**: Error messages displayed when errors occur

---

## 6. Technical Implementation Details

### 6.1 WebRTC Implementation

#### 6.1.1 Signaling Protocol

**REST API Endpoints:**

```typescript
// Client → Server: POST /api/realtime/session
// Request body (Content-Type: application/sdp):
<SDP offer string>

// Query parameters:
// ?model=gpt-4o-realtime-preview-2024-12-17&voice=alloy

// Response:
// Status: 200 OK
// Headers:
//   X-Session-Config: { "session_id": "uuid", "model": "...", "voice": "..." }
// Body (application/sdp):
<SDP answer string>

// WebRTC connection is established directly between client and OpenAI
// No ICE candidate exchange needed (handled by OpenAI)
```

#### 6.1.2 STUN/TURN Configuration

**STUN Servers (Public):**
- `stun:stun.l.google.com:19302`
- `stun:stun1.l.google.com:19302`

**TURN Server (Optional for POC):**
- Self-hosted using `coturn` or cloud service
- Only needed if STUN fails (NAT traversal issues)

#### 6.1.3 Audio Configuration

- **Codec**: Opus (preferred) or VP8
- **Sample Rate**: 16 kHz (mono)
- **Bitrate**: 16-32 kbps
- **Channels**: Mono
- **Packetization**: 20ms packets

#### 6.1.4 SDP Exchange (Backend)

```python
# FastAPI REST endpoint for SDP exchange
@app.post("/api/realtime/session")
async def create_realtime_session(
    request: Request,
    model: str = "gpt-4o-realtime-preview-2024-12-17",
    voice: str = "alloy"
):
    # Read SDP offer from request body
    sdp_offer = await request.body()
    sdp_offer = sdp_offer.decode('utf-8')

    # Validate SDP format
    is_valid, error = validate_sdp_format(sdp_offer)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error)

    # Forward SDP to OpenAI Realtime API
    openai_url = f"{OPENAI_REALTIME_URL}?model={model}&voice={voice}"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/sdp"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(openai_url, content=sdp_offer, headers=headers)
        sdp_answer = response.text

    # Return SDP answer with session config in header
    session_id = str(uuid.uuid4())
    session_config = {"session_id": session_id, "model": model, "voice": voice}

    return Response(
        content=sdp_answer,
        media_type="application/sdp",
        headers={"X-Session-Config": json.dumps(session_config)}
    )
```

### 6.2 OpenAI Realtime API Integration

#### 6.2.1 WebRTC Connection to OpenAI

**Endpoint**: `POST https://api.openai.com/v1/realtime`

**Authentication**: Bearer token in Authorization header

**Connection Setup:**
The system establishes a WebRTC connection to OpenAI Realtime API:

1. Client generates SDP offer
2. Client sends SDP to backend via `POST /api/realtime/session`
3. Backend forwards SDP to OpenAI with API key
4. OpenAI returns SDP answer
5. Backend forwards answer to client
6. Client completes WebRTC connection with OpenAI directly
7. Audio streams and events flow via WebRTC data channel

#### 6.2.2 Event Handling

**Key Events:**
- `input_audio_buffer.speech_started` - User started speaking
- `input_audio_buffer.transcription.completed` - Transcription finished
- `response.audio_transcript.delta` - Audio chunk available
- `response.done` - Response complete
- `error` - Error occurred

**Event Processing (with Function Calling):**
```python
# Function calling is handled natively by OpenAI Realtime API
# The model decides when to call the rag_knowledge function

# Session configuration includes function definition
session_config = {
    "tools": [
        {
            "type": "function",
            "name": "rag_knowledge",
            "description": "Search and retrieve information from the knowledge base to answer user questions",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query"
                    }
                },
                "required": ["query"]
            }
        }
    ]
}

# Frontend handles function call events
async def handle_function_call(event):
    if event.type == "response.function_call_arguments.done":
        # Extract function call details
        call_id = event.call_id
        function_name = event.name
        arguments = JSON.parse(event.arguments)

        if (function_name === "rag_knowledge"):
            # Send function call to backend via REST API
            const response = await fetch(`${BACKEND_URL}/api/rag/function-call`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    type: "function_call",
                    call_id: call_id,
                    function_name: function_name,
                    arguments: arguments
                })
            })

            # Backend executes RAG query and returns result
            const result = await response.json()

            # Frontend sends result back to OpenAI via data channel
            await data_channel.send({
                "type": "conversation.item.create",
                "item": {
                    "type": "function_call_output",
                    "call_id": call_id,
                    "output": JSON.stringify(result.data)
                }
            })
```

#### 6.2.3 Audio Stream Flow

**Note**: Audio streaming happens directly via WebRTC between client and OpenAI.
Backend does NOT handle audio forwarding. The backend only:

1. Facilitates SDP exchange for WebRTC setup
2. Executes function calls (RAG queries) via REST API

```typescript
// Client-side WebRTC audio handling
const peerConnection = new RTCPeerConnection()

// Add local audio track
const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
stream.getTracks().forEach(track => {
    peerConnection.addTrack(track, stream)
})

// Receive remote audio from OpenAI
peerConnection.ontrack = (event) => {
    const audioElement = new Audio()
    audioElement.srcObject = event.streams[0]
    audioElement.play()
}
```

### 6.3 RAG Pipeline Implementation

#### 6.3.1 Document Ingestion API

```python
# RAG Service endpoint
@app.post("/api/documents/ingest")
async def ingest_document(file: UploadFile):
    # Parse document
    text = await parse_document(file)
    
    # Chunk text
    chunks = chunk_text(text, chunk_size=500, overlap=100)
    
    # Generate embeddings
    embeddings = await generate_embeddings(chunks)
    
    # Store in ChromaDB
    collection = chroma_client.get_or_create_collection("knowledge_base")
    collection.add(
        embeddings=embeddings,
        documents=chunks,
        metadatas=[{"source": file.filename}] * len(chunks),
        ids=[f"{file.filename}_{i}" for i in range(len(chunks))]
    )
    
    return {"status": "success", "chunks": len(chunks)}
```

#### 6.3.2 Query Processing

```python
@app.post("/api/rag/query")
async def process_query(query: str):
    # Generate query embedding
    query_embedding = await generate_embedding(query)
    
    # Search ChromaDB
    collection = chroma_client.get_collection("knowledge_base")
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=5
    )
    
    # Assemble context
    context = "\n\n".join([
        f"[Document {i+1}]\n{doc}"
        for i, doc in enumerate(results["documents"][0])
    ])
    
    return {
        "context": context,
        "sources": results["metadatas"][0]
    }
```

#### 6.3.3 ChromaDB Setup

```python
import chromadb

# Initialize ChromaDB client
chroma_client = chromadb.Client()

# Create or get collection
collection = chroma_client.get_or_create_collection(
    name="knowledge_base",
    metadata={"hnsw:space": "cosine"}  # Cosine similarity
)
```

### 6.4 Backend Integration

#### 6.4.1 RAG Service Client (Backend)

```python
import httpx

async def retrieve_context(query: str) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://rag-service:8000/api/rag/query",
            json={"query": query}
        )
        result = response.json()
        return result["context"]
```

#### 6.4.2 Function Calling for RAG Integration

```python
# Function calling approach - Model decides when to search knowledge base
# Function is registered in session configuration

# Backend handles function call execution
async def handle_function_call(call_id, function_name, arguments):
    if function_name == "rag_knowledge":
        query = arguments.get("query")
        
        # Retrieve context from RAG service
        context = await retrieve_context(query)
        
        # Return function result
        return {
            "success": True,
            "context": context,
            "sources": sources
        }

# Frontend receives function call from OpenAI and forwards to backend
# Frontend sends function result back to OpenAI
# Model uses function result to generate response
```

### 6.5 Frontend Implementation

#### 6.5.1 WebRTC Client Setup

```typescript
// Next.js component/hook
const useVoiceSession = () => {
  const [peerConnection, setPeerConnection] = useState<RTCPeerConnection | null>(null);
  const [dataChannel, setDataChannel] = useState<RTCDataChannel | null>(null);

  const startSession = async () => {
    // Get user media
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

    // Create peer connection
    const pc = new RTCPeerConnection();

    // Add audio track
    stream.getTracks().forEach(track => {
      pc.addTrack(track, stream);
    });

    // Handle incoming audio
    pc.ontrack = (event) => {
      const audioElement = new Audio();
      audioElement.srcObject = event.streams[0];
      audioElement.play();
    };

    // Create data channel for OpenAI events
    const dc = pc.createDataChannel('oai-events');
    dc.onmessage = (event) => {
      const openaiEvent = JSON.parse(event.data);
      handleOpenAIEvent(openaiEvent);
    };

    // Create SDP offer
    const offer = await pc.createOffer();
    await pc.setLocalDescription(offer);

    // Send SDP to backend via REST API
    const response = await fetch(`${BACKEND_URL}/api/realtime/session?model=gpt-4o-realtime-preview-2024-12-17&voice=alloy`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/sdp' },
      body: offer.sdp
    });

    // Get SDP answer
    const answerSdp = await response.text();
    await pc.setRemoteDescription({
      type: 'answer',
      sdp: answerSdp
    });

    setPeerConnection(pc);
    setDataChannel(dc);
  };

  return { startSession, peerConnection, dataChannel };
};
```

#### 6.5.2 UI Components

```typescript
// components/MicrophoneButton.tsx
export default function MicrophoneButton() {
  const [isListening, setIsListening] = useState(false);
  const { startSession } = useVoiceSession();
  
  const handleClick = async () => {
    if (!isListening) {
      await startSession();
      setIsListening(true);
    } else {
      // Stop session
      setIsListening(false);
    }
  };
  
  return (
    <button onClick={handleClick}>
      {isListening ? 'Stop' : 'Start'} Voice
    </button>
  );
}
```

```typescript
// components/Transcript.tsx
export default function Transcript({ messages }: { messages: Message[] }) {
  return (
    <div>
      {messages.map((msg, i) => (
        <div key={i} className={msg.role === 'user' ? 'user-msg' : 'assistant-msg'}>
          {msg.text}
        </div>
      ))}
    </div>
  );
}
```

---

## 7. UI/UX Requirements

### 7.1 Minimum Functional UI Components

#### 7.1.1 Microphone Button
- **Purpose**: Start/stop voice interaction
- **States**: 
  - Idle (default): "Start Voice" or microphone icon
  - Listening: "Listening..." with visual indicator (e.g., pulsing)
  - Processing: "Processing..." with spinner
  - Speaking: "Speaking..." indicator
  - Error: "Error" with error icon
- **Interaction**: Click to toggle
- **Visual**: Large, prominent button (minimum 60x60px)

#### 7.1.2 Status Indicator
- **Purpose**: Show current system state
- **Display**: Text label + optional icon
- **States**: Idle, Listening, Processing, Speaking, Error
- **Position**: Near microphone button or top of page

#### 7.1.3 Conversation Transcript
- **Purpose**: Display user queries and system responses
- **Layout**: 
  - User messages: Right-aligned or distinct styling
  - System messages: Left-aligned or distinct styling
  - Timestamps: Optional (can be hidden for POC)
- **Features**:
  - Auto-scroll to latest message
  - Basic text formatting
- **Styling**: Minimal but readable

#### 7.1.4 Error Messages
- **Purpose**: Inform user of errors
- **Display**: Alert-style message (red text or alert box)
- **Content**: Clear error description
- **Position**: Top of page or inline with relevant component

### 7.2 Layout Structure

```
┌─────────────────────────────────────┐
│         Header/Title                │
├─────────────────────────────────────┤
│                                     │
│      [Microphone Button]            │
│      Status: Listening              │
│                                     │
├─────────────────────────────────────┤
│                                     │
│  Transcript:                        │
│  ┌─────────────────────────────┐   │
│  │ User: What is...            │   │
│  │ Assistant: Based on...      │   │
│  │ User: Can you tell me...    │   │
│  │ Assistant: ...              │   │
│  └─────────────────────────────┘   │
│                                     │
└─────────────────────────────────────┘
```

### 7.3 Styling Guidelines

- **Minimal Styling**: Focus on functionality over aesthetics
- **Readable Fonts**: System fonts or basic web fonts
- **Color Scheme**: 
  - Primary action: Blue or brand color
  - Success/Active: Green
  - Error: Red
  - Text: Dark gray/black on white
- **Spacing**: Adequate padding for clickability
- **Responsive**: Basic responsive design (works on desktop and tablet)

### 7.4 User Interactions

1. **Start Session**: Click microphone button → Request permission → Start recording
2. **Speak**: User speaks naturally → System transcribes → System responds
3. **Stop Session**: Click stop button → End session
4. **View Transcript**: Scroll through conversation history
5. **Handle Errors**: Error message displayed → User can retry

---

## 8. Success Criteria

### 8.1 Functional Success Criteria

1. ✅ **Voice Session Works**: User can start a session and speak
2. ✅ **Transcription Works**: User speech is transcribed accurately
3. ✅ **RAG Retrieval Works**: System retrieves relevant context from knowledge base
4. ✅ **Response Generation Works**: System generates and speaks response
5. ✅ **Multi-Turn Conversation**: System handles at least 5 consecutive turns
6. ✅ **Error Handling**: Basic errors don't crash the system

### 8.2 Performance Criteria (Relaxed for POC)

- **End-to-End Latency**: < 2 seconds (from speech end to response start)
- **Transcription Latency**: < 500ms
- **RAG Retrieval Latency**: < 300ms
- **Response Generation**: < 1 second

### 8.3 Quality Criteria

- **Transcription Accuracy**: > 80% word accuracy (subjective)
- **Response Relevance**: Responses should reference knowledge base when relevant
- **Audio Quality**: Audio playback is clear and understandable
- **System Stability**: No crashes during 10-minute test session

### 8.4 Technical Validation

- ✅ WebRTC connection establishes successfully
- ✅ Audio streams bidirectionally
- ✅ OpenAI Realtime API integration works
- ✅ ChromaDB queries return relevant results
- ✅ Function calling enables intelligent knowledge base search
- ✅ System handles basic error scenarios

---

## 9. Implementation Phases

### Phase 1: Project Setup and Infrastructure (Week 1)

**Deliverables:**
- Project structure created (frontend, backend, rag-service)
- Docker Compose setup with ChromaDB
- Basic Next.js app running
- Basic FastAPI backend running
- Environment configuration

**Tasks:**
1. Initialize Next.js project with TypeScript
2. Initialize FastAPI backend project
3. Initialize RAG service project
4. Create Docker Compose file with ChromaDB
5. Set up environment variables and configuration
6. Create basic project structure and folders

### Phase 2: WebRTC Signaling and Connection (Week 1-2)

**Deliverables:**
- REST API signaling endpoints in backend
- WebRTC peer connection establishment
- Basic audio streaming (client ↔ OpenAI via WebRTC)

**Tasks:**
1. Implement REST endpoint for SDP exchange in FastAPI
2. Implement SDP offer/answer forwarding to OpenAI
3. Test peer connection establishment
4. Verify direct WebRTC connection (client ↔ OpenAI)
5. Implement data channel for OpenAI events

### Phase 3: OpenAI Realtime API Integration (Week 2)

**Deliverables:**
- OpenAI Realtime API WebRTC connection
- Audio streaming directly between client and OpenAI
- Basic transcription display

**Tasks:**
1. Set up WebRTC connection to OpenAI Realtime API
2. Handle audio streaming via WebRTC (no backend forwarding)
3. Implement data channel event handling
4. Handle transcription events from data channel
5. Display transcription in UI

### Phase 4: RAG Pipeline Implementation (Week 2-3)

**Deliverables:**
- Document ingestion API
- ChromaDB integration
- Query processing API
- Context retrieval working

**Tasks:**
1. Implement document parsing (PDF, TXT, MD)
2. Implement text chunking
3. Implement embedding generation
4. Set up ChromaDB collection
5. Implement vector similarity search
6. Create query processing endpoint

### Phase 5: RAG Integration with Voice Flow (Week 3)

**Deliverables:**
- RAG service called from backend
- Function calling integrated for RAG queries
- Knowledge-grounded responses working

**Tasks:**
1. Integrate RAG service client in backend
2. Model calls rag_knowledge function when needed
3. Function executes RAG query and returns context to model
4. Test end-to-end flow with knowledge base

### Phase 6: UI Implementation (Week 3-4)

**Deliverables:**
- Microphone button component
- Status indicator
- Transcript display
- Basic error handling UI

**Tasks:**
1. Create microphone button component
2. Implement status state management
3. Create transcript component
4. Add error message display
5. Basic styling and layout

### Phase 7: End-to-End Integration and Testing (Week 4)

**Deliverables:**
- Complete end-to-end flow working
- Error handling implemented
- Basic testing completed
- Documentation

**Tasks:**
1. Test complete voice interaction flow
2. Test multi-turn conversations
3. Test error scenarios
4. Fix bugs and issues
5. Create README and setup documentation

### Phase 8: POC Demo Preparation (Week 4)

**Deliverables:**
- Working POC demo
- Sample knowledge base documents
- Demo script
- Known issues document

**Tasks:**
1. Prepare sample documents for knowledge base
2. Test demo scenarios
3. Create demo script
4. Document known limitations
5. Prepare presentation materials

---

## 10. Appendices

### 10.1 Project Structure

```
rag-based-voice-assistant-poc/
├── frontend/                    # Next.js application
│   ├── app/
│   │   ├── page.tsx            # Main page
│   │   └── layout.tsx           # Root layout
│   ├── components/
│   │   ├── MicrophoneButton.tsx
│   │   ├── Transcript.tsx
│   │   ├── StatusIndicator.tsx
│   │   └── ErrorMessage.tsx
│   ├── hooks/
│   │   └── useVoiceSession.ts  # Main voice session hook
│   ├── constants/              # Frontend constants
│   │   ├── timing.ts
│   │   ├── tools.ts            # Function definitions
│   │   └── api.ts
│   ├── types/                  # TypeScript type definitions
│   │   ├── session.ts
│   │   └── openai.ts
│   ├── utils/                  # Utility functions
│   │   ├── functionCalls.ts
│   │   └── webrtc.ts
│   ├── package.json
│   └── next.config.js
│
├── backend/                     # FastAPI backend
│   ├── app/
│   │   ├── main.py             # FastAPI app
│   │   ├── config.py           # Configuration
│   │   ├── routes/
│   │   │   ├── realtime.py     # SDP forwarding endpoint
│   │   │   └── rag.py          # REST API for function calls
│   │   ├── services/
│   │   │   └── rag_client.py   # RAG service HTTP client
│   │   ├── constants/          # Backend constants
│   │   └── utils/              # Utility functions
│   ├── requirements.txt
│   └── Dockerfile
│
├── rag-service/                 # RAG service (FastAPI)
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py           # Configuration
│   │   ├── routes/
│   │   │   ├── documents.py    # Document ingestion
│   │   │   └── rag.py          # RAG query endpoint
│   │   ├── services/
│   │   │   ├── embedding_service.py
│   │   │   ├── chromadb_service.py
│   │   │   └── document_service.py
│   │   ├── models/
│   │   │   └── schemas.py      # Pydantic models
│   │   ├── constants/          # RAG constants
│   │   └── utils/              # Utility functions
│   ├── requirements.txt
│   └── Dockerfile
│
├── docker-compose.yml
├── .env.example
└── README.md
```

### 10.2 Environment Variables

```bash
# Backend
OPENAI_API_KEY=sk-...
BACKEND_PORT=8000
RAG_SERVICE_URL=http://rag-service:8000

# RAG Service
CHROMADB_HOST=chromadb
CHROMADB_PORT=8000
OPENAI_API_KEY=sk-...

# Frontend
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

### 10.3 Key Dependencies

#### Frontend (package.json)
```json
{
  "dependencies": {
    "next": "^14.0.0",
    "react": "^18.0.0",
    "react-dom": "^18.0.0"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "@types/react": "^18.0.0",
    "typescript": "^5.0.0",
    "tailwindcss": "^3.0.0"
  }
}
```

#### Backend (requirements.txt)
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
openai==1.3.0
httpx==0.25.0
python-dotenv==1.0.0
pydantic==2.5.0
```

#### RAG Service (requirements.txt)
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
chromadb==0.4.18
openai==1.3.0
pypdf2==3.0.1
python-docx==1.1.0
markdown==3.5.1
python-dotenv==1.0.0
```

### 10.4 Docker Compose Configuration

```yaml
version: '3.8'

services:
  chromadb:
    image: chromadb/chroma:latest
    ports:
      - "8000:8000"
    volumes:
      - chroma_data:/chroma/chroma
    environment:
      - IS_PERSISTENT=TRUE
      - PERSIST_DIRECTORY=/chroma/chroma

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - RAG_SERVICE_URL=http://rag-service:8000
    depends_on:
      - rag-service
    volumes:
      - ./backend:/app

  rag-service:
    build: ./rag-service
    ports:
      - "8001:8000"
    environment:
      - CHROMADB_HOST=chromadb
      - CHROMADB_PORT=8000
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      - chromadb
    volumes:
      - ./rag-service:/app

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
    volumes:
      - ./frontend:/app
      - /app/node_modules

volumes:
  chroma_data:
```

### 10.5 API Endpoints

#### Backend Endpoints
- `POST /api/realtime/session` - Create OpenAI Realtime session (SDP forwarding)
- `POST /api/rag/function-call` - RAG function call execution via REST API
- `GET /health` - Health check

#### RAG Service Endpoints
- `POST /api/documents/ingest` - Upload and ingest document
- `POST /api/rag/query` - Process query and retrieve context
- `GET /health` - Health check

### 10.6 Known Limitations and Future Work

**POC Limitations:**
1. Single session at a time (can extend to 5-10 for testing)
2. No persistent storage (sessions lost on restart)
3. Basic error handling (not comprehensive)
4. No authentication/authorization
5. No rate limiting
6. Basic UI (not production-ready)
7. Limited document format support

**Future Enhancements:**
1. Add Redis for session persistence
2. Implement user authentication
3. Add comprehensive error handling
4. Implement rate limiting
5. Add monitoring and logging
6. Improve UI/UX
7. Add more document format support
8. Implement conversation history
9. Add admin dashboard
10. Scale to multiple concurrent sessions

---

**Document End**

