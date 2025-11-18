"""
Database service for notes operations.

Provides CRUD operations and full-text search for notes.
"""

import logging
from typing import List, Optional
from uuid import UUID
from sqlalchemy import select, delete, func, text
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.database import Note
from app.models.notes_schemas import NoteCreate, NoteUpdate
from app.constants.notes import MAX_SEARCH_RESULTS

logger = logging.getLogger(__name__)


async def create_note(db: AsyncSession, note_data: NoteCreate) -> Note:
    """
    Create a new note in the database.

    Args:
        db: Database session
        note_data: Note creation data

    Returns:
        Created Note object

    Raises:
        Exception: If database operation fails
    """
    try:
        note = Note(
            title=note_data.title,
            content=note_data.content
        )

        db.add(note)
        await db.commit()
        await db.refresh(note)

        logger.info(f"Created note: {note.id}")
        return note

    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating note: {e}", exc_info=True)
        raise


async def get_note(db: AsyncSession, note_id: UUID) -> Optional[Note]:
    """
    Get a note by ID.

    Args:
        db: Database session
        note_id: UUID of the note

    Returns:
        Note object if found, None otherwise
    """
    try:
        result = await db.execute(
            select(Note).where(Note.id == note_id)
        )
        note = result.scalar_one_or_none()

        if note:
            logger.info(f"Retrieved note: {note_id}")
        else:
            logger.info(f"Note not found: {note_id}")

        return note

    except Exception as e:
        logger.error(f"Error retrieving note {note_id}: {e}", exc_info=True)
        raise


async def list_notes(db: AsyncSession, limit: Optional[int] = None) -> List[Note]:
    """
    List all notes, ordered by creation date (newest first).

    Args:
        db: Database session
        limit: Optional limit on number of results

    Returns:
        List of Note objects
    """
    try:
        query = select(Note).order_by(Note.created_at.desc())

        if limit:
            query = query.limit(limit)

        result = await db.execute(query)
        notes = result.scalars().all()

        logger.info(f"Retrieved {len(notes)} notes")
        return list(notes)

    except Exception as e:
        logger.error(f"Error listing notes: {e}", exc_info=True)
        raise


async def update_note(
    db: AsyncSession,
    note_id: UUID,
    note_data: NoteUpdate
) -> Optional[Note]:
    """
    Update an existing note.

    Args:
        db: Database session
        note_id: UUID of the note to update
        note_data: Update data (fields with None are not updated)

    Returns:
        Updated Note object if found, None otherwise

    Raises:
        Exception: If database operation fails
    """
    try:
        # Get existing note
        result = await db.execute(
            select(Note).where(Note.id == note_id)
        )
        note = result.scalar_one_or_none()

        if not note:
            logger.info(f"Note not found for update: {note_id}")
            return None

        # Update fields if provided
        if note_data.title is not None:
            note.title = note_data.title

        if note_data.content is not None:
            note.content = note_data.content

        await db.commit()
        await db.refresh(note)

        logger.info(f"Updated note: {note_id}")
        return note

    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating note {note_id}: {e}", exc_info=True)
        raise


async def delete_note(db: AsyncSession, note_id: UUID) -> bool:
    """
    Delete a note by ID.

    Args:
        db: Database session
        note_id: UUID of the note to delete

    Returns:
        True if note was deleted, False if not found

    Raises:
        Exception: If database operation fails
    """
    try:
        result = await db.execute(
            delete(Note).where(Note.id == note_id)
        )
        await db.commit()

        deleted = result.rowcount > 0

        if deleted:
            logger.info(f"Deleted note: {note_id}")
        else:
            logger.info(f"Note not found for deletion: {note_id}")

        return deleted

    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting note {note_id}: {e}", exc_info=True)
        raise


async def search_notes(
    db: AsyncSession,
    query: str,
    limit: int = MAX_SEARCH_RESULTS
) -> List[Note]:
    """
    Search notes using PostgreSQL full-text search.

    Searches both title and content fields using the search_vector.

    Args:
        db: Database session
        query: Search query text
        limit: Maximum number of results (default: MAX_SEARCH_RESULTS)

    Returns:
        List of matching Note objects, ordered by relevance

    Note:
        Requires search_vector column to be populated by database trigger.
        Uses PostgreSQL's to_tsquery for query parsing.
    """
    try:
        # Use PostgreSQL full-text search with ranking
        # to_tsquery with 'english' configuration for English language support
        search_query = select(Note).where(
            Note.search_vector.op('@@')(func.to_tsquery('english', query))
        ).order_by(
            # Order by relevance (rank)
            func.ts_rank(Note.search_vector, func.to_tsquery('english', query)).desc()
        ).limit(limit)

        result = await db.execute(search_query)
        notes = result.scalars().all()

        logger.info(f"Search for '{query}' returned {len(notes)} results")
        return list(notes)

    except Exception as e:
        # If full-text search fails, fall back to simple ILIKE search
        logger.warning(f"Full-text search failed, falling back to ILIKE: {e}")
        
        # Rollback the failed transaction before attempting fallback query
        await db.rollback()

        try:
            # Simple case-insensitive search on title and content
            pattern = f"%{query}%"
            fallback_query = select(Note).where(
                (Note.title.ilike(pattern)) | (Note.content.ilike(pattern))
            ).order_by(Note.created_at.desc()).limit(limit)

            result = await db.execute(fallback_query)
            notes = result.scalars().all()

            logger.info(f"Fallback search for '{query}' returned {len(notes)} results")
            return list(notes)

        except Exception as fallback_error:
            logger.error(f"Fallback search also failed: {fallback_error}", exc_info=True)
            raise
