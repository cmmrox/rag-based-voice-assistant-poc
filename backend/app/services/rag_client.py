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
    
    async def check_health(self) -> dict:
        """Check RAG service health and connectivity"""
        try:
            url = f"{self.base_url}/health"
            health_timeout = 5.0  # Shorter timeout for health checks
            
            async with httpx.AsyncClient(timeout=health_timeout) as client:
                response = await client.get(url)
                response.raise_for_status()
                result = response.json()
                
                logger.info(f"RAG service health check successful: {result}")
                return {
                    "status": "connected",
                    "url": self.base_url,
                    "details": result
                }
        
        except httpx.TimeoutException:
            logger.warning(f"RAG service health check timeout: {self.base_url}")
            return {
                "status": "unavailable",
                "url": self.base_url,
                "details": {"error": "Connection timeout"}
            }
        except httpx.ConnectError:
            logger.warning(f"RAG service health check connection error: {self.base_url}")
            return {
                "status": "unavailable",
                "url": self.base_url,
                "details": {"error": "Connection refused"}
            }
        except httpx.HTTPStatusError as e:
            logger.warning(f"RAG service health check HTTP error: {e.response.status_code}")
            return {
                "status": "error",
                "url": self.base_url,
                "details": {"error": f"HTTP {e.response.status_code}"}
            }
        except Exception as e:
            logger.error(f"RAG service health check error: {e}", exc_info=True)
            return {
                "status": "error",
                "url": self.base_url,
                "details": {"error": str(e)[:100]}
            }


# Global RAG client instance
rag_client = RAGClient()

