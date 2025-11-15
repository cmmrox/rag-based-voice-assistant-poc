"""
OpenAI Realtime API constants.

Centralized configuration for OpenAI Realtime API integration,
including model names, voices, and API endpoints.
"""

# OpenAI Realtime API model identifier
# This is the latest GPT-4 Realtime model with audio capabilities
REALTIME_MODEL = "gpt-4o-realtime-preview-2024-10-01"

# Default voice for text-to-speech
# Available voices: alloy, echo, fable, onyx, nova, shimmer, marin
DEFAULT_VOICE = "marin"

# OpenAI Realtime API base URL
REALTIME_API_URL = "https://api.openai.com/v1/realtime"

# Supported audio formats
SUPPORTED_AUDIO_FORMATS = ["pcm16", "g711_ulaw", "g711_alaw"]

# Default audio format for input and output
DEFAULT_AUDIO_FORMAT = "pcm16"
