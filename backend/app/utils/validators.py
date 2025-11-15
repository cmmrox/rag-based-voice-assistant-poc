"""
Input validation utilities.

Provides validation functions for requests to ensure data integrity
and prevent invalid inputs from reaching business logic.
"""

import logging
import re
from typing import Tuple, Optional, Dict, Any

from ..constants.validation import (
    MAX_SDP_SIZE_BYTES,
    REQUIRED_SDP_FIELDS,
    MAX_SESSION_ID_LENGTH,
    MAX_QUERY_LENGTH,
)

logger = logging.getLogger(__name__)


def validate_sdp_format(sdp: str) -> Tuple[bool, Optional[str]]:
    """
    Validate SDP (Session Description Protocol) format.

    Checks that the SDP string contains required fields and is properly formatted.

    Args:
        sdp: SDP string to validate

    Returns:
        Tuple of (is_valid, error_message)
        - is_valid: True if SDP is valid, False otherwise
        - error_message: None if valid, error description if invalid
    """
    # Check if SDP is provided
    if not sdp or not isinstance(sdp, str):
        return False, "SDP is required and must be a string"

    # Check SDP size
    sdp_size = len(sdp.encode('utf-8'))
    if sdp_size > MAX_SDP_SIZE_BYTES:
        return False, f"SDP size ({sdp_size} bytes) exceeds maximum ({MAX_SDP_SIZE_BYTES} bytes)"

    # Check for required SDP fields
    for field in REQUIRED_SDP_FIELDS:
        if field not in sdp:
            return False, f"SDP is missing required field: {field}"

    # Basic format validation - SDP should start with v=
    if not sdp.strip().startswith('v='):
        return False, "SDP must start with version field (v=)"

    # Check for media description
    if 'm=' not in sdp:
        return False, "SDP must contain media description (m=)"

    logger.debug(f"SDP validation passed, size: {sdp_size} bytes")
    return True, None


def validate_session_id(session_id: str) -> Tuple[bool, Optional[str]]:
    """
    Validate session ID format.

    Checks that the session ID is a valid format (typically UUID).

    Args:
        session_id: Session ID to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check if session ID is provided
    if not session_id or not isinstance(session_id, str):
        return False, "Session ID is required and must be a string"

    # Check length
    if len(session_id) > MAX_SESSION_ID_LENGTH:
        return False, f"Session ID too long (max {MAX_SESSION_ID_LENGTH} characters)"

    # Check for valid characters (alphanumeric, hyphens, underscores)
    if not re.match(r'^[a-zA-Z0-9_-]+$', session_id):
        return False, "Session ID contains invalid characters"

    return True, None


def validate_function_call_message(message: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    Validate function call message format.

    Checks that a WebSocket message for function calling has all required fields.

    Args:
        message: Message dictionary to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check message is a dictionary
    if not isinstance(message, dict):
        return False, "Message must be a dictionary"

    # Check required fields
    required_fields = ["type", "call_id", "function_name", "arguments"]
    for field in required_fields:
        if field not in message:
            return False, f"Message missing required field: {field}"

    # Validate message type
    if message["type"] != "function_call":
        return False, f"Invalid message type: {message['type']}"

    # Validate call_id
    if not isinstance(message["call_id"], str) or not message["call_id"]:
        return False, "call_id must be a non-empty string"

    # Validate function_name
    if not isinstance(message["function_name"], str) or not message["function_name"]:
        return False, "function_name must be a non-empty string"

    # Validate arguments
    if not isinstance(message["arguments"], dict):
        return False, "arguments must be a dictionary"

    # For RAG function, validate query field
    if message["function_name"] == "rag_knowledge":
        if "query" not in message["arguments"]:
            return False, "RAG function requires 'query' in arguments"

        query = message["arguments"]["query"]
        if not isinstance(query, str) or not query.strip():
            return False, "RAG query must be a non-empty string"

        if len(query) > MAX_QUERY_LENGTH:
            return False, f"Query too long (max {MAX_QUERY_LENGTH} characters)"

    return True, None


def validate_content_type(content_type: str, expected: str) -> Tuple[bool, Optional[str]]:
    """
    Validate HTTP Content-Type header.

    Args:
        content_type: Actual content type from request
        expected: Expected content type

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not content_type:
        return False, f"Content-Type header missing, expected: {expected}"

    # Content-Type may include charset, so check if it starts with expected type
    if not content_type.startswith(expected):
        return False, f"Invalid Content-Type: {content_type}, expected: {expected}"

    return True, None
