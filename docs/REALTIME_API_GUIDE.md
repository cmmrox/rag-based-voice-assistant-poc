# Complete OpenAI Realtime API with Function Calling Guide

This guide explains how the OpenAI Realtime API works with function calling, based on the actual implementation in this codebase.

## Table of Contents
1. [WebRTC Initialization & SDP Exchange](#1-webrtc-initialization--sdp-exchange)
2. [Custom Function Registration](#2-custom-function-registration)
3. [Complete Function Call Flow](#3-complete-function-call-flow)
4. [Communication Protocols](#4-communication-protocols)
5. [Realtime API Events](#5-realtime-api-events)
6. [Critical Implementation Details](#6-critical-implementation-details)

---

## 1. WebRTC Initialization & SDP Exchange

### What is SDP?

**SDP (Session Description Protocol)** is a format used to describe multimedia communication sessions. Think of it as a "connection contract" between two peers that contains:

- **Media types** (audio/video)
- **Codecs supported** (what audio/video formats each side can handle)
- **Network transport addresses** (IP addresses and ports)
- **Session attributes** (encryption, bandwidth, etc.)

In WebRTC, both sides exchange SDP to negotiate and agree on how they'll communicate.

### The Connection Flow

```
Frontend                  Backend                   OpenAI
   |                         |                         |
   |--1. Create Offer SDP--->|                         |
   |                         |--2. Forward SDP-------->|
   |                         |                         |
   |                         |<--3. Answer SDP---------|
   |<--4. Return Answer------|                         |
   |                         |                         |
   |==5. WebRTC Connection Established================>|
   |                         |                         |
```

### Implementation Code

**Location:** `frontend/hooks/useVoiceSession.ts:400-515`

```typescript
// Step 1: Get user's microphone
const stream = await getUserAudioStream();

// Step 2: Create RTCPeerConnection (no STUN servers needed - OpenAI handles it)
const peerConnection = new RTCPeerConnection();

// Step 3: Set up audio playback for OpenAI's voice
const audioElement = createAudioElement();
peerConnection.ontrack = (event) => {
  handleIncomingTrack(event, audioElement);
};

// Step 4: Add microphone track to connection
addAudioTracks(peerConnection, stream);

// Step 5: Create data channel for events (CRITICAL!)
// This is how OpenAI sends function calls, transcriptions, etc.
const dataChannel = peerConnection.createDataChannel('oai-events');

// Step 6: Create SDP offer
const offer = await peerConnection.createOffer();
await peerConnection.setLocalDescription(offer);

// Step 7: Send SDP to backend for forwarding to OpenAI
const sdpResponse = await fetch(`${BACKEND_URL}/api/realtime/session`, {
  method: 'POST',
  body: offer.sdp,  // Raw SDP text
  headers: {
    'Content-Type': 'application/sdp',  // MUST be application/sdp
  },
});

// Step 8: Get OpenAI's SDP answer and complete the connection
const answerSdp = await sdpResponse.text();
await peerConnection.setRemoteDescription(
  new RTCSessionDescription({ type: 'answer', sdp: answerSdp })
);

// Now WebRTC connection is established!
// - Audio flows directly between browser and OpenAI
// - Data channel receives events from OpenAI
```

### Backend SDP Forwarding

**Location:** `backend/app/routes/realtime.py:14-174`

The backend acts as a proxy to hide your OpenAI API key from the frontend.

```python
@router.post("/realtime/session")
async def create_realtime_session(request: Request):
    # Get SDP from frontend
    sdp = await request.body()
    sdp_text = sdp.decode('utf-8')

    # Validate SDP format (must contain version and media sections)
    if "v=0" not in sdp_text or "m=" not in sdp_text:
        return Response(content=json.dumps({"error": "Invalid SDP format"}))

    # Configure OpenAI request
    model = "gpt-4o-realtime-preview-2024-10-01"
    voice = "marin"

    # Build URL with query parameters
    # IMPORTANT: Model and voice MUST be query params, not in SDP body
    base_url = "https://api.openai.com/v1/realtime/calls"
    query_params = {"model": model, "voice": voice}
    url = f"{base_url}?{urllib.parse.urlencode(query_params)}"

    # Forward to OpenAI with correct headers
    headers = {
        "Authorization": f"Bearer {settings.openai_api_key}",
        "Content-Type": "application/sdp",  # CRITICAL!
    }

    # Send to OpenAI and return answer
    response = await client.post(url, headers=headers, content=sdp_text.encode('utf-8'))
    answer_sdp = response.text

    return PlainTextResponse(content=answer_sdp, media_type="application/sdp")
```

**Key Points:**
- ✅ SDP MUST be sent with `Content-Type: application/sdp`
- ✅ Model and voice are query parameters, NOT in the SDP body
- ✅ Backend acts as a proxy to hide the OpenAI API key
- ✅ OpenAI returns SDP answer which completes the WebRTC handshake
- ✅ No STUN/TURN servers needed - OpenAI handles NAT traversal

---

## 2. Custom Function Registration

### When Does Registration Happen?

Functions are registered **AFTER** the WebRTC connection is established, specifically when the `session.created` event is received from OpenAI.

**Location:** `frontend/hooks/useVoiceSession.ts:298-321`

```typescript
const handleDataChannelMessage = useCallback(async (event: MessageEvent) => {
  const eventData = JSON.parse(event.data);

  // Registration happens AFTER session.created event
  if (eventData.type === 'session.created' && !functionRegisteredRef.current) {
    console.log('[RAG] Session created, registering rag_knowledge function');

    // Small delay to ensure data channel is fully ready
    setTimeout(() => {
      if (dataChannelRef.current && dataChannelRef.current.readyState === 'open') {
        const sessionUpdate = {
          type: 'session.update',
          event_id: crypto.randomUUID(),  // REQUIRED!
          session: {
            type: 'realtime',
            tools: [RAG_KNOWLEDGE_TOOL],  // Function definition
            tool_choice: 'auto',           // Let AI decide when to call
          },
        };
        dataChannelRef.current.send(JSON.stringify(sessionUpdate));
        functionRegisteredRef.current = true;
      }
    }, EVENT_PROCESSING_DELAY_MS);  // 100ms delay
  }
});
```

### Function Definition Format

Functions must follow the OpenAI function calling schema (same as Chat Completions API).

**Location:** `frontend/constants/tools.ts`

```typescript
export const RAG_KNOWLEDGE_TOOL = {
  type: 'function' as const,
  name: 'rag_knowledge',
  description: 'Search and retrieve information from the knowledge base. Use this when the user asks questions that require specific information from documents or data sources.',
  parameters: {
    type: 'object',
    properties: {
      query: {
        type: 'string',
        description: 'The search query to find relevant information in the knowledge base',
      },
    },
    required: ['query'],
  },
};
```

**Format Requirements:**
- `type` must be `'function'`
- `name` is the function identifier (alphanumeric + underscores)
- `description` tells the AI **when** and **why** to use this function
- `parameters` follows [JSON Schema](https://json-schema.org/) format
- `required` array specifies mandatory parameters

### How OpenAI Knows About Your Function

1. You register the function via `session.update` event
2. OpenAI stores the function definition in the session
3. When the user speaks, OpenAI analyzes the request
4. If the request needs information from your knowledge base, OpenAI decides to call `rag_knowledge`
5. OpenAI extracts the search query from the user's speech
6. OpenAI sends a function call event via the data channel

**The AI decides when to call your function based on the description you provide!**

---

## 3. Complete Function Call Flow

### Visual Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│ 1. User speaks: "What is in the documentation?"                    │
└─────────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────────┐
│ 2. OpenAI processes speech and decides to call rag_knowledge       │
│    (based on function description)                                  │
└─────────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────────┐
│ 3. OpenAI sends function call via WebRTC data channel              │
│    Event: response.function_call_arguments.done                     │
│    Data: { name: "rag_knowledge", arguments: '{"query":"docs"}' }  │
└─────────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────────┐
│ 4. Frontend detects function call and extracts call_id + arguments │
└─────────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────────┐
│ 5. Frontend sends to Backend via REST API POST                     │
│    Endpoint: POST /api/rag/function-call                            │
│    Body: { type: "function_call", call_id, function_name, args }   │
└─────────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────────┐
│ 6. Backend queries RAG service via HTTP POST                       │
│    Endpoint: POST /api/rag/query                                    │
│    Body: { query: "docs" }                                          │
└─────────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────────┐
│ 7. RAG service searches ChromaDB and returns context               │
│    Response: { context: "...", sources: [...] }                    │
└─────────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────────┐
│ 8. Backend returns results in HTTP response                        │
│    Response: { type: "function_call_result", call_id, result }     │
└─────────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────────┐
│ 9. Frontend sends function output to OpenAI via data channel       │
│    Event: conversation.item.create (type: function_call_output)    │
└─────────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────────┐
│ 10. Frontend creates new response                                   │
│     Event: response.create                                          │
└─────────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────────┐
│ 11. OpenAI formulates answer using context and speaks to user      │
│     "Based on the documentation, ..."                               │
└─────────────────────────────────────────────────────────────────────┘
```

### Step 3-4: Function Call Detection (CRITICAL!)

**Why Early Detection Matters:**
- OpenAI sends function calls via `response.function_call_arguments.done` event
- This fires **BEFORE** `response.done` event
- If you wait for `response.done`, the `item_id` may be invalid
- Result: "Tool call ID not found in conversation" error

**Location:** `frontend/hooks/useVoiceSession.ts:126-159`

```typescript
const handleFunctionCall = useCallback((eventData: any) => {
  // HIGHEST PRIORITY - EARLIEST DETECTION
  // This fires when arguments are complete but BEFORE response.done
  if (eventData.type === 'response.function_call_arguments.done') {
    if (eventData.name === 'rag_knowledge') {
      // Validate arguments are valid JSON
      try {
        if (eventData.arguments && typeof eventData.arguments === 'string') {
          const parsedArgs = JSON.parse(eventData.arguments);

          if (parsedArgs && Object.keys(parsedArgs).length > 0) {
            console.log('[RAG] ✓✓✓ Found function call with VALID arguments');
            detectedFunctionCall = eventData;  // Process this!
          }
        }
      } catch (parseError) {
        // Arguments not ready yet, fallback to response.done
      }
    }
  }

  // Multiple fallback detection strategies follow...
  // But response.function_call_arguments.done is the PRIMARY strategy
});
```

**Detection Strategies (in priority order):**
1. `response.function_call_arguments.done` ← **PRIMARY (use this!)**
2. `response.done` ← Fallback (may be too late)
3. `response.function_call` ← Fallback
4. `response.function_call.done` ← Fallback
5. `conversation.item.completed` ← Fallback
6. `conversation.updated` ← Last resort

### Step 5: Call ID Extraction & REST API Call

**Location:** `frontend/utils/functionCalls.ts:68-85`

```typescript
export function extractCallId(functionCall: any): string | null {
  // Priority: call_id > id > item_id (as last resort)
  const callId = functionCall.call_id || functionCall.id || functionCall.item_id;

  if (!callId) {
    console.error('[RAG] ✗ No call_id found');
    return null;
  }

  return callId;
}
```

**Location:** `frontend/hooks/useVoiceSession.ts` (function call execution)

```typescript
async function sendFunctionCallToBackend(
  callId: string,
  functionName: string,
  args: Record<string, any>
): Promise<any> {
  const response = await fetch(`${BACKEND_URL}/api/rag/function-call`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      type: 'function_call',
      call_id: callId,
      function_name: functionName,
      arguments: args,
    }),
  });

  if (!response.ok) {
    throw new Error(`Function call failed: ${response.statusText}`);
  }

  return await response.json();
}
```

### Step 6-8: Backend Processing

**Location:** `backend/app/routes/rag.py`

```python
@router.post("/api/rag/function-call")
async def execute_function_call(request: Request):
    # Parse request body
    body = await request.json()

    call_id = body.get("call_id")
    function_name = body.get("function_name")
    arguments = body.get("arguments", {})

    if function_name == "rag_knowledge":
        query = arguments.get("query", "")

        # Query RAG service via HTTP
        rag_result = await rag_client.query(query)

        # Return result in HTTP response
        return JSONResponse(content={
            "type": "function_call_result",
            "call_id": call_id,
            "function_name": function_name,
            "result": {
                "context": rag_result.get("context", ""),
                "sources": rag_result.get("sources", []),
                "success": True
            }
        })
```

**Location:** `backend/app/services/rag_client.py:16-30`

```python
async def query(self, query_text: str) -> Optional[dict]:
    """Query RAG service for relevant context"""
    url = f"{self.base_url}/api/rag/query"

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(url, json={"query": query_text})
        response.raise_for_status()
        result = response.json()

        return result
```

### Step 9-11: Sending Results to OpenAI

**Location:** `frontend/hooks/useVoiceSession.ts` (function call execution flow)

```typescript
// After detecting function call in data channel event
const handleFunctionCall = useCallback(async (callId: string, functionName: string, args: any) => {
  try {
    // Send to backend via REST API
    const response = await fetch(`${BACKEND_URL}/api/rag/function-call`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        type: 'function_call',
        call_id: callId,
        function_name: functionName,
        arguments: args,
      }),
    });

    const result = await response.json();

    // Clear timeout since we got a response
    if (functionTimeoutRef.current) {
      clearTimeout(functionTimeoutRef.current);
    }

    if (dataChannelRef.current && dataChannelRef.current.readyState === 'open') {
      // Format result for OpenAI
      const output = formatRagResult(result.result);

      // Send function call output to OpenAI
      sendFunctionOutput(dataChannelRef.current, callId, output);

      // Create NEW response to use the function output
      createNewResponse(dataChannelRef.current, FUNCTION_OUTPUT_DELAY_MS);
    }
  } catch (error) {
    console.error('[RAG] Function call failed:', error);
    // Handle error...
  }
});
```

**Location:** `frontend/utils/functionCalls.ts:17-36, 45-59`

```typescript
export function sendFunctionOutput(
  dataChannel: RTCDataChannel,
  callId: string,
  output: string
): string {
  const functionOutput: FunctionCallOutputEvent = {
    type: 'conversation.item.create',
    event_id: crypto.randomUUID(),  // REQUIRED!
    item: {
      type: 'function_call_output',
      call_id: callId,
      output: output,
    },
  };

  dataChannel.send(JSON.stringify(functionOutput));
  return functionOutput.event_id;
}

export function createNewResponse(
  dataChannel: RTCDataChannel,
  delay: number = 100  // 100ms delay
): void {
  setTimeout(() => {
    if (dataChannel.readyState === 'open') {
      const responseCreate: ResponseCreateEvent = {
        type: 'response.create',
        event_id: crypto.randomUUID(),  // REQUIRED!
      };
      dataChannel.send(JSON.stringify(responseCreate));
    }
  }, delay);
}
```

**Critical Points:**
1. ✅ **event_id is REQUIRED** - All events sent to OpenAI must have `event_id: crypto.randomUUID()`
2. ✅ **call_id vs item_id** - Use `call_id` from the function call, not `item_id`
3. ✅ **New response creation** - After sending function output, MUST create new response
4. ✅ **100ms delay** - Ensures function output is processed before new response starts

---

## 4. Communication Protocols

### Why Multiple Protocols?

This application uses **4 different communication protocols** for different purposes. Here's why each is necessary:

| Protocol | Purpose | Endpoints | Direction | When Used |
|----------|---------|-----------|-----------|-----------|
| **REST API (SDP)** | SDP exchange | `POST /api/realtime/session` | Frontend → Backend → OpenAI | Once, during setup |
| **WebRTC Data Channel** | OpenAI events & function calls | `oai-events` channel | Bidirectional (Frontend ↔ OpenAI) | Continuous, for all events |
| **WebRTC Audio** | Voice streams | RTP over UDP | Bidirectional (Frontend ↔ OpenAI) | Continuous, for voice |
| **REST API (Function Calls)** | Function execution | `POST /api/rag/function-call` | Request/Response (Frontend → Backend) | On-demand, when function called |
| **HTTP** | RAG queries | `POST /api/rag/query` | Backend → RAG Service | On-demand, when function called |

### Protocol Details

#### REST API (SDP Exchange)
**Purpose:** One-time setup to establish WebRTC connection

```
Frontend                  Backend                   OpenAI
   |                         |                         |
   |--POST /api/realtime---->|                         |
   |   (SDP Offer)           |--POST /v1/realtime----->|
   |                         |   (Forward SDP)         |
   |                         |<---SDP Answer-----------|
   |<--SDP Answer------------|                         |
```

**Why REST?**
- Simple request/response pattern
- One-time operation
- Backend can validate and add authentication
- No need for persistent connection

#### WebRTC Data Channel
**Purpose:** Real-time bidirectional event streaming with OpenAI

```
Frontend                              OpenAI
   |                                     |
   |<===== Data Channel: oai-events ====>|
   |                                     |
   |<-- session.created -----------------|
   |--- session.update ----------------->|
   |<-- response.function_call... -------|
   |--- conversation.item.create ------->|
   |--- response.create ---------------->|
   |<-- response.audio_transcript -------|
```

**Why Data Channel?**
- Low latency (peer-to-peer after setup)
- Bidirectional (can send and receive)
- Ordered delivery (messages arrive in order)
- Direct browser ↔ OpenAI communication
- No backend involvement after setup

#### WebRTC Audio
**Purpose:** Real-time voice streaming

```
Frontend                              OpenAI
   |                                     |
   |<====== RTP Audio Stream (UDP) =====>|
   |                                     |
   |--- User's voice -------------------->|
   |<-- AI's voice -----------------------|
```

**Why WebRTC Audio?**
- Real-time, low-latency audio
- Browser's built-in echo cancellation
- Noise suppression
- Automatic gain control
- Direct peer-to-peer (no server processing)
- Efficient bandwidth usage

#### REST API (Function Execution)
**Purpose:** Backend orchestration for function calls

```
Frontend                  Backend                   RAG Service
   |                         |                         |
   |                         |                         |
   |                         |                         |
   |--POST /api/rag/-------->|                         |
   |   function-call         |--HTTP POST /api/rag---->|
   |                         |<--Context + Sources-----|
   |<--HTTP Response---------|                         |
   |   (function result)     |                         |
```

**Why REST API?**
- Simple synchronous request/response pattern
- Stateless backend (no connection management needed)
- Each function call is independent
- Easy error handling via HTTP status codes
- No persistent connection overhead
- Straightforward timeout handling

#### HTTP (RAG Queries)
**Purpose:** Service-to-service communication

```
Backend                   RAG Service
   |                         |
   |--POST /api/rag/query--->|
   |   { query: "..." }      |
   |                         |
   |<--{ context, sources }--|
```

**Why HTTP?**
- Standard service-to-service communication
- Simple stateless queries
- Backend → RAG is server-side only
- Easy to add authentication/validation
- Widely supported

### Why REST API for Function Calls?

**For SDP exchange:** ✅ REST API (already using)

**For function calls:** ✅ REST API (synchronous pattern)

Here's why REST API works well for function calls in this architecture:

```typescript
// ✅ Synchronous REST API pattern
async function executeFunctionCall(callId: string, args: any) {
  // Send request and wait for response
  const response = await fetch(`${BACKEND_URL}/api/rag/function-call`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ call_id: callId, arguments: args }),
  });

  // Response arrives synchronously with result
  const result = await response.json();

  // Immediately send to OpenAI via data channel
  sendFunctionOutput(dataChannel, callId, result);
}
```

**REST API advantages:**
- Synchronous request/response (natural for function calls)
- Stateless backend (no connection management)
- Standard HTTP error codes
- No connection overhead
- Each call is independent
- Simple timeout handling with fetch AbortSignal

---

## 5. Realtime API Events

### Event Flow Sequence

```
┌─────────────────────────────────────────────────────────────────────┐
│                        SESSION LIFECYCLE                            │
└─────────────────────────────────────────────────────────────────────┘

