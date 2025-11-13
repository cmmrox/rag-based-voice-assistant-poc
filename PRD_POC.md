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
- **WebSocket:** Native WebSocket API for signaling
- **State Management:** React Context API + useState/useEffect hooks

**Key Libraries:**
- `next` - Next.js framework
- `react` - React library
- `react-dom` - React DOM rendering
- `tailwindcss` - Utility-first CSS framework (optional, minimal)

### 2.2 Backend

**Framework:** FastAPI (Python 3.11+)
- **Language:** Python 3.11+
- **WebSocket:** FastAPI WebSocket support
- **HTTP Client:** `httpx` or `aiohttp` for async HTTP requests
- **OpenAI Integration:** `openai` Python SDK
- **WebRTC Signaling:** Custom WebSocket server using FastAPI

**Key Libraries:**
- `fastapi` - Modern Python web framework
- `uvicorn` - ASGI server
- `websockets` - WebSocket support
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
- ✅ Context injection into OpenAI prompts

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
│  │  WebSocket Client:                                    │   │
│  │  - Signaling for WebRTC                              │   │
│  │  - Session management                                 │   │
│  └──────────────┬────────────────────────────────────────┘   │
└─────────────────┼────────────────────────────────────────────┘
                  │ WebSocket (signaling)
                  │ WebRTC (audio stream)
                  │
