"""
Document chunking configuration constants.

Settings for splitting documents into chunks for embedding and retrieval,
including chunk sizes, overlaps, and tokenization parameters.
"""

# Target chunk size in tokens
# Larger chunks: More context, but less granular retrieval
# Smaller chunks: More precise, but may lose context
CHUNK_SIZE_TOKENS = 500

# Overlap between chunks in tokens
# Overlap ensures context isn't lost at chunk boundaries
# Typically 10-20% of chunk size
CHUNK_OVERLAP_TOKENS = 100

# Approximate characters per token (for estimation)
# English text: ~4 characters per token
# This is used to estimate token counts without actual tokenization
CHARS_PER_TOKEN = 4

# Minimum chunk size in characters
# Chunks smaller than this are discarded as too short
MIN_CHUNK_SIZE = 50

# Maximum chunk size in characters
# Calculated from token limits
MAX_CHUNK_SIZE_CHARS = CHUNK_SIZE_TOKENS * CHARS_PER_TOKEN

# Maximum overlap in characters
MAX_OVERLAP_CHARS = CHUNK_OVERLAP_TOKENS * CHARS_PER_TOKEN
