import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config import settings
from app.routes import documents, query
from app.services.chromadb_service import chromadb_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup: Try to pre-initialize ChromaDB (non-blocking)
    logger.info("Starting RAG Service...")
    try:
        # Attempt to initialize ChromaDB, but don't fail if it's unavailable
        chromadb_service.is_available()
        logger.info("ChromaDB pre-initialization attempted")
    except Exception as e:
        logger.warning(f"ChromaDB pre-initialization failed (non-critical): {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down RAG Service...")


app = FastAPI(title="RAG Service", version="1.0.0", lifespan=lifespan)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for POC
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(documents.router)
app.include_router(query.router)


@app.get("/health")
async def health_check():
    """Health check endpoint - works regardless of ChromaDB availability"""
    # Get status without blocking (non-initializing check)
    chromadb_status = chromadb_service.get_status()
    
    # If uninitialized, try a quick availability check (with timeout protection)
    if chromadb_status == "uninitialized":
        try:
            # This will attempt initialization but has timeout protection
            chromadb_status = "available" if chromadb_service.is_available() else "unavailable"
        except Exception as e:
            chromadb_status = f"unavailable: {str(e)[:50]}"
            logger.debug(f"Health check ChromaDB status error: {e}")
    elif chromadb_status == "initialized":
        chromadb_status = "available"
    
    return {
        "status": "healthy",
        "service": "rag-service",
        "chromadb": chromadb_status
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