1. session.created              → Connection established, register functions
2. session.updated             → Confirmation of updates

┌─────────────────────────────────────────────────────────────────────┐
│                          USER SPEECH                                │
└─────────────────────────────────────────────────────────────────────┘

3. input_audio_buffer.speech_started
4. input_audio_buffer.speech_stopped
5. conversation.item.input_audio_transcription.completed  → User transcript

┌─────────────────────────────────────────────────────────────────────┐
│                  AI RESPONSE (NO FUNCTION CALL)                     │
└─────────────────────────────────────────────────────────────────────┘

6. response.created
7. response.output_audio_transcript.delta  → AI speech (incremental)
8. response.output_audio_transcript.done
9. response.done

┌─────────────────────────────────────────────────────────────────────┐
│                  AI RESPONSE (WITH FUNCTION CALL)                   │
└─────────────────────────────────────────────────────────────────────┘

6. response.created
7. response.function_call_arguments.delta  → Arguments building up
8. response.function_call_arguments.done   → ⚠️ CRITICAL: Detect here!
9. response.done                           → Too late for detection!

┌─────────────────────────────────────────────────────────────────────┐
│                      FUNCTION CALL EXECUTION                        │
└─────────────────────────────────────────────────────────────────────┘

10. [Frontend sends to backend via REST API POST]
11. [Backend queries RAG service and returns response]
12. [Frontend receives result in REST response]
13. conversation.item.create (function_call_output)  → Send result
14. response.create                                  → Request new response

