import logging
import asyncio
from typing import List
from openai import OpenAI
from app.config import settings

logger = logging.getLogger(__name__)

# Batch size limit for OpenAI API (max 2048 inputs per request)
MAX_BATCH_SIZE = 2048


class EmbeddingService:
    """Service for generating embeddings using OpenAI API"""
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = "text-embedding-3-small"  # Using smaller model for POC
    
    def _generate_embedding_sync(self, text: str) -> List[float]:
        """Synchronous helper for generating a single embedding"""
        response = self.client.embeddings.create(
            model=self.model,
            input=text
        )
        return response.data[0].embedding
    
    def _generate_embeddings_batch_sync(self, texts: List[str]) -> List[List[float]]:
        """Synchronous helper for generating embeddings in batch"""
        response = self.client.embeddings.create(
            model=self.model,
            input=texts
        )
        return [item.embedding for item in response.data]
    
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        try:
            logger.debug(f"Generating embedding for text: {len(text)} chars")
            embedding = await asyncio.to_thread(self._generate_embedding_sync, text)
            logger.debug(f"Successfully generated embedding: {len(embedding)} dimensions")
            return embedding
        
        except Exception as e:
            logger.error(f"Error generating embedding: {e}", exc_info=True)
            raise
    
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts with progress logging and batching"""
        try:
            total_texts = len(texts)
            logger.info(f"Starting embedding generation for {total_texts} texts using model: {self.model}")
            
            all_embeddings = []
            
            # Process in batches to avoid API limits and provide progress updates
            batch_size = min(MAX_BATCH_SIZE, total_texts)
            num_batches = (total_texts + batch_size - 1) // batch_size
            
            for batch_idx in range(num_batches):
                start_idx = batch_idx * batch_size
                end_idx = min(start_idx + batch_size, total_texts)
                batch_texts = texts[start_idx:end_idx]
                
                logger.info(f"Processing embedding batch {batch_idx + 1}/{num_batches} "
                          f"(chunks {start_idx + 1}-{end_idx} of {total_texts})")
                
                # Run the blocking API call in a thread pool
                batch_embeddings = await asyncio.to_thread(
                    self._generate_embeddings_batch_sync,
                    batch_texts
                )
                
                all_embeddings.extend(batch_embeddings)
                logger.info(f"Completed batch {batch_idx + 1}/{num_batches}: "
                          f"generated {len(batch_embeddings)} embeddings "
                          f"({len(all_embeddings)}/{total_texts} total)")
            
            logger.info(f"Successfully generated all {len(all_embeddings)} embeddings")
            return all_embeddings
        
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}", exc_info=True)
            raise


# Global embedding service instance
embedding_service = EmbeddingService()

