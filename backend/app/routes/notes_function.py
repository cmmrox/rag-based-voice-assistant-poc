"""
REST API endpoint for notes function calling.

Handles function call requests from the frontend and routes them
to appropriate database operations.
"""

import logging
from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.database import get_db
from app.services import notes_db
from app.models.notes_schemas import (
    NotesFunctionRequest,
    NotesFunctionResponse,
    NotesFunctionResult,
    NotesData,
    NoteResponse,
    NoteCreate,
    NoteUpdate
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/api/notes/function-call", response_model=NotesFunctionResponse)
async def execute_notes_function(
    request: NotesFunctionRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    REST API endpoint for executing notes function calls.

    This endpoint receives function call requests from the frontend,
    performs the requested operation on notes, and returns results.

    Supported actions:
    - create: Create a new note
    - list: List all notes or get specific note by ID
    - search: Search notes using full-text search
    - update: Update an existing note
    - delete: Delete a note

    Args:
        request: NotesFunctionRequest containing call_id, function_name, and arguments
        db: Database session (injected by FastAPI)

    Returns:
        NotesFunctionResponse with the function execution result

    Raises:
        HTTPException: If function name is invalid (400)
    """
    call_id = request.call_id
    function_name = request.function_name
    args = request.arguments

    logger.info(f"Received notes function call: {function_name} action={args.action} (call_id: {call_id})")

    if function_name != "manage_notes":
        logger.warning(f"Unknown function name: {function_name}")
        raise HTTPException(
            status_code=400,
            detail=f"Unknown function: {function_name}"
        )

    # Route to appropriate action handler
    try:
        if args.action == "create":
            return await handle_create(call_id, function_name, args, db)

        elif args.action == "list":
            return await handle_list(call_id, function_name, args, db)

        elif args.action == "search":
            return await handle_search(call_id, function_name, args, db)

        elif args.action == "update":
            return await handle_update(call_id, function_name, args, db)

        elif args.action == "delete":
            return await handle_delete(call_id, function_name, args, db)

        else:
            logger.warning(f"Unknown action: {args.action}")
            return NotesFunctionResponse(
                call_id=call_id,
                function_name=function_name,
                result=NotesFunctionResult(
                    success=False,
                    error=f"Unknown action: {args.action}"
                )
            )

    except Exception as e:
        logger.error(f"Error executing function call: {e}", exc_info=True)
        return NotesFunctionResponse(
            call_id=call_id,
            function_name=function_name,
            result=NotesFunctionResult(
                success=False,
                error=str(e)
            )
        )


async def handle_create(call_id: str, function_name: str, args, db: AsyncSession):
    """Handle create note action"""
    if not args.title or not args.content:
        return NotesFunctionResponse(
            call_id=call_id,
            function_name=function_name,
            result=NotesFunctionResult(
                success=False,
                error="Both title and content are required for creating a note"
            )
        )

    note_data = NoteCreate(title=args.title, content=args.content)
    note = await notes_db.create_note(db, note_data)

    note_response = NoteResponse(
        id=str(note.id),
        title=note.title,
        content=note.content,
        created_at=note.created_at.isoformat(),
        updated_at=note.updated_at.isoformat()
    )

    logger.info(f"Note created successfully: {note.id}")

    return NotesFunctionResponse(
        call_id=call_id,
        function_name=function_name,
        result=NotesFunctionResult(
            success=True,
            message=f"Note created: {note.title}",
            data=NotesData(notes=[note_response], count=1)
        )
    )


async def handle_list(call_id: str, function_name: str, args, db: AsyncSession):
    """Handle list notes action"""
    # If note_id provided, get specific note
    if args.note_id:
        try:
            note_uuid = UUID(args.note_id)
            note = await notes_db.get_note(db, note_uuid)

            if not note:
                return NotesFunctionResponse(
                    call_id=call_id,
                    function_name=function_name,
                    result=NotesFunctionResult(
                        success=False,
                        error=f"Note not found: {args.note_id}"
                    )
                )

            note_response = NoteResponse(
                id=str(note.id),
                title=note.title,
                content=note.content,
                created_at=note.created_at.isoformat(),
                updated_at=note.updated_at.isoformat()
            )

            return NotesFunctionResponse(
                call_id=call_id,
                function_name=function_name,
                result=NotesFunctionResult(
                    success=True,
                    message="Note retrieved",
                    data=NotesData(notes=[note_response], count=1)
                )
            )

        except ValueError:
            return NotesFunctionResponse(
                call_id=call_id,
                function_name=function_name,
                result=NotesFunctionResult(
                    success=False,
                    error=f"Invalid note ID format: {args.note_id}"
                )
            )

    # List all notes
    notes = await notes_db.list_notes(db)

    if not notes:
        return NotesFunctionResponse(
            call_id=call_id,
            function_name=function_name,
            result=NotesFunctionResult(
                success=True,
                message="No notes found",
                data=NotesData(notes=[], count=0)
            )
        )

    note_responses = [
        NoteResponse(
            id=str(note.id),
            title=note.title,
            content=note.content,
            created_at=note.created_at.isoformat(),
            updated_at=note.updated_at.isoformat()
        )
        for note in notes
    ]

    logger.info(f"Listed {len(notes)} notes")

    return NotesFunctionResponse(
        call_id=call_id,
        function_name=function_name,
        result=NotesFunctionResult(
            success=True,
            message=f"Found {len(notes)} note(s)",
            data=NotesData(notes=note_responses, count=len(notes))
        )
    )


async def handle_search(call_id: str, function_name: str, args, db: AsyncSession):
    """Handle search notes action"""
    if not args.query:
        return NotesFunctionResponse(
            call_id=call_id,
            function_name=function_name,
            result=NotesFunctionResult(
                success=False,
                error="Search query is required"
            )
        )

    notes = await notes_db.search_notes(db, args.query)

    if not notes:
        return NotesFunctionResponse(
            call_id=call_id,
            function_name=function_name,
            result=NotesFunctionResult(
                success=True,
                message=f"No notes found matching '{args.query}'",
                data=NotesData(notes=[], count=0)
            )
        )

    note_responses = [
        NoteResponse(
            id=str(note.id),
            title=note.title,
            content=note.content,
            created_at=note.created_at.isoformat(),
            updated_at=note.updated_at.isoformat()
        )
        for note in notes
    ]

    logger.info(f"Search for '{args.query}' returned {len(notes)} results")

    return NotesFunctionResponse(
        call_id=call_id,
        function_name=function_name,
        result=NotesFunctionResult(
            success=True,
            message=f"Found {len(notes)} note(s) matching '{args.query}'",
            data=NotesData(notes=note_responses, count=len(notes))
        )
    )


async def handle_update(call_id: str, function_name: str, args, db: AsyncSession):
    """Handle update note action"""
    if not args.note_id:
        return NotesFunctionResponse(
            call_id=call_id,
            function_name=function_name,
            result=NotesFunctionResult(
                success=False,
                error="Note ID is required for update"
            )
        )

    if not args.title and not args.content:
        return NotesFunctionResponse(
            call_id=call_id,
            function_name=function_name,
            result=NotesFunctionResult(
                success=False,
                error="At least one field (title or content) must be provided for update"
            )
        )

    try:
        note_uuid = UUID(args.note_id)
        note_data = NoteUpdate(title=args.title, content=args.content)
        note = await notes_db.update_note(db, note_uuid, note_data)

        if not note:
            return NotesFunctionResponse(
                call_id=call_id,
                function_name=function_name,
                result=NotesFunctionResult(
                    success=False,
                    error=f"Note not found: {args.note_id}"
                )
            )

        note_response = NoteResponse(
            id=str(note.id),
            title=note.title,
            content=note.content,
            created_at=note.created_at.isoformat(),
            updated_at=note.updated_at.isoformat()
        )

        logger.info(f"Note updated successfully: {note.id}")

        return NotesFunctionResponse(
            call_id=call_id,
            function_name=function_name,
            result=NotesFunctionResult(
                success=True,
                message=f"Note updated: {note.title}",
                data=NotesData(notes=[note_response], count=1)
            )
        )

    except ValueError:
        return NotesFunctionResponse(
            call_id=call_id,
            function_name=function_name,
            result=NotesFunctionResult(
                success=False,
                error=f"Invalid note ID format: {args.note_id}"
            )
        )


async def handle_delete(call_id: str, function_name: str, args, db: AsyncSession):
    """Handle delete note action"""
    if not args.note_id:
        return NotesFunctionResponse(
            call_id=call_id,
            function_name=function_name,
            result=NotesFunctionResult(
                success=False,
                error="Note ID is required for delete"
            )
        )

    try:
        note_uuid = UUID(args.note_id)
        deleted = await notes_db.delete_note(db, note_uuid)

        if not deleted:
            return NotesFunctionResponse(
                call_id=call_id,
                function_name=function_name,
                result=NotesFunctionResult(
                    success=False,
                    error=f"Note not found: {args.note_id}"
                )
            )

        logger.info(f"Note deleted successfully: {note_uuid}")

        return NotesFunctionResponse(
            call_id=call_id,
            function_name=function_name,
            result=NotesFunctionResult(
                success=True,
                message=f"Note deleted: {args.note_id}"
            )
        )

    except ValueError:
        return NotesFunctionResponse(
            call_id=call_id,
            function_name=function_name,
            result=NotesFunctionResult(
                success=False,
                error=f"Invalid note ID format: {args.note_id}"
            )
        )
