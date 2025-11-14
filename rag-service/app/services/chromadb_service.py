import logging
import asyncio
import chromadb
from chromadb.config import Settings
from app.config import settings
import socket

logger = logging.getLogger(__name__)


class ChromaDBService:
    """ChromaDB service for vector storage and retrieval"""
    
    def __init__(self):
        self.client = None
        self.collection = None
        self._initialized = False
        self._initialization_error = None
    
    def _ensure_initialized(self):
        """Lazy initialization - only connect when first needed"""
        if self._initialized:
            return
        
        if self._initialization_error:
            raise RuntimeError(f"ChromaDB initialization failed: {self._initialization_error}")
        
        self._initialize()
    
    def _check_connection(self, host: str, port: int, timeout: float = 2.0) -> bool:
        """Check if ChromaDB server is reachable"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except Exception as e:
            logger.debug(f"Connection check failed: {e}")
            return False
    
    def _initialize(self):
        """Initialize ChromaDB client and collection"""
        try:
            # Check if ChromaDB server is reachable first (with timeout)
            if not self._check_connection(settings.chromadb_host, settings.chromadb_port, timeout=2.0):
                logger.warning(f"ChromaDB server not reachable at {settings.chromadb_host}:{settings.chromadb_port}, will use in-memory client")
                raise ConnectionError("ChromaDB server not reachable")
            
            # Connect to ChromaDB with timeout handling
            self.client = chromadb.HttpClient(
                host=settings.chromadb_host,
                port=settings.chromadb_port
            )
            
            # Create or get collection
            self.collection = self.client.get_or_create_collection(
                name="knowledge_base",
                metadata={"hnsw:space": "cosine"}  # Cosine similarity
            )
            
            self._initialized = True
            logger.info("ChromaDB initialized successfully")
        
        except Exception as e:
            logger.warning(f"Error initializing ChromaDB: {e}, falling back to in-memory client")
            # Fallback to in-memory client for development
            try:
                self.client = chromadb.Client()
                self.collection = self.client.get_or_create_collection(
                    name="knowledge_base",
                    metadata={"hnsw:space": "cosine"}
                )
                self._initialized = True
                logger.info("Using in-memory ChromaDB client")
            except Exception as e2:
                logger.error(f"Error initializing in-memory ChromaDB: {e2}", exc_info=True)
                self._initialization_error = str(e2)
                raise
    
    def is_available(self) -> bool:
        """Check if ChromaDB is available and initialized"""
        if not self._initialized:
            try:
                self._ensure_initialized()
            except Exception:
                return False
        return self._initialized and self.client is not None and self.collection is not None
    
    def get_status(self) -> str:
        """Get ChromaDB status without blocking - returns 'initialized', 'uninitialized', or 'error'"""
        if self._initialization_error:
            return "error"
        if self._initialized:
            return "initialized"
        return "uninitialized"
    
    def _add_documents_sync(
        self,
        documents: list[str],
        embeddings: list[list[float]],
        metadatas: list[dict],
        ids: list[str]
    ):
        """Synchronous helper for adding documents"""
        self.collection.add(
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
    
    async def add_documents(
        self,
        documents: list[str],
        embeddings: list[list[float]],
        metadatas: list[dict],
        ids: list[str]
    ):
        """Add documents to the collection asynchronously"""
        self._ensure_initialized()
        try:
            total_docs = len(documents)
            logger.info(f"Starting to store {total_docs} documents in ChromaDB...")
            
            # ChromaDB can handle large batches, but we'll process in chunks for progress logging
            # ChromaDB has a practical limit, so we'll use batches of 1000
            batch_size = 1000
            num_batches = (total_docs + batch_size - 1) // batch_size
            
            for batch_idx in range(num_batches):
                start_idx = batch_idx * batch_size
                end_idx = min(start_idx + batch_size, total_docs)
                
                batch_docs = documents[start_idx:end_idx]
                batch_embeddings = embeddings[start_idx:end_idx]
                batch_metadatas = metadatas[start_idx:end_idx]
                batch_ids = ids[start_idx:end_idx]
                
                if num_batches > 1:
                    logger.info(f"Storing batch {batch_idx + 1}/{num_batches} "
                              f"(documents {start_idx + 1}-{end_idx} of {total_docs})")
                
                # Run the blocking ChromaDB operation in a thread pool
                await asyncio.to_thread(
                    self._add_documents_sync,
                    batch_docs,
                    batch_embeddings,
                    batch_metadatas,
                    batch_ids
                )
                
                if num_batches > 1:
                    logger.info(f"Completed batch {batch_idx + 1}/{num_batches}: "
                              f"stored {len(batch_docs)} documents "
                              f"({end_idx}/{total_docs} total)")
            
            logger.info(f"Successfully stored all {total_docs} documents in ChromaDB")
        except Exception as e:
            logger.error(f"Error adding documents to ChromaDB: {e}", exc_info=True)
            raise
    
    def _query_sync(
        self,
        query_embeddings: list[list[float]],
        n_results: int = 5
    ) -> dict:
        """Synchronous helper for querying"""
        return self.collection.query(
            query_embeddings=query_embeddings,
            n_results=n_results
        )
    
    async def query(
        self,
        query_embeddings: list[list[float]],
        n_results: int = 5
    ) -> dict:
        """Query the collection for similar documents asynchronously"""
        self._ensure_initialized()
        try:
            logger.debug(f"Querying ChromaDB for {n_results} results")
            results = await asyncio.to_thread(
                self._query_sync,
                query_embeddings,
                n_results
            )
            num_results = len(results.get('documents', [[]])[0])
            logger.info(f"Retrieved {num_results} results from ChromaDB")
            return results
        except Exception as e:
            logger.error(f"Error querying ChromaDB: {e}", exc_info=True)
            raise
    
    def get_collection_info(self) -> dict:
        """Get collection information"""
        if not self.is_available():
            return {"count": 0, "name": "unknown", "status": "unavailable"}
        try:
            count = self.collection.count()
            return {
                "count": count,
                "name": self.collection.name,
                "status": "available"
            }
        except Exception as e:
            logger.error(f"Error getting collection info: {e}", exc_info=True)
            return {"count": 0, "name": "unknown", "status": "error"}


# Global ChromaDB service instance
chromadb_service = ChromaDBService()

