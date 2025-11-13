import logging
import chromadb
from chromadb.config import Settings
from app.config import settings

logger = logging.getLogger(__name__)


class ChromaDBService:
    """ChromaDB service for vector storage and retrieval"""
    
    def __init__(self):
        self.client = None
        self.collection = None
        self._initialize()
    
    def _initialize(self):
        """Initialize ChromaDB client and collection"""
        try:
            # Connect to ChromaDB
            self.client = chromadb.HttpClient(
                host=settings.chromadb_host,
                port=settings.chromadb_port
            )
            
            # Create or get collection
            self.collection = self.client.get_or_create_collection(
                name="knowledge_base",
                metadata={"hnsw:space": "cosine"}  # Cosine similarity
            )
            
            logger.info("ChromaDB initialized successfully")
        
        except Exception as e:
            logger.error(f"Error initializing ChromaDB: {e}", exc_info=True)
            # Fallback to in-memory client for development
            try:
                self.client = chromadb.Client()
                self.collection = self.client.get_or_create_collection(
                    name="knowledge_base",
                    metadata={"hnsw:space": "cosine"}
                )
                logger.info("Using in-memory ChromaDB client")
            except Exception as e2:
                logger.error(f"Error initializing in-memory ChromaDB: {e2}", exc_info=True)
                raise
    
    def add_documents(
        self,
        documents: list[str],
        embeddings: list[list[float]],
        metadatas: list[dict],
        ids: list[str]
    ):
        """Add documents to the collection"""
        try:
            self.collection.add(
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"Added {len(documents)} documents to ChromaDB")
        except Exception as e:
            logger.error(f"Error adding documents to ChromaDB: {e}", exc_info=True)
            raise
    
    def query(
        self,
        query_embeddings: list[list[float]],
        n_results: int = 5
    ) -> dict:
        """Query the collection for similar documents"""
        try:
            results = self.collection.query(
                query_embeddings=query_embeddings,
                n_results=n_results
            )
            logger.info(f"Retrieved {len(results.get('documents', [[]])[0])} results from ChromaDB")
            return results
        except Exception as e:
            logger.error(f"Error querying ChromaDB: {e}", exc_info=True)
            raise
    
    def get_collection_info(self) -> dict:
        """Get collection information"""
        try:
            count = self.collection.count()
            return {
                "count": count,
                "name": self.collection.name
            }
        except Exception as e:
            logger.error(f"Error getting collection info: {e}", exc_info=True)
            return {"count": 0, "name": "unknown"}


# Global ChromaDB service instance
chromadb_service = ChromaDBService()

