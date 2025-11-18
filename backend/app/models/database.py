import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID, TSVECTOR
from app.services.database import Base


class Note(Base):
    """
    SQLAlchemy model for notes table.

    Supports full-text search using PostgreSQL tsvector.
    """

    __tablename__ = "notes"

    # Primary key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False
    )

    # Note content
    title = Column(String(255), nullable=False, index=True)
    content = Column(Text, nullable=False)

    # Full-text search vector (automatically updated by trigger)
    search_vector = Column(TSVECTOR)

    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Indexes
    __table_args__ = (
        # GIN index for full-text search
        Index('notes_search_idx', 'search_vector', postgresql_using='gin'),
    )

    def __repr__(self):
        return f"<Note(id={self.id}, title='{self.title[:30]}...')>"

    def to_dict(self):
        """Convert model to dictionary for JSON serialization"""
        return {
            "id": str(self.id),
            "title": self.title,
            "content": self.content,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
