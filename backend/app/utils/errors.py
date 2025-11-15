"""
Standardized error handling utilities.

Provides consistent error parsing, formatting, and handling
across the backend service.
"""

import logging
from typing import Dict, Any, Optional
import httpx

logger = logging.getLogger(__name__)


class OpenAIErrorHandler:
    """
    Handles and parses errors from OpenAI Realtime API.

    Provides standardized error parsing for different error response formats
    from the OpenAI API, including JSON errors and plain text errors.
    """

    @staticmethod
    def parse_error_response(response: httpx.Response) -> str:
        """
        Parse error message from OpenAI API response.

        Args:
            response: HTTP response from OpenAI API

        Returns:
            Parsed error message string
        """
        try:
            # Try to parse as JSON first
            error_data = response.json()

            # Check for different error formats
            if isinstance(error_data, dict):
                # Format 1: {"error": {"message": "...", "type": "...", "code": "..."}}
                if "error" in error_data and isinstance(error_data["error"], dict):
                    error_obj = error_data["error"]
                    message = error_obj.get("message", "Unknown error")
                    error_type = error_obj.get("type", "")
                    code = error_obj.get("code", "")

                    if error_type or code:
                        return f"{message} (type: {error_type}, code: {code})"
                    return message

                # Format 2: {"error": "error message string"}
                if "error" in error_data and isinstance(error_data["error"], str):
                    return error_data["error"]

                # Format 3: {"message": "error message"}
                if "message" in error_data:
                    return error_data["message"]

            # If we can't parse specific fields, return the whole JSON
            return str(error_data)

        except (ValueError, KeyError) as e:
            # If JSON parsing fails, try to get text content
            try:
                text_content = response.text
                if text_content:
                    return text_content[:500]  # Limit length
            except Exception:
                pass

            # Fallback to generic error
            return f"HTTP {response.status_code}: {response.reason_phrase}"


def handle_http_error(
    response: httpx.Response,
    context: str = "HTTP request"
) -> Dict[str, Any]:
    """
    Handle HTTP error responses in a standardized way.

    Args:
        response: HTTP response object
        context: Description of what operation failed (for logging)

    Returns:
        Dictionary with error information
    """
    error_message = OpenAIErrorHandler.parse_error_response(response)

    logger.error(
        f"{context} failed with status {response.status_code}: {error_message}"
    )

    return {
        "error": error_message,
        "status_code": response.status_code,
        "context": context,
    }


def handle_timeout_error(
    error: Exception,
    context: str = "Operation"
) -> Dict[str, Any]:
    """
    Handle timeout errors in a standardized way.

    Args:
        error: The timeout exception
        context: Description of what operation timed out

    Returns:
        Dictionary with error information
    """
    error_message = f"{context} timed out: {str(error)}"
    logger.error(error_message)

    return {
        "error": error_message,
        "error_type": "timeout",
        "context": context,
    }


def handle_connection_error(
    error: Exception,
    context: str = "Connection",
    service_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Handle connection errors in a standardized way.

    Args:
        error: The connection exception
        context: Description of what connection failed
        service_name: Name of the service that couldn't be reached

    Returns:
        Dictionary with error information
    """
    if service_name:
        error_message = f"Failed to connect to {service_name}: {str(error)}"
    else:
        error_message = f"{context} failed: {str(error)}"

    logger.error(error_message)

    return {
        "error": error_message,
        "error_type": "connection",
        "context": context,
        "service": service_name,
    }


def create_error_response(
    message: str,
    status_code: int = 500,
    details: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create a standardized error response dictionary.

    Args:
        message: Human-readable error message
        status_code: HTTP status code
        details: Optional additional error details

    Returns:
        Standardized error response dictionary
    """
    response = {
        "error": message,
        "status_code": status_code,
    }

    if details:
        response["details"] = details

    return response
