# Demo Script

This script outlines how to demonstrate the RAG-Based Voice Assistant POC.

## Pre-Demo Setup

### 1. Start All Services

```bash
# Run all services together
docker-compose -f docker-compose.full.yml up

# Or run in development mode
docker-compose -f docker-compose.dev.yml up
```

Wait for all services to be healthy:
- ChromaDB: http://localhost:8000/health
- Backend: http://localhost:8002/health
- RAG Service: http://localhost:8001/health
- Frontend: http://localhost:3000

### 2. Ingest Sample Documents

Prepare 2-3 sample documents (PDF, TXT, or MD) related to a specific topic.

**Example: Ingest a document about AI**

```bash
curl -X POST http://localhost:8001/api/documents/ingest \
  -F "file=@sample_document.pdf"
```

Verify ingestion:
```bash
curl http://localhost:8001/health
```

### 3. Open Frontend

Navigate to http://localhost:3000 in a modern browser (Chrome recommended).

## Demo Flow

### Step 1: Introduction (30 seconds)

**Say:**
"Today I'll demonstrate a RAG-based voice assistant that can answer questions using a knowledge base. The system uses WebRTC for real-time audio, OpenAI's Realtime API for speech-to-text and text-to-speech with native function calling, and ChromaDB for vector-based document retrieval. The model intelligently decides when to search the knowledge base using function calling."

### Step 2: Start Voice Session (30 seconds)

**Actions:**
1. Click the "Start Voice" button
2. Grant microphone permissions when prompted
3. Wait for "Ready" status

**Say:**
"I'm starting a voice session. The system is establishing a WebRTC connection and connecting to OpenAI's Realtime API."

### Step 3: Ask a Question (1 minute)

**Actions:**
1. Click the microphone button (if needed)
2. Ask a question related to the ingested documents
3. Example: "What is the main topic discussed in the documents?"

**Say:**
"I'll ask a question about the documents we ingested. The system will transcribe my speech, retrieve relevant context from the knowledge base, and generate a response."

**Expected Behavior:**
- Status changes to "Listening"
- Your speech is transcribed
- Status changes to "Processing"
- Model analyzes query and calls search_knowledge_base function (if needed)
- Function executes: RAG service retrieves relevant context
- Function result returned to model
- Assistant responds with knowledge-grounded answer
- Status changes to "Speaking"
- Response appears in transcript

### Step 4: Multi-Turn Conversation (2 minutes)

**Actions:**
1. Ask follow-up questions
2. Example: "Can you tell me more about that?"
3. Example: "What are the key points?"

**Say:**
"Now I'll have a multi-turn conversation. The system maintains context and can answer follow-up questions."

**Expected Behavior:**
- Multiple conversation turns work smoothly
- Context is maintained
- Responses reference the knowledge base

### Step 5: Demonstrate Error Handling (30 seconds)

**Actions:**
1. Ask a question unrelated to the knowledge base
2. Example: "What's the weather today?"

**Say:**
"If I ask something not in the knowledge base, the system should handle it gracefully."

**Expected Behavior:**
- System responds appropriately
- May say it doesn't have that information
- No crashes or errors

### Step 6: End Session (30 seconds)

**Actions:**
1. Click "Stop" button
2. Session ends

**Say:**
"I'll end the session. The system closes all connections and cleans up resources."

## Demo Tips

### Before Demo

1. **Test Everything First**
   - Test the complete flow
   - Verify documents are ingested
   - Check all services are running
   - Test microphone permissions

2. **Prepare Backup Plans**
   - Have sample questions ready
   - Have backup documents
   - Know how to check logs if issues occur

3. **Environment Setup**
   - Ensure stable internet connection
   - Use Chrome browser (most reliable)
   - Close unnecessary applications

### During Demo

1. **Speak Clearly**
   - Speak at normal pace
   - Enunciate clearly
   - Wait for responses

2. **Explain What's Happening**
   - Point out status changes
   - Explain the flow
   - Highlight key features

3. **Handle Issues Gracefully**
   - If something fails, explain it's a POC
   - Check logs if needed
   - Have backup questions ready

### After Demo

1. **Answer Questions**
   - Be ready to explain architecture
   - Discuss limitations
   - Talk about future enhancements

2. **Show Code/Architecture**
   - Show project structure
   - Explain key components
   - Discuss technology choices

## Sample Questions

### For Technical Documents

- "What is the main architecture described?"
- "What are the key components?"
- "How does the system work?"
- "What are the main features?"

### For General Documents

- "What is this document about?"
- "What are the main points?"
- "Can you summarize the key ideas?"
- "What are the important details?"

## Troubleshooting During Demo

### If WebRTC Fails to Connect

**Say:** "Let me check the connection..."
- Check browser console
- Verify backend is running
- Try refreshing the page

### If Transcription Fails

**Say:** "There seems to be an audio issue..."
- Check microphone permissions
- Verify OpenAI API key
- Check backend logs

### If RAG Retrieval Fails

**Say:** "The knowledge retrieval is having issues..."
- Verify documents are ingested
- Check RAG service logs
- Try a simpler question

### If Response Generation Fails

**Say:** "The response generation is taking longer than expected..."
- Check OpenAI API status
- Verify API key has credits
- Check backend logs

## Key Points to Highlight

1. **Real-time Voice Interaction**
   - Low latency
   - Natural conversation flow

2. **RAG Integration with Function Calling**
   - Native function calling for intelligent knowledge base search
   - Model decides when to search knowledge base
   - Knowledge-grounded responses
   - Relevant context retrieval

3. **Technology Stack**
   - WebRTC for audio
   - OpenAI Realtime API
   - ChromaDB for vector search

4. **Architecture**
   - Microservices design
   - Scalable components
   - Docker orchestration

## Demo Duration

- **Quick Demo**: 5 minutes
- **Full Demo**: 10 minutes
- **Detailed Demo**: 15-20 minutes

Adjust based on audience and time available.

