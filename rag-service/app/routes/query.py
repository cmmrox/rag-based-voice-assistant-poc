import logging
from fastapi import APIRouter, HTTPException
from app.models.schemas import QueryRequest, QueryResponse
from app.services.embedding import embedding_service
from app.services.chromadb_service import chromadb_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/rag", tags=["rag"])


@router.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Process a query and retrieve relevant context"""
    try:
        query = request.query.strip()
        
        if not query:
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        logger.info(f"Processing query: {query[:50]}...")
        
        # Generate query embedding
        query_embedding = await embedding_service.generate_embedding(query)
        
        # Search ChromaDB (now async)
        results = await chromadb_service.query(
            query_embeddings=[query_embedding],
            n_results=5
        )
        
        # Extract documents and metadata
        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        
        if not documents:
            return QueryResponse(
                context="No relevant context found in knowledge base.",
                sources=[],
                message="No documents found"
            )
        
        # Assemble context
        context_parts = []
        for i, doc in enumerate(documents):
            source_info = metadatas[i] if i < len(metadatas) else {}
            context_parts.append(f"[Document {i+1} - Source: {source_info.get('source', 'unknown')}]\n{doc}")
        
        context = "\n\n".join(context_parts)
        
        logger.info(f"Retrieved {len(documents)} relevant documents")
        
        return QueryResponse(
            context=context,
            sources=metadatas,
            message=f"Retrieved {len(documents)} relevant documents"
        )
    
    except Exception as e:
        logger.error(f"Error processing query: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

