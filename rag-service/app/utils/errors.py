"""
Standardized error handling utilities for RAG service.

Provides consistent error parsing, formatting, and handling
across the RAG service modules.
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


def handle_chromadb_error(
    error: Exception,
    operation: str = "ChromaDB operation"
) -> Dict[str, Any]:
    """
    Handle ChromaDB-related errors in a standardized way.

    Args:
        error: The ChromaDB exception
        operation: Description of what operation failed

    Returns:
        Dictionary with error information
    """
    error_message = f"{operation} failed: {str(error)}"
    logger.error(error_message, exc_info=True)

    return {
        "error": error_message,
        "error_type": "database",
        "operation": operation,
        "details": str(error),
    }


def handle_embedding_error(
    error: Exception,
    operation: str = "Embedding generation"
) -> Dict[str, Any]:
    """
    Handle OpenAI embedding API errors in a standardized way.

    Args:
        error: The embedding API exception
        operation: Description of what operation failed

    Returns:
        Dictionary with error information
    """
    error_message = f"{operation} failed: {str(error)}"
    logger.error(error_message, exc_info=True)

    # Check if it's a timeout error
    error_type = "timeout" if "timeout" in str(error).lower() else "api"

    return {
        "error": error_message,
        "error_type": error_type,
        "operation": operation,
        "details": str(error),
    }


def handle_parsing_error(
    error: Exception,
    file_name: Optional[str] = None,
    operation: str = "Document parsing"
) -> Dict[str, Any]:
    """
    Handle document parsing errors in a standardized way.

    Args:
        error: The parsing exception
        file_name: Name of file being parsed (if applicable)
        operation: Description of what operation failed

    Returns:
        Dictionary with error information
    """
    if file_name:
        error_message = f"{operation} failed for '{file_name}': {str(error)}"
    else:
        error_message = f"{operation} failed: {str(error)}"

    logger.error(error_message, exc_info=True)

    return {
        "error": error_message,
        "error_type": "parsing",
        "operation": operation,
        "file": file_name,
        "details": str(error),
    }


def create_error_response(
    message: str,
    status_code: int = 500,
    error_type: str = "internal",
    details: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create a standardized error response dictionary.

    Args:
        message: Human-readable error message
        status_code: HTTP status code
        error_type: Type of error (api, database, parsing, validation, etc.)
        details: Optional additional error details

    Returns:
        Standardized error response dictionary
    """
    response = {
        "error": message,
        "error_type": error_type,
        "status_code": status_code,
    }

    if details:
        response["details"] = details

    return response


def handle_validation_error(
    field: str,
    message: str,
    value: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Handle input validation errors.

    Args:
        field: Name of the field that failed validation
        message: Description of the validation error
        value: The invalid value (optional, for logging)

    Returns:
        Dictionary with error information
    """
    error_message = f"Validation error for '{field}': {message}"

    if value is not None:
        logger.warning(f"{error_message} (value: {value})")
    else:
        logger.warning(error_message)

    return {
        "error": error_message,
        "error_type": "validation",
        "field": field,
        "message": message,
    }
