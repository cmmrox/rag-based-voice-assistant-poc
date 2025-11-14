import logging
import time
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.models.schemas import DocumentIngestResponse
from app.services.document_parser import document_parser
from app.services.embedding import embedding_service
from app.services.chromadb_service import chromadb_service
import uuid

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/documents", tags=["documents"])

# Maximum file size: 50MB
MAX_FILE_SIZE = 50 * 1024 * 1024


@router.post("/ingest", response_model=DocumentIngestResponse)
async def ingest_document(file: UploadFile = File(...)):
    """Ingest a document into the knowledge base"""
    start_time = time.time()
    filename = file.filename or "unknown"
    
    try:
        logger.info(f"=" * 60)
        logger.info(f"Starting document ingestion: {filename}")
        logger.info(f"=" * 60)
        
        # Phase 1: Read file content
        phase_start = time.time()
        logger.info(f"[Phase 1/5] Reading file content...")
        file_content = await file.read()
        file_size = len(file_content)
        
        # Validate file size
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File size ({file_size / 1024 / 1024:.2f} MB) exceeds maximum allowed size ({MAX_FILE_SIZE / 1024 / 1024} MB)"
            )
        
        phase_time = time.time() - phase_start
        logger.info(f"[Phase 1/5] File read completed: {file_size:,} bytes ({file_size / 1024:.2f} KB) in {phase_time:.2f}s")
        
        # Phase 2: Parse document
        phase_start = time.time()
        logger.info(f"[Phase 2/5] Parsing document...")
        text = await document_parser.parse_document(file_content, filename)
        
        if not text or len(text.strip()) == 0:
            raise HTTPException(status_code=400, detail="Document is empty or could not be parsed")
        
        phase_time = time.time() - phase_start
        text_length = len(text)
        logger.info(f"[Phase 2/5] Document parsing completed: {text_length:,} characters extracted in {phase_time:.2f}s")
        
        # Phase 3: Chunk text
        phase_start = time.time()
        logger.info(f"[Phase 3/5] Chunking text...")
        chunks = document_parser.chunk_text(text, chunk_size=500, overlap=100)
        
        if not chunks:
            raise HTTPException(status_code=400, detail="No chunks created from document")
        
        phase_time = time.time() - phase_start
        logger.info(f"[Phase 3/5] Text chunking completed: {len(chunks)} chunks created in {phase_time:.2f}s")
        
        # Phase 4: Generate embeddings
        phase_start = time.time()
        logger.info(f"[Phase 4/5] Generating embeddings...")
        chunk_texts = [chunk[0] for chunk in chunks]
        embeddings = await embedding_service.generate_embeddings(chunk_texts)
        
        if len(embeddings) != len(chunk_texts):
            raise HTTPException(
                status_code=500,
                detail=f"Embedding count mismatch: expected {len(chunk_texts)}, got {len(embeddings)}"
            )
        
        phase_time = time.time() - phase_start
        logger.info(f"[Phase 4/5] Embedding generation completed: {len(embeddings)} embeddings generated in {phase_time:.2f}s")
        
        # Phase 5: Store in ChromaDB
        phase_start = time.time()
        logger.info(f"[Phase 5/5] Storing documents in ChromaDB...")
        
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
        
        # Store in ChromaDB (now async)
        await chromadb_service.add_documents(
            documents=chunk_texts,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
        
        phase_time = time.time() - phase_start
        total_time = time.time() - start_time
        
        logger.info(f"[Phase 5/5] ChromaDB storage completed: {len(chunks)} documents stored in {phase_time:.2f}s")
        logger.info(f"=" * 60)
        logger.info(f"Document ingestion completed successfully!")
        logger.info(f"  File: {filename}")
        logger.info(f"  Chunks: {len(chunks)}")
        logger.info(f"  Total time: {total_time:.2f}s")
        logger.info(f"  Average time per chunk: {total_time / len(chunks):.3f}s")
        logger.info(f"=" * 60)
        
        return DocumentIngestResponse(
            status="success",
            chunks=len(chunks),
            message=f"Document ingested successfully with {len(chunks)} chunks in {total_time:.2f}s"
        )
    
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except ValueError as e:
        logger.error(f"Validation error during ingestion: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        total_time = time.time() - start_time
        logger.error(f"Error ingesting document after {total_time:.2f}s: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error ingesting document: {str(e)}"
        )

