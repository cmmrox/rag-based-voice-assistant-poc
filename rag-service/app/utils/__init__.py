"""
RAG service utility modules.

Provides reusable utility functions for error handling, logging,
and other cross-cutting concerns specific to the RAG service.
"""

from .errors import (
    handle_chromadb_error,
    handle_embedding_error,
    handle_parsing_error,
    create_error_response,
)
from .logging_config import setup_logging, get_logger

__all__ = [
    # Error handling
    'handle_chromadb_error',
    'handle_embedding_error',
    'handle_parsing_error',
    'create_error_response',
    # Logging
    'setup_logging',
    'get_logger',
]
