import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.services.rag_client import rag_client

logger = logging.getLogger(__name__)

router = APIRouter()


class FunctionCallRequest(BaseModel):
    """Request model for RAG function call"""
    call_id: str = Field(..., description="Unique identifier for the function call")
    function_name: str = Field(..., description="Name of the function to execute")
    arguments: dict = Field(..., description="Function arguments")


class FunctionCallResult(BaseModel):
    """Result model for RAG function call"""
    context: str = Field(default="", description="Retrieved context from knowledge base")
    sources: list = Field(default_factory=list, description="Source documents")
    success: bool = Field(..., description="Whether the function call succeeded")
    message: str = Field(default="", description="Optional message")
    error: str = Field(default="", description="Error message if failed")


class FunctionCallResponse(BaseModel):
    """Response model for RAG function call"""
    call_id: str = Field(..., description="Unique identifier for the function call")
    function_name: str = Field(..., description="Name of the function executed")
    result: FunctionCallResult


@router.post("/api/rag/function-call", response_model=FunctionCallResponse)
async def execute_rag_function(request: FunctionCallRequest):
    """
    REST API endpoint for executing RAG function calls.

    This endpoint receives function call requests from the frontend,
    queries the RAG service, and returns results.

    Args:
        request: FunctionCallRequest containing call_id, function_name, and arguments

    Returns:
        FunctionCallResponse with the function execution result

    Raises:
        HTTPException: If function execution fails or invalid function name
    """
    call_id = request.call_id
    function_name = request.function_name
    arguments = request.arguments

    logger.info(f"Received function call request: {function_name} (call_id: {call_id})")

    if function_name == "rag_knowledge":
        try:
            query = arguments.get("query", "")
            if not query:
                raise ValueError("Query parameter is required")

            # Query RAG service
            rag_result = await rag_client.query(query)

            if rag_result and rag_result.get("context"):
                context = rag_result.get("context", "")
                sources = rag_result.get("sources", [])

                logger.info(f"RAG query successful: {len(context)} chars from {len(sources)} sources")

                return FunctionCallResponse(
                    call_id=call_id,
                    function_name=function_name,
                    result=FunctionCallResult(
                        context=context,
                        sources=sources,
                        success=True
                    )
                )
            else:
                # No context found
                logger.info(f"No RAG context found for query: {query}")
                return FunctionCallResponse(
                    call_id=call_id,
                    function_name=function_name,
                    result=FunctionCallResult(
                        context="",
                        sources=[],
                        success=True,
                        message="No relevant information found in knowledge base"
                    )
                )

        except Exception as e:
            logger.error(f"Error executing function call: {e}", exc_info=True)
            return FunctionCallResponse(
                call_id=call_id,
                function_name=function_name,
                result=FunctionCallResult(
                    success=False,
                    error=str(e)
                )
            )
    else:
        logger.warning(f"Unknown function name: {function_name}")
        raise HTTPException(
            status_code=400,
            detail=f"Unknown function: {function_name}"
        )