┌─────────────────────────────────────────────────────────────────────┐
│                  AI FINAL RESPONSE (WITH CONTEXT)                   │
└─────────────────────────────────────────────────────────────────────┘

15. response.created
16. response.output_audio_transcript.delta
17. response.output_audio_transcript.done
18. response.done

┌─────────────────────────────────────────────────────────────────────┐
│                          ERROR HANDLING                             │
└─────────────────────────────────────────────────────────────────────┘

19. error  → Any error event
```

### Event Types Used in Code

**Location:** `frontend/hooks/useVoiceSession.ts:292-349`

```typescript
// ──────────────────────────────────────────────────────────
// SESSION MANAGEMENT
// ──────────────────────────────────────────────────────────
if (eventData.type === 'session.created') {
  // Triggers function registration
  console.log('[Session] Created, registering functions');
}

if (eventData.type === 'session.updated') {
  // Confirmation of session updates
  console.log('[Session] Updated successfully');
}

// ──────────────────────────────────────────────────────────
// USER SPEECH TRANSCRIPTION
// ──────────────────────────────────────────────────────────
if (eventData.type === 'conversation.item.input_audio_transcription.completed') {
  const transcriptText = eventData.transcript || '';
  addTranscriptMessage('user', transcriptText);
  console.log('[User]', transcriptText);
}

