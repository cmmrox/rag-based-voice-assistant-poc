"""
OpenAI embedding model configuration constants.

Settings for OpenAI text embedding generation including
model selection, dimensions, and request limits.
"""

# OpenAI embedding model
# text-embedding-3-small: Fast, cost-effective, 1536 dimensions
# text-embedding-3-large: Higher quality, 3072 dimensions, more expensive
EMBEDDING_MODEL = "text-embedding-3-small"

# Embedding vector dimensions for the selected model
# text-embedding-3-small: 1536
# text-embedding-3-large: 3072
EMBEDDING_DIMENSIONS = 1536

# Maximum tokens per OpenAI embedding API request
# API limit is 8191 tokens per request for text-embedding-3-small
MAX_TOKENS_PER_REQUEST = 8000  # Leave buffer for safety

# Maximum number of texts to embed in a single batch
# OpenAI API can handle arrays of texts, but we limit batch size
MAX_BATCH_SIZE = 100
