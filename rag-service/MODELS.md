# Models Used in RAG-based Voice Assistant POC

This document lists all AI models used in the application.

## RAG Service Models

### Embedding Model

**Model**: `text-embedding-3-small`

- **Provider**: OpenAI
- **Dimensions**: 1536
- **Usage**: 
  - Document chunk embeddings (during ingestion)
  - Query embeddings (during search)
- **Location**: `rag-service/app/services/embedding.py`
- **API Endpoint**: `https://api.openai.com/v1/embeddings`
- **Cost**: Lower cost option suitable for POC
- **Performance**: Good balance between cost and performance

**Configuration**:
```python
self.model = "text-embedding-3-small"
```

**Notes**:
- Used for both document ingestion and query processing
- Supports batch processing (up to 2048 inputs per request)
- All embedding operations are now async to prevent blocking

## Backend Service Models

### GPT Model (Realtime API)

**Model**: `gpt-4o-realtime-preview-2024-10-01`

- **Provider**: OpenAI
- **Usage**: 
  - Voice conversation processing
  - Real-time speech-to-speech interaction
  - Response generation with RAG context
- **Location**: `backend/app/services/openai_gateway.py`
- **API Endpoint**: `wss://api.openai.com/v1/realtime`
- **Voice**: `alloy` (default)
- **Features**:
  - Real-time audio streaming
  - Speech-to-speech conversion
  - Context-aware responses using RAG

**Configuration**:
```python
model="gpt-4o-realtime-preview-2024-10-01"
voice="alloy"
```

## Model Selection Rationale

### Embedding Model: `text-embedding-3-small`

- **Why**: Cost-effective for POC while maintaining good quality
- **Alternative Options**:
  - `text-embedding-ada-002`: Older model, 1536 dimensions
  - `text-embedding-3-large`: Higher quality but more expensive (3072 dimensions)
- **Future Considerations**: May upgrade to `text-embedding-3-large` for production if higher accuracy is needed

### GPT Model: `gpt-4o-realtime-preview-2024-10-01`

- **Why**: Latest Realtime API model with best performance
- **Features**: 
  - Optimized for real-time voice interactions
  - Supports streaming audio
  - Low latency response generation
- **Future Considerations**: Will automatically use newer versions as OpenAI releases them

## Model Configuration

All models are configured via environment variables:

- `OPENAI_API_KEY`: Required for all OpenAI API calls
- Models are hardcoded in the service files but can be made configurable if needed

## Performance Characteristics

### Embedding Generation

- **Batch Size**: Up to 2048 texts per request
- **Async Processing**: All embedding calls are non-blocking
- **Progress Logging**: Batch progress is logged during generation

### GPT Realtime API

- **Latency**: Low latency for real-time voice interactions
- **Streaming**: Supports bidirectional audio streaming
- **Context Window**: Uses RAG context from ChromaDB for informed responses

## Cost Considerations

- **Embedding Model**: `text-embedding-3-small` is cost-effective (~$0.02 per 1M tokens)
- **GPT Model**: `gpt-4o-realtime-preview` pricing varies by usage
- **Optimization**: Batch processing reduces API calls and costs

## References

- [OpenAI Embeddings Documentation](https://platform.openai.com/docs/guides/embeddings)
- [OpenAI Realtime API Documentation](https://platform.openai.com/docs/guides/realtime)
- [text-embedding-3-small Model Card](https://platform.openai.com/docs/models/embeddings)