// ──────────────────────────────────────────────────────────
// FUNCTION CALL DETECTION (6 STRATEGIES)
// ──────────────────────────────────────────────────────────
if (eventData.type === 'response.function_call_arguments.done') {
  // PRIMARY STRATEGY - Earliest detection
  console.log('[Function] Arguments complete');
}

if (eventData.type === 'response.done') {
  // FALLBACK 1 - May be too late
  console.log('[Response] Complete');
}

if (eventData.type === 'response.function_call') {
  // FALLBACK 2
  console.log('[Function] Call detected');
}

if (eventData.type === 'response.function_call.done') {
  // FALLBACK 3
  console.log('[Function] Call done');
}

if (eventData.type === 'conversation.item.completed') {
  // FALLBACK 4
  console.log('[Conversation] Item completed');
}

if (eventData.type === 'conversation.updated') {
  // FALLBACK 5 - Last resort
  console.log('[Conversation] Updated');
}

// ──────────────────────────────────────────────────────────
// AI SPEECH TRANSCRIPTION
// ──────────────────────────────────────────────────────────
if (eventData.type === 'response.output_audio_transcript.delta') {
  const delta = eventData.delta || '';
  addTranscriptMessage('assistant', delta);
  setStatus('speaking');
  console.log('[AI]', delta);
}

