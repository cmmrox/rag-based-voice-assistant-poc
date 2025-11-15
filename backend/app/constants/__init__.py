"""
Backend application constants module.

This module provides centralized constant definitions for the backend service,
improving maintainability and reducing magic values throughout the codebase.
"""

from .openai import (
    REALTIME_MODEL,
    DEFAULT_VOICE,
    REALTIME_API_URL,
)
from .timeouts import (
    RAG_QUERY_TIMEOUT_SECONDS,
    OPENAI_REQUEST_TIMEOUT_SECONDS,
    HEALTH_CHECK_TIMEOUT_SECONDS,
)
from .validation import (
    MAX_SDP_SIZE_BYTES,
    MAX_MESSAGE_SIZE_BYTES,
)

__all__ = [
    # OpenAI constants
    'REALTIME_MODEL',
    'DEFAULT_VOICE',
    'REALTIME_API_URL',
    # Timeout constants
    'RAG_QUERY_TIMEOUT_SECONDS',
    'OPENAI_REQUEST_TIMEOUT_SECONDS',
    'HEALTH_CHECK_TIMEOUT_SECONDS',
    # Validation constants
    'MAX_SDP_SIZE_BYTES',
    'MAX_MESSAGE_SIZE_BYTES',
]
