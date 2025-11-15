"""
RAG service constants module.

Centralized constant definitions for the RAG service,
including ChromaDB, embedding, chunking, and limit configurations.
"""

from .chromadb import (
    COLLECTION_NAME,
    BATCH_SIZE,
    DEFAULT_N_RESULTS,
    SIMILARITY_THRESHOLD,
)
from .embedding import (
    EMBEDDING_MODEL,
    EMBEDDING_DIMENSIONS,
    MAX_TOKENS_PER_REQUEST,
)
from .chunking import (
    CHUNK_SIZE_TOKENS,
    CHUNK_OVERLAP_TOKENS,
    CHARS_PER_TOKEN,
    MIN_CHUNK_SIZE,
)
from .limits import (
    MAX_FILE_SIZE_MB,
    MAX_FILE_SIZE_BYTES,
    EMBEDDING_REQUEST_TIMEOUT,
    CHROMADB_REQUEST_TIMEOUT,
)

__all__ = [
    # ChromaDB constants
    'COLLECTION_NAME',
    'BATCH_SIZE',
    'DEFAULT_N_RESULTS',
    'SIMILARITY_THRESHOLD',
    # Embedding constants
    'EMBEDDING_MODEL',
    'EMBEDDING_DIMENSIONS',
    'MAX_TOKENS_PER_REQUEST',
    # Chunking constants
    'CHUNK_SIZE_TOKENS',
    'CHUNK_OVERLAP_TOKENS',
    'CHARS_PER_TOKEN',
    'MIN_CHUNK_SIZE',
    # Limit constants
    'MAX_FILE_SIZE_MB',
    'MAX_FILE_SIZE_BYTES',
    'EMBEDDING_REQUEST_TIMEOUT',
    'CHROMADB_REQUEST_TIMEOUT',
]