if (eventData.type === 'response.output_audio_transcript.done') {
  console.log('[AI] Finished speaking');
}

// ──────────────────────────────────────────────────────────
// RESPONSE COMPLETION
// ──────────────────────────────────────────────────────────
if (eventData.type === 'response.done') {
  setStatus('listening');
  console.log('[Response] Complete, back to listening');
}

// ──────────────────────────────────────────────────────────
// ERROR HANDLING
// ──────────────────────────────────────────────────────────
if (eventData.type === 'error') {
  const errorMessage = eventData.error?.message || 'Unknown error';
  setError(errorMessage);
  console.error('[Error]', errorMessage);
}
```

### Event Data Structures

**Location:** `frontend/types/openai.ts`

```typescript
// ──────────────────────────────────────────────────────────
// FUNCTION CALL EVENT (FROM OPENAI)
// ──────────────────────────────────────────────────────────
interface FunctionCallEvent {
  type: 'response.function_call_arguments.done';
  call_id: string;          // Function call identifier
  name: string;             // Function name (e.g., 'rag_knowledge')
  arguments: string;        // JSON string of arguments
}

// Example:
{
  "type": "response.function_call_arguments.done",
  "call_id": "call_abc123",
  "name": "rag_knowledge",
  "arguments": "{\"query\":\"What is in the docs?\"}"
}

