import json
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.rag_client import rag_client

logger = logging.getLogger(__name__)

router = APIRouter()


class ConnectionManager:
    """Manages WebSocket connections for event handling"""
    
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket
        logger.info(f"WebSocket connected for session: {session_id}")
    
    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]
            logger.info(f"WebSocket disconnected for session: {session_id}")
    
    async def send_message(self, session_id: str, message: dict):
        if session_id in self.active_connections:
            websocket = self.active_connections[session_id]
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Error sending message to {session_id}: {e}")
                self.disconnect(session_id)


# Global connection manager
connection_manager = ConnectionManager()


@router.websocket("/ws/events/{session_id}")
async def websocket_events(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for handling transcription events and RAG integration.
    
    Frontend sends transcription events, backend queries RAG service,
    and sends context back to frontend for injection into OpenAI.
    """
    await connection_manager.connect(websocket, session_id)
    
    try:
        while True:
            # Receive message from frontend
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                message_type = message.get("type")
                
                if message_type == "transcription":
                    # Handle transcription event
                    transcript = message.get("transcript", "")
                    logger.info(f"Received transcription for session {session_id}: {transcript}")
                    
                    if transcript:
                        # Query RAG service for relevant context
                        try:
                            rag_result = await rag_client.query(transcript)
                            
                            if rag_result and rag_result.get("context"):
                                context = rag_result.get("context", "")
                                sources = rag_result.get("sources", [])
                                
                                logger.info(f"Retrieved RAG context: {len(context)} chars from {len(sources)} sources")
                                
                                # Send context back to frontend
                                await connection_manager.send_message(session_id, {
                                    "type": "rag_context",
                                    "context": context,
                                    "sources": sources,
                                    "query": transcript
                                })
                            else:
                                # No context found, send empty context
                                logger.info(f"No RAG context found for query: {transcript}")
                                await connection_manager.send_message(session_id, {
                                    "type": "rag_context",
                                    "context": "",
                                    "sources": [],
                                    "query": transcript
                                })
                        
                        except Exception as e:
                            logger.error(f"Error querying RAG service: {e}", exc_info=True)
                            # Send error response but don't break the connection
                            await connection_manager.send_message(session_id, {
                                "type": "rag_error",
                                "error": "Failed to retrieve context from RAG service",
                                "query": transcript
                            })
                
                elif message_type == "ping":
                    # Heartbeat/ping message
                    await connection_manager.send_message(session_id, {
                        "type": "pong"
                    })
                
                else:
                    logger.warning(f"Unknown message type: {message_type}")
            
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON received: {e}")
                await connection_manager.send_message(session_id, {
                    "type": "error",
                    "error": "Invalid JSON format"
                })
            
            except Exception as e:
                logger.error(f"Error processing message: {e}", exc_info=True)
                await connection_manager.send_message(session_id, {
                    "type": "error",
                    "error": str(e)
                })
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session: {session_id}")
        connection_manager.disconnect(session_id)
    
    except Exception as e:
        logger.error(f"WebSocket error for session {session_id}: {e}", exc_info=True)
        connection_manager.disconnect(session_id)