┌─────────────────▼────────────────────────────────────────────┐
│              Backend (FastAPI)                                 │
│  ┌──────────────────────────────────────────────────────┐     │
│  │  WebSocket Signaling Server                          │     │
│  │  - WebRTC offer/answer exchange                     │     │
│  │  - ICE candidate exchange                            │     │
│  │  - Session state management                          │     │
│  └──────────────┬───────────────────────────────────────┘     │
│                 │                                              │
│  ┌──────────────▼───────────────────────────────────────┐     │
│  │  WebRTC Peer Connection Handler                      │     │
│  │  - Audio stream routing                              │     │
│  │  - Client ↔ OpenAI audio forwarding                 │     │
│  └──────────────┬───────────────────────────────────────┘     │
│                 │                                              │
│  ┌──────────────▼───────────────────────────────────────┐     │
│  │  OpenAI Realtime API Gateway                        │     │
│  │  - WebSocket to OpenAI API                          │     │
│  │  - Audio stream forwarding                          │     │
│  │  - Event handling (transcription, response)         │     │
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
│  OpenAI Realtime API (wss://api.openai.com/v1/realtime)   │
│  OpenAI Embeddings API (https://api.openai.com/v1/...)     │
│  STUN Servers (public)                                      │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 Component Responsibilities

#### 4.2.1 Frontend (Next.js)
- **Audio Capture**: Use MediaRecorder API to capture microphone audio
- **WebRTC Client**: Establish peer connection with backend
- **Audio Playback**: Play received audio using Web Audio API
- **UI Rendering**: Display microphone button, transcript, status
- **WebSocket Client**: Handle signaling for WebRTC setup
- **State Management**: Manage session state, transcript, status

#### 4.2.2 Backend (FastAPI)
- **WebSocket Signaling Server**: Handle WebRTC offer/answer/ICE exchange
- **WebRTC Peer Connection**: Manage peer connection with client
- **Audio Routing**: Forward audio between client and OpenAI API
- **OpenAI Gateway**: Maintain WebSocket connection to OpenAI Realtime API
- **Event Processing**: Handle transcription and response events
- **RAG Integration**: Call RAG service to retrieve context
- **Session Management**: Track active sessions (in-memory)

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

#### 4.3.1 Voice Query Flow

```
1. User clicks microphone button
   ↓
2. Frontend requests microphone access
   ↓
3. Frontend establishes WebSocket connection to backend
   ↓
4. Backend creates WebRTC offer
   ↓
5. Frontend receives offer, creates answer, exchanges ICE candidates
   ↓
6. WebRTC peer connection established
   ↓
7. User speaks → Frontend captures audio
   ↓
8. Frontend → WebRTC → Backend: Audio stream
   ↓
9. Backend → OpenAI Realtime API: Forward audio stream
   ↓
10. OpenAI API → Backend: Transcription event (text)
    ↓
11. Backend → RAG Service: HTTP POST with query text
    ↓
12. RAG Service → OpenAI Embeddings API: Generate query embedding
    ↓
13. RAG Service → ChromaDB: Vector similarity search
    ↓
14. RAG Service → Backend: Return retrieved context
    ↓
15. Backend → OpenAI Realtime API: Inject context + generate response
    ↓
16. OpenAI API → Backend: Response text + audio stream
    ↓
17. Backend → WebRTC → Frontend: Audio stream
    ↓
18. Frontend: Play audio and display transcript
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
- **FR-POC-2.2**: System streams audio to backend via WebRTC
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

**WebSocket Messages:**

```typescript
// Client → Server: Request session
{
  "type": "session_request",
  "session_id": "optional-uuid"
}

// Server → Client: WebRTC offer
{
  "type": "offer",
  "sdp": "...",
  "session_id": "uuid"
}

// Client → Server: WebRTC answer
{
  "type": "answer",
  "sdp": "...",
  "session_id": "uuid"
}

// Client ↔ Server: ICE candidates
{
  "type": "ice_candidate",
  "candidate": "...",
  "session_id": "uuid"
}

// Server → Client: Session ready
{
  "type": "session_ready",
  "session_id": "uuid"
}
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

#### 6.1.4 Peer Connection Setup (Backend)

```python
# FastAPI WebSocket endpoint for signaling
@app.websocket("/ws/signaling")
async def websocket_signaling(websocket: WebSocket):
    await websocket.accept()
    
    # Create RTCPeerConnection
    pc = RTCPeerConnection()
    
    # Handle incoming audio stream
    @pc.on("track")
    def on_track(track):
        if track.kind == "audio":
            # Forward to OpenAI Realtime API
            forward_audio_to_openai(track)
    
    # Handle WebRTC signaling messages
    while True:
        message = await websocket.receive_json()
        # Process offer/answer/ICE candidates
```

### 6.2 OpenAI Realtime API Integration

#### 6.2.1 WebSocket Connection

**Endpoint**: `wss://api.openai.com/v1/realtime`

**Authentication**: Bearer token in connection header

**Connection Setup:**
```python
import openai

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Create session
session = client.beta.realtime.connect(
    model="gpt-4o-realtime-preview-2024-10-01",
    voice="alloy",
    instructions="You are a helpful voice assistant..."
)
```

#### 6.2.2 Event Handling

**Key Events:**
- `input_audio_buffer.speech_started` - User started speaking
- `input_audio_buffer.transcription.completed` - Transcription finished
- `response.audio_transcript.delta` - Audio chunk available
- `response.done` - Response complete
- `error` - Error occurred

**Event Processing:**
```python
async def handle_openai_events(session):
    async for event in session:
        if event.type == "input_audio_buffer.transcription.completed":
            query_text = event.transcript
            # Trigger RAG retrieval
            context = await retrieve_context(query_text)
            # Inject context into session
            session.submit(
                type="conversation.item.create",
                item={
                    "type": "message",
                    "role": "user",
                    "content": query_text
                }
            )
            # Add context to system message
            session.update(
                instructions=f"Context: {context}\n\n{base_instructions}"
            )
```

#### 6.2.3 Audio Stream Forwarding

```python
# Forward WebRTC audio to OpenAI
async def forward_audio_to_openai(audio_track):
    async for audio_chunk in audio_track:
        # Convert to format expected by OpenAI
        audio_data = process_audio_chunk(audio_chunk)
        # Send to OpenAI Realtime API
        session.submit(
            type="input_audio_buffer.append",
            audio=audio_data
        )

# Forward OpenAI audio to WebRTC
async def forward_openai_audio_to_client(session, peer_connection):
    async for event in session:
        if event.type == "response.audio_transcript.delta":
            audio_data = event.delta
            # Send to WebRTC peer connection
            send_audio_to_peer(peer_connection, audio_data)
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

#### 6.4.2 Context Injection

```python
# When transcription completes
if event.type == "input_audio_buffer.transcription.completed":
    query = event.transcript
    
    # Retrieve context
    context = await retrieve_context(query)
    
    # Update session instructions with context
    session.update(
        instructions=f"""
        You are a helpful voice assistant. Use the following context to answer questions.
        
        Context:
        {context}
        
        If the context doesn't contain relevant information, say so.
        """
    )
    
    # Submit user query
    session.submit(
        type="conversation.item.create",
        item={
            "type": "message",
            "role": "user",
            "content": query
        }
    )
```

### 6.5 Frontend Implementation

#### 6.5.1 WebRTC Client Setup

```typescript
// Next.js component/hook
const useVoiceSession = () => {
  const [peerConnection, setPeerConnection] = useState<RTCPeerConnection | null>(null);
  const [ws, setWs] = useState<WebSocket | null>(null);
  
  const startSession = async () => {
    // Get user media
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    
    // Create peer connection
    const pc = new RTCPeerConnection({
      iceServers: [
        { urls: 'stun:stun.l.google.com:19302' }
      ]
    });
    
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
    
    // WebSocket for signaling
    const websocket = new WebSocket('ws://localhost:8000/ws/signaling');
    
    // Handle offer
    websocket.onmessage = async (event) => {
      const message = JSON.parse(event.data);
      if (message.type === 'offer') {
        await pc.setRemoteDescription(new RTCSessionDescription(message));
        const answer = await pc.createAnswer();
        await pc.setLocalDescription(answer);
        websocket.send(JSON.stringify({
          type: 'answer',
          sdp: answer.sdp
        }));
      }
    };
    
    setPeerConnection(pc);
    setWs(websocket);
  };
  
  return { startSession, peerConnection };
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
- ✅ Context injection improves response quality
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
- WebSocket signaling server in backend
- WebRTC peer connection establishment
- Basic audio streaming (client ↔ backend)

**Tasks:**
1. Implement WebSocket server in FastAPI
2. Implement WebRTC offer/answer exchange
3. Implement ICE candidate exchange
4. Test peer connection establishment
5. Implement basic audio forwarding (echo test)

### Phase 3: OpenAI Realtime API Integration (Week 2)

**Deliverables:**
- OpenAI Realtime API WebSocket connection
- Audio forwarding (backend ↔ OpenAI)
- Basic transcription display

**Tasks:**
1. Set up OpenAI Realtime API connection
2. Forward audio from WebRTC to OpenAI
3. Forward audio from OpenAI to WebRTC
4. Handle transcription events
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
- Context injected into OpenAI prompts
- Knowledge-grounded responses working

**Tasks:**
1. Integrate RAG service client in backend
2. Call RAG service on transcription completion
3. Inject context into OpenAI session
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
voice-assistant-poc/
├── frontend/                    # Next.js application
│   ├── app/
│   │   ├── page.tsx            # Main page
│   │   └── layout.tsx           # Root layout
│   ├── components/
│   │   ├── MicrophoneButton.tsx
│   │   ├── Transcript.tsx
│   │   └── StatusIndicator.tsx
│   ├── hooks/
│   │   └── useVoiceSession.ts
│   ├── lib/
│   │   └── websocket.ts
│   ├── package.json
│   └── next.config.js
│
├── backend/                     # FastAPI backend
│   ├── app/
│   │   ├── main.py             # FastAPI app
│   │   ├── routes/
│   │   │   └── websocket.py    # WebSocket routes
│   │   ├── services/
│   │   │   ├── webrtc.py       # WebRTC handling
│   │   │   ├── openai_gateway.py
│   │   │   └── rag_client.py
│   │   └── models/
│   │       └── session.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── rag-service/                 # RAG service (FastAPI)
│   ├── app/
│   │   ├── main.py
│   │   ├── routes/
│   │   │   ├── documents.py
│   │   │   └── query.py
│   │   ├── services/
│   │   │   ├── embedding.py
│   │   │   ├── chromadb_service.py
│   │   │   └── document_parser.py
│   │   └── models/
│   │       └── schemas.py
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
NEXT_PUBLIC_WS_URL=ws://localhost:8000
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
websockets==12.0
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
      - NEXT_PUBLIC_WS_URL=ws://localhost:8000
    volumes:
      - ./frontend:/app
      - /app/node_modules

volumes:
  chroma_data:
```

### 10.5 API Endpoints

#### Backend Endpoints
- `WS /ws/signaling` - WebSocket signaling for WebRTC
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