// ──────────────────────────────────────────────────────────
// FUNCTION OUTPUT EVENT (TO OPENAI)
// ──────────────────────────────────────────────────────────
interface FunctionCallOutputEvent {
  type: 'conversation.item.create';
  event_id: string;         // REQUIRED: crypto.randomUUID()
  item: {
    type: 'function_call_output';
    call_id: string;        // Must match call_id from function call
    output: string;         // JSON string of results
  };
}

// Example:
{
  "type": "conversation.item.create",
  "event_id": "evt_xyz789",
  "item": {
    "type": "function_call_output",
    "call_id": "call_abc123",
    "output": "{\"context\":\"The documentation contains...\",\"sources\":[\"doc1.pdf\"]}"
  }
}

// ──────────────────────────────────────────────────────────
// RESPONSE CREATE EVENT (TO OPENAI)
// ──────────────────────────────────────────────────────────
interface ResponseCreateEvent {
  type: 'response.create';
  event_id: string;         // REQUIRED: crypto.randomUUID()
}

// Example:
{
  "type": "response.create",
  "event_id": "evt_create_123"
}

// ──────────────────────────────────────────────────────────
// SESSION UPDATE EVENT (TO OPENAI)
// ──────────────────────────────────────────────────────────
interface SessionUpdateEvent {
  type: 'session.update';
  event_id: string;         // REQUIRED: crypto.randomUUID()
  session: {
    type: 'realtime';
    tools?: Array<{         // Function definitions
      type: 'function';
      name: string;
      description: string;
      parameters: object;
    }>;
    tool_choice?: string;   // 'auto' | 'none' | { type: 'function', name: string }
  };
}

// Example:
{
  "type": "session.update",
  "event_id": "evt_update_456",
  "session": {
    "type": "realtime",
    "tools": [{
      "type": "function",
      "name": "rag_knowledge",
      "description": "Search the knowledge base",
      "parameters": {
        "type": "object",
        "properties": {
          "query": { "type": "string" }
        },
        "required": ["query"]
      }
    }],
    "tool_choice": "auto"
  }
}

// ──────────────────────────────────────────────────────────
// TRANSCRIPTION EVENT (FROM OPENAI)
// ──────────────────────────────────────────────────────────
interface TranscriptionEvent {
  type: 'conversation.item.input_audio_transcription.completed';
  transcript: string;       // What the user said
}

// Example:
{
  "type": "conversation.item.input_audio_transcription.completed",
  "transcript": "What is in the documentation?"
}

// ──────────────────────────────────────────────────────────
// AI SPEECH EVENT (FROM OPENAI)
// ──────────────────────────────────────────────────────────
interface AudioTranscriptEvent {
  type: 'response.output_audio_transcript.delta';
  delta: string;            // Incremental text of AI's speech
}

