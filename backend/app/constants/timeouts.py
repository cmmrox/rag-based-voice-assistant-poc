"""
Timeout constants for external service calls.

Defines timeout values for HTTP requests and service interactions
to prevent hanging requests and ensure responsive error handling.
"""

# RAG service query timeout (in seconds)
# How long to wait for RAG service to return query results
RAG_QUERY_TIMEOUT_SECONDS = 30

# OpenAI API request timeout (in seconds)
# How long to wait for OpenAI Realtime API responses
OPENAI_REQUEST_TIMEOUT_SECONDS = 60

# Health check timeout (in seconds)
# How long to wait for dependent services during health checks
HEALTH_CHECK_TIMEOUT_SECONDS = 5
