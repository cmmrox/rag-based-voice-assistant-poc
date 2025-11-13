import logging
import httpx
from typing import Optional
from app.config import settings

logger = logging.getLogger(__name__)


class RAGClient:
    """HTTP client for RAG service"""
    
    def __init__(self):
        self.base_url = settings.rag_service_url
        self.timeout = 30.0
    
    async def query(self, query_text: str) -> Optional[dict]:
        """Query RAG service for relevant context"""
        try:
            url = f"{self.base_url}/api/rag/query"
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    url,
                    json={"query": query_text}
                )
                response.raise_for_status()
                result = response.json()
                
                logger.info(f"RAG query successful: {len(result.get('context', ''))} chars")
                return result
        
        except httpx.TimeoutException:
            logger.error("RAG service timeout")
            return None
        except httpx.HTTPStatusError as e:
            logger.error(f"RAG service HTTP error: {e.response.status_code}")
            return None
        except Exception as e:
            logger.error(f"Error querying RAG service: {e}", exc_info=True)
            return None
    
    async def retrieve_context(self, query_text: str) -> str:
        """Retrieve context from RAG service"""
        result = await self.query(query_text)
        
        if result and result.get("context"):
            return result["context"]
        
        return ""


# Global RAG client instance
rag_client = RAGClient()

