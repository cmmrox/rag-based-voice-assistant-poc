import json
import logging
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
        
        # Session configuration
        session_config = {
            "type": "realtime",
            "model": "gpt-realtime",
            "audio": {
                "output": {
                    "voice": "marin"
                }
            }
        }
        
        # Forward to OpenAI using multipart form data
        async with httpx.AsyncClient(timeout=30.0) as client:
            form_data = {
                "sdp": sdp_text,
                "session": json.dumps(session_config)
            }
            
            response = await client.post(
                "https://api.openai.com/v1/realtime/calls",
                headers={
                    "Authorization": f"Bearer {settings.openai_api_key}",
                },
                data=form_data
            )
            
            response.raise_for_status()
            
            # Return OpenAI's SDP answer to browser
            answer_sdp = response.text
            logger.info(f"Received SDP answer from OpenAI: {len(answer_sdp)} bytes")
            
            return PlainTextResponse(
                content=answer_sdp,
                media_type="application/sdp"
            )
            
    except httpx.HTTPStatusError as e:
        logger.error(f"OpenAI API error: {e.response.status_code} - {e.response.text}")
        return Response(
            content=json.dumps({"error": f"OpenAI API error: {e.response.status_code}"}),
            status_code=e.response.status_code,
            media_type="application/json"
        )
    except Exception as e:
        logger.error(f"Error creating realtime session: {e}", exc_info=True)
        return Response(
            content=json.dumps({"error": "Failed to create realtime session"}),
            status_code=500,
            media_type="application/json"
        )

