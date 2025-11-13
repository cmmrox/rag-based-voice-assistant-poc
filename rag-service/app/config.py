import os
try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings


class Settings(BaseSettings):
    """RAG Service settings"""
    
    # OpenAI Configuration
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    
    # ChromaDB Configuration
    chromadb_host: str = os.getenv("CHROMADB_HOST", "chromadb")
    chromadb_port: int = int(os.getenv("CHROMADB_PORT", "8000"))
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