// Example:
{
  "type": "response.output_audio_transcript.delta",
  "delta": "Based on the documentation, "
}
```

### When Are Events Triggered?

| Event | Trigger | Purpose |
|-------|---------|---------|
| `session.created` | After WebRTC connection established | Register functions, configure session |
| `session.updated` | After `session.update` sent | Confirm configuration changes |
| `input_audio_buffer.speech_started` | User starts speaking | Update UI to show user is speaking |
| `input_audio_buffer.speech_stopped` | User stops speaking | Update UI to show processing |
| `conversation.item.input_audio_transcription.completed` | User's speech transcribed | Display what user said |
| `response.created` | AI starts generating response | Update UI to show AI is thinking |
| `response.function_call_arguments.delta` | AI building function arguments | Optional: show progress |
| `response.function_call_arguments.done` | Function arguments complete | **DETECT FUNCTION CALL HERE** |
| `response.output_audio_transcript.delta` | AI speaking (incremental) | Display what AI is saying |
| `response.output_audio_transcript.done` | AI finished speaking | Complete transcript |
| `response.done` | Response complete | Update UI back to listening |
| `error` | Any error occurs | Display error to user |

---

## 6. Critical Implementation Details

### Must-Have Requirements

#### 1. Event IDs are REQUIRED

Every event sent to OpenAI MUST include `event_id: crypto.randomUUID()`. Missing this causes events to be **silently ignored**.

```typescript
// ❌ WRONG - Event will be ignored
dataChannel.send(JSON.stringify({
  type: 'session.update',
  session: { tools: [...] }
}));

// ✅ CORRECT - Event will be processed
dataChannel.send(JSON.stringify({
  type: 'session.update',
  event_id: crypto.randomUUID(),  // REQUIRED!
  session: { tools: [...] }
}));
```

#### 2. Early Function Call Detection

Detect at `response.function_call_arguments.done`, NOT `response.done`.

```typescript
// ❌ WRONG - Too late, causes "Tool call ID not found" error
if (eventData.type === 'response.done') {
  if (eventData.output?.function_call) {
    // By now, the item_id is invalid!
  }
}

// ✅ CORRECT - Early detection
if (eventData.type === 'response.function_call_arguments.done') {
  // Perfect timing - arguments complete, item_id still valid
  const callId = eventData.call_id;
  const args = JSON.parse(eventData.arguments);
  // Process immediately
}
```

**Timeline:**
```
response.created
  ↓
response.function_call_arguments.delta (building args)
  ↓
response.function_call_arguments.done  ← DETECT HERE! ✅
  ↓
[other events...]
  ↓
response.done  ← Too late! ❌ (item_id may be invalid)
```

#### 3. Call ID Priority

Use `call_id` field first, then `id`, then `item_id` as last resort.

```typescript
// ✅ CORRECT - Priority order
const callId = eventData.call_id || eventData.id || eventData.item_id;

// Why this order?
// - call_id: Specifically for function calls
// - id: General identifier
// - item_id: Conversation item (may not match function call)
```

#### 4. New Response After Function Output

After sending function output, MUST create new response.

```typescript
// Send function output
dataChannel.send(JSON.stringify({
  type: 'conversation.item.create',
  event_id: crypto.randomUUID(),
  item: {
    type: 'function_call_output',
    call_id: callId,
    output: JSON.stringify(result),
  }
}));

// ⚠️ MUST create new response (with 100ms delay)
setTimeout(() => {
  dataChannel.send(JSON.stringify({
    type: 'response.create',
    event_id: crypto.randomUUID(),
  }));
}, 100);
```

**Why 100ms delay?**
- Ensures function output is processed before new response starts
- Prevents race conditions
- OpenAI needs time to add the output to the conversation

#### 5. Deduplication

Track processed `call_id` values to prevent processing same function call multiple times.

```typescript
const processedCallIds = new Set<string>();

function handleFunctionCall(eventData: any) {
  const callId = eventData.call_id;

  // Check if already processed
  if (processedCallIds.has(callId)) {
    console.log('[RAG] Already processed', callId);
    return;  // Skip
  }

  // Process function call
  processedCallIds.add(callId);
  // ... rest of processing
}
```

**Why deduplication?**
- Multiple events can contain the same function call
- 6 different event types are checked (fallback strategies)
- Without deduplication, function would be called 6 times!

#### 6. Timeout Handling

30-second timeout for function execution to prevent hanging sessions.

```typescript
// Use AbortController for fetch timeout
const abortController = new AbortController();
const timeoutId = setTimeout(() => abortController.abort(), 30000);

