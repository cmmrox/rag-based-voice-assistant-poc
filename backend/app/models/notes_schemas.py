"""
Pydantic schemas for notes feature.

Request and response models for notes operations and function calling.
"""

from typing import Optional, List, Literal
from datetime import datetime
from pydantic import BaseModel, Field, validator
from app.constants.notes import MAX_TITLE_LENGTH, MAX_CONTENT_LENGTH


# ============================================================================
# Base Note Models
# ============================================================================

class NoteBase(BaseModel):
    """Base model with common note fields"""
    title: str = Field(..., description="Note title", max_length=MAX_TITLE_LENGTH)
    content: str = Field(..., description="Note content", max_length=MAX_CONTENT_LENGTH)

    @validator('title')
    def title_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip()

    @validator('content')
    def content_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Content cannot be empty')
        return v.strip()


class NoteCreate(NoteBase):
    """Model for creating a new note"""
    pass


class NoteUpdate(BaseModel):
    """Model for updating an existing note (all fields optional)"""
    title: Optional[str] = Field(None, description="Note title", max_length=MAX_TITLE_LENGTH)
    content: Optional[str] = Field(None, description="Note content", max_length=MAX_CONTENT_LENGTH)

    @validator('title')
    def title_not_empty(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError('Title cannot be empty')
        return v.strip() if v else None

    @validator('content')
    def content_not_empty(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError('Content cannot be empty')
        return v.strip() if v else None


class NoteResponse(BaseModel):
    """Model for note API response"""
    id: str = Field(..., description="Note UUID")
    title: str = Field(..., description="Note title")
    content: str = Field(..., description="Note content")
    created_at: str = Field(..., description="Creation timestamp (ISO 8601)")
    updated_at: str = Field(..., description="Last update timestamp (ISO 8601)")

    class Config:
        from_attributes = True  # For SQLAlchemy model conversion


# ============================================================================
# Function Calling Models
# ============================================================================

class NotesArguments(BaseModel):
    """Arguments for manage_notes function"""
    action: Literal["create", "list", "search", "update", "delete"] = Field(
        ...,
        description="Action to perform on notes"
    )
    title: Optional[str] = Field(None, description="Note title (for create/update)")
    content: Optional[str] = Field(None, description="Note content (for create/update)")
    note_id: Optional[str] = Field(None, description="Note ID (for update/delete/specific list)")
    query: Optional[str] = Field(None, description="Search query (for search)")


class NotesData(BaseModel):
    """Data wrapper for function result"""
    notes: List[NoteResponse] = Field(default_factory=list, description="List of notes")
    count: int = Field(default=0, description="Number of notes returned")


class NotesFunctionRequest(BaseModel):
    """Request model for notes function call"""
    call_id: str = Field(..., description="Unique identifier for the function call")
    function_name: str = Field(..., description="Name of the function to execute")
    arguments: NotesArguments = Field(..., description="Function arguments")


class NotesFunctionResult(BaseModel):
    """Result model for notes function call"""
    success: bool = Field(..., description="Whether the function call succeeded")
    message: str = Field(default="", description="Success or error message")
    data: Optional[NotesData] = Field(None, description="Notes data (if successful)")
    error: Optional[str] = Field(None, description="Error message (if failed)")


class NotesFunctionResponse(BaseModel):
    """Response model for notes function call"""
    call_id: str = Field(..., description="Unique identifier for the function call")
    function_name: str = Field(..., description="Name of the function executed")
    result: NotesFunctionResult


# ============================================================================
# Search Models
# ============================================================================

class NoteSearchRequest(BaseModel):
    """Request model for note search"""
    query: str = Field(..., description="Search query")
    limit: Optional[int] = Field(10, description="Maximum number of results", ge=1, le=100)

    @validator('query')
    def query_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Search query cannot be empty')
        return v.strip()
