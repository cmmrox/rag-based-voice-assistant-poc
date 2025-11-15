"""
Backend utility modules.

Provides reusable utility functions for error handling, logging,
validation, and other cross-cutting concerns.
"""

from .errors import (
    OpenAIErrorHandler,
    handle_http_error,
    handle_timeout_error,
    handle_connection_error,
)
from .validators import (
    validate_sdp_format,
    validate_session_id,
    validate_function_call_message,
)
from .logging_config import setup_logging

__all__ = [
    # Error handling
    'OpenAIErrorHandler',
    'handle_http_error',
    'handle_timeout_error',
    'handle_connection_error',
    # Validators
    'validate_sdp_format',
    'validate_session_id',
    'validate_function_call_message',
    # Logging
    'setup_logging',
]