try {
  // Send function call with timeout
  const response = await fetch(`${BACKEND_URL}/api/rag/function-call`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ call_id: callId, arguments: args }),
    signal: abortController.signal,  // Abort after 30s
  });

  clearTimeout(timeoutId);  // Clear timeout on success

  const result = await response.json();
  // ... process result

} catch (error) {
  if (error.name === 'AbortError') {
    console.error('[RAG] Function call timeout');

    // Send error to OpenAI
    dataChannel.send(JSON.stringify({
      type: 'conversation.item.create',
      event_id: crypto.randomUUID(),
      item: {
        type: 'function_call_output',
        call_id: callId,
        output: JSON.stringify({
          error: 'Function execution timed out after 30 seconds',
        }),
      }
    }));

    // Create new response
    createNewResponse(dataChannel);
  }
}
```

### Common Pitfalls & Solutions

#### Pitfall 1: "Tool call ID not found in conversation"

**Cause:** Detecting function call too late (at `response.done`)

**Solution:** Detect at `response.function_call_arguments.done`

```typescript
// ❌ WRONG
if (eventData.type === 'response.done') {
  // Too late - item_id invalid
}

// ✅ CORRECT
if (eventData.type === 'response.function_call_arguments.done') {
  // Perfect timing - item_id valid
}
```

#### Pitfall 2: Events Silently Ignored

**Cause:** Missing `event_id` field

**Solution:** Always include `event_id: crypto.randomUUID()`

```typescript
// ❌ WRONG - Silently ignored
dataChannel.send(JSON.stringify({
  type: 'response.create'
}));

// ✅ CORRECT - Processed
dataChannel.send(JSON.stringify({
  type: 'response.create',
  event_id: crypto.randomUUID()
}));
```

#### Pitfall 3: Function Called Multiple Times

**Cause:** No deduplication

**Solution:** Track processed `call_id` values

```typescript
const processedCallIds = new Set<string>();

if (processedCallIds.has(callId)) {
  return;  // Skip duplicate
}
processedCallIds.add(callId);
```

#### Pitfall 4: No AI Response After Function Output

**Cause:** Forgot to create new response

**Solution:** Call `response.create` after sending function output

```typescript
// Send function output
sendFunctionOutput(dataChannel, callId, output);

// MUST create new response
setTimeout(() => {
  dataChannel.send(JSON.stringify({
    type: 'response.create',
    event_id: crypto.randomUUID(),
  }));
}, 100);
```

#### Pitfall 5: Invalid SDP Format

**Cause:** Wrong content type or malformed SDP

**Solution:** Use `Content-Type: application/sdp` and validate SDP

```typescript
// ❌ WRONG
fetch(url, {
  headers: { 'Content-Type': 'application/json' },  // Wrong!
  body: JSON.stringify({ sdp: offer.sdp })          // Wrong format!
});

// ✅ CORRECT
fetch(url, {
  headers: { 'Content-Type': 'application/sdp' },   // Correct!
  body: offer.sdp                                   // Raw SDP text
});
```

#### Pitfall 6: WebRTC Connection Fails

**Cause:** Data channel created after SDP exchange

**Solution:** Create data channel BEFORE creating offer

```typescript
// ❌ WRONG - Too late
const offer = await peerConnection.createOffer();
const dataChannel = peerConnection.createDataChannel('oai-events');  // Too late!

// ✅ CORRECT - Before offer
const dataChannel = peerConnection.createDataChannel('oai-events');
const offer = await peerConnection.createOffer();  // Channel included in SDP
```

---

## Summary: How It All Works Together

1. **Setup Phase (REST + WebRTC)**
   - Frontend creates WebRTC offer with data channel
   - Backend forwards SDP to OpenAI
   - WebRTC connection established
   - Audio streams and data channel ready

2. **Registration Phase (WebRTC Data Channel)**
   - OpenAI sends `session.created` event
   - Frontend registers custom functions via `session.update`
   - OpenAI confirms with `session.updated`

3. **Conversation Phase (WebRTC Audio + Data Channel)**
   - User speaks → Audio sent to OpenAI
   - OpenAI transcribes → Sends transcription event
   - OpenAI decides to call function → Sends function call event

4. **Function Execution Phase (REST API + HTTP)**
   - Frontend detects function call early (`response.function_call_arguments.done`)
   - Frontend sends to backend via REST API POST `/api/rag/function-call`
   - Backend queries RAG service via HTTP
   - Results flow back synchronously: RAG → Backend → Frontend (HTTP response)

5. **Response Phase (WebRTC Data Channel + Audio)**
   - Frontend sends function output to OpenAI via data channel
   - Frontend creates new response
   - OpenAI generates answer using context
   - OpenAI speaks answer → Audio received by frontend

**Key Insight:** The architecture cleverly uses each protocol for its strengths:
- **REST API** for simple setup and function execution
- **WebRTC Audio** for real-time voice
- **WebRTC Data Channel** for real-time events
- **HTTP** for service-to-service calls

This creates a low-latency, scalable system where:
- Browser directly communicates with OpenAI for audio/events (WebRTC)
- Backend handles secure operations (API key management, function execution)
- Stateless REST API for function calls (no connection management overhead)
- Simple, reliable request/response pattern for function execution
