import json
import logging
import urllib.parse
from fastapi import APIRouter, Request, Response
from fastapi.responses import PlainTextResponse
import httpx
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/realtime/session")
async def create_realtime_session(request: Request):
    """
    Create OpenAI Realtime session via unified interface.
    This endpoint forwards SDP data from the browser to OpenAI's /v1/realtime/calls endpoint.
    """
    try:
        # Get SDP from browser (raw body as text)
        sdp = await request.body()
        sdp_text = sdp.decode('utf-8')
        
        logger.info(f"Received SDP offer from client: {len(sdp_text)} bytes")
        
        # Validate SDP format
        if not sdp_text or len(sdp_text.strip()) == 0:
            logger.error("Empty SDP offer received")
            return Response(
                content=json.dumps({"error": "Empty SDP offer"}),
                status_code=400,
                media_type="application/json"
            )
        
        # Basic SDP validation - check for required SDP fields
        if "v=0" not in sdp_text or "m=" not in sdp_text:
            logger.error(f"Invalid SDP format. First 200 chars: {sdp_text[:200]}")
            return Response(
                content=json.dumps({"error": "Invalid SDP format"}),
                status_code=400,
                media_type="application/json"
            )
        
        # Log SDP preview for debugging
        sdp_preview = "\n".join(sdp_text.split("\n")[:5])
        logger.debug(f"SDP preview (first 5 lines):\n{sdp_preview}")
        
        # Extract model and voice from session config for query parameters
        model = "gpt-4o-realtime-preview-2024-10-01"
        voice = "marin"
        
        # Session configuration with RAG function calling support
        # Note: This will be sent via data channel after WebRTC connection is established
        session_config = {
            "type": "realtime",
            "model": model,
            "audio": {
                "output": {
                    "voice": voice
                }
            },
            "tools": [
                {
                    "type": "function",
                    "name": "rag_knowledge",
                    "description": "Retrieve information from the RAG (Retrieval-Augmented Generation) knowledge base. Use this function when you need specific information from documents, knowledge base, or when the user asks questions that require information retrieval from stored knowledge.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search query to find relevant information from the RAG knowledge base"
                            }
                        },
                        "required": ["query"]
                    }
                }
            ],
            "instructions": "You are a helpful voice assistant. When users ask questions that might require information from documents or a knowledge base, use the rag_knowledge function to retrieve relevant context before answering."
        }
        
        # Forward SDP to OpenAI with correct Content-Type and query parameters
        # OpenAI's /v1/realtime/calls endpoint expects application/sdp content type
        # and requires model and voice as query parameters
        base_url = "https://api.openai.com/v1/realtime/calls"
        query_params = {
            "model": model,
            "voice": voice
        }
        url = f"{base_url}?{urllib.parse.urlencode(query_params)}"
        
        headers = {
            "Authorization": f"Bearer {settings.openai_api_key}",
            "Content-Type": "application/sdp",
        }
        
        logger.info(f"Sending request to OpenAI: {base_url} with model={model}, voice={voice}")
        logger.debug(f"Request headers: {list(headers.keys())}")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    url,
                    headers=headers,
                    content=sdp_text.encode('utf-8')
                )
            except httpx.RequestError as e:
                logger.error(f"Request error to OpenAI API: {e}", exc_info=True)
                return Response(
                    content=json.dumps({"error": f"Failed to connect to OpenAI API: {str(e)}"}),
                    status_code=500,
                    media_type="application/json"
                )
            
            response.raise_for_status()
            
            # Return OpenAI's SDP answer to browser
            answer_sdp = response.text
            logger.info(f"Received SDP answer from OpenAI: {len(answer_sdp)} bytes")
            
            # Return SDP answer with session config in header for frontend to use
            return PlainTextResponse(
                content=answer_sdp,
                media_type="application/sdp",
                headers={
                    "X-Session-Config": json.dumps(session_config)
                }
            )
            
    except httpx.HTTPStatusError as e:
        # Enhanced error logging with full response details
        error_status = e.response.status_code
        error_text = e.response.text
        error_headers = dict(e.response.headers)
        
        logger.error(f"OpenAI API error: {error_status}")
        logger.error(f"Error response body: {error_text}")
        logger.error(f"Error response headers: {error_headers}")
        logger.error(f"Request URL: {e.request.url if hasattr(e, 'request') else 'N/A'}")
        
        # Try to parse error response for more details
        error_detail = f"OpenAI API error: {error_status}"
        try:
            if error_text:
                error_json = json.loads(error_text)
                if isinstance(error_json, dict) and "error" in error_json:
                    error_obj = error_json["error"]
                    if isinstance(error_obj, dict):
                        error_message = error_obj.get("message", "")
                        error_type = error_obj.get("type", "")
                        error_code = error_obj.get("code", "")
                        if error_message:
                            error_detail = f"OpenAI API error: {error_status} - {error_message}"
                        elif error_type:
                            error_detail = f"OpenAI API error: {error_status} - {error_type}"
                        if error_code:
                            error_detail += f" (code: {error_code})"
        except (json.JSONDecodeError, KeyError, AttributeError):
            pass
        
        return Response(
            content=json.dumps({"error": error_detail}),
            status_code=error_status,
            media_type="application/json"
        )
    except Exception as e:
        logger.error(f"Error creating realtime session: {e}", exc_info=True)
        return Response(
            content=json.dumps({"error": "Failed to create realtime session"}),
            status_code=500,
            media_type="application/json"
        )

