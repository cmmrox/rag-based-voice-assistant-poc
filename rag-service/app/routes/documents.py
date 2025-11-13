import logging
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.models.schemas import DocumentIngestResponse
from app.services.document_parser import document_parser
from app.services.embedding import embedding_service
from app.services.chromadb_service import chromadb_service
import uuid

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/documents", tags=["documents"])


@router.post("/ingest", response_model=DocumentIngestResponse)
async def ingest_document(file: UploadFile = File(...)):
    """Ingest a document into the knowledge base"""
    try:
        # Read file content
        file_content = await file.read()
        filename = file.filename or "unknown"
        
        logger.info(f"Ingesting document: {filename}")
        
        # Parse document
        text = await document_parser.parse_document(file_content, filename)
        
        if not text or len(text.strip()) == 0:
            raise HTTPException(status_code=400, detail="Document is empty or could not be parsed")
        
        # Chunk text
        chunks = document_parser.chunk_text(text, chunk_size=500, overlap=100)
        
        if not chunks:
            raise HTTPException(status_code=400, detail="No chunks created from document")
        
        # Generate embeddings
        chunk_texts = [chunk[0] for chunk in chunks]
        embeddings = await embedding_service.generate_embeddings(chunk_texts)
        
        # Prepare metadata and IDs
        metadatas = [
            {
                "source": filename,
                "chunk_id": chunk[1],
                "chunk_index": idx
            }
            for idx, chunk in enumerate(chunks)
        ]
        
        ids = [f"{filename}_{chunk[1]}_{uuid.uuid4().hex[:8]}" for chunk in chunks]
        
        # Store in ChromaDB
        chromadb_service.add_documents(
            documents=chunk_texts,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
        
        logger.info(f"Successfully ingested document: {filename}, {len(chunks)} chunks")
        
        return DocumentIngestResponse(
            status="success",
            chunks=len(chunks),
            message=f"Document ingested successfully with {len(chunks)} chunks"
        )
    
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error ingesting document: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error ingesting document: {str(e)}")

