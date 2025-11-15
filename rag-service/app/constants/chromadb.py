"""
ChromaDB configuration constants.

Settings for ChromaDB vector database operations including
collection names, batch sizes, and similarity thresholds.
"""

# ChromaDB collection name for knowledge base
# All documents and embeddings are stored in this collection
COLLECTION_NAME = "knowledge_base"

# Batch size for adding documents to ChromaDB
# Larger batches improve performance but use more memory
BATCH_SIZE = 1000

# Default number of results to return from similarity search
# This can be overridden per query
DEFAULT_N_RESULTS = 5

# Similarity threshold for filtering results
# Results with similarity below this threshold are filtered out
# Range: 0.0 to 1.0, where 1.0 is identical and 0.0 is completely different
SIMILARITY_THRESHOLD = 0.7

# Maximum number of results to consider
# Even if user requests more, we cap at this limit
MAX_N_RESULTS = 20

# ChromaDB metadata fields
METADATA_SOURCE_KEY = "source"
METADATA_CHUNK_ID_KEY = "chunk_id"
METADATA_TOTAL_CHUNKS_KEY = "total_chunks"
