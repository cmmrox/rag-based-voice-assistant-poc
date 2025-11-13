from pydantic import BaseModel
from typing import List, Optional


class DocumentIngestRequest(BaseModel):
    """Request model for document ingestion"""
    filename: str
    content: bytes


class DocumentIngestResponse(BaseModel):
    """Response model for document ingestion"""
    status: str
    chunks: int
    message: Optional[str] = None


class QueryRequest(BaseModel):
    """Request model for RAG query"""
    query: str


class QueryResponse(BaseModel):
    """Response model for RAG query"""
    context: str
    sources: List[dict]
    message: Optional[str] = None

