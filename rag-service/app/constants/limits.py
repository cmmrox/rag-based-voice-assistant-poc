"""
Request and resource limit constants.

Defines maximum file sizes, timeouts, and other limits to ensure
system stability and prevent resource exhaustion.
"""

# Maximum file size for document upload (in megabytes)
MAX_FILE_SIZE_MB = 50

# Maximum file size in bytes
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

# Timeout for OpenAI embedding API requests (seconds)
# Embedding generation can take time for large batches
EMBEDDING_REQUEST_TIMEOUT = 30

# Timeout for ChromaDB operations (seconds)
# Database operations should be fast, but network can be slow
CHROMADB_REQUEST_TIMEOUT = 10

# Maximum number of concurrent document processing tasks
MAX_CONCURRENT_UPLOADS = 5

# Maximum query length in characters
# Prevents excessively long queries
MAX_QUERY_LENGTH = 10000
