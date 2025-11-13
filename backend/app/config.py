import os
try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # OpenAI Configuration
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    
    # Server Configuration
    backend_port: int = int(os.getenv("BACKEND_PORT", "8000"))
    
    # RAG Service Configuration
    rag_service_url: str = os.getenv("RAG_SERVICE_URL", "http://rag-service:8000")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

