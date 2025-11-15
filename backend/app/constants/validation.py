"""
Validation constants for request validation.

Defines maximum sizes, limits, and validation rules for incoming requests
to ensure system stability and prevent abuse.
"""

# Maximum SDP (Session Description Protocol) size in bytes
# SDP messages should typically be under 10KB
MAX_SDP_SIZE_BYTES = 10 * 1024  # 10KB

# Maximum WebSocket message size in bytes
# Prevents memory exhaustion from oversized messages
MAX_MESSAGE_SIZE_BYTES = 1024 * 1024  # 1MB

# Required SDP fields for validation
# These fields must be present in a valid SDP message
REQUIRED_SDP_FIELDS = ["v=", "m="]

# Maximum session ID length
# UUIDs are 36 characters, add buffer for future formats
MAX_SESSION_ID_LENGTH = 64

# Maximum function call query length
# Prevents excessively long RAG queries
MAX_QUERY_LENGTH = 10000  # 10K characters
