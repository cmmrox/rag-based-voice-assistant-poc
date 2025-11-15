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
    WebSocket endpoint for handling function call execution and RAG integration.
    
    With function calling enabled, OpenAI Realtime API calls the rag_knowledge
    function when needed. Frontend sends function call requests to this endpoint,
    backend executes them via RAG service, and sends results back to frontend.
    
    Also supports backward compatibility with old transcription-based approach.
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
                    # Handle transcription event (kept for backward compatibility, but function calling is preferred)
                    transcript = message.get("transcript", "")
                    logger.info(f"Received transcription for session {session_id}: {transcript}")
                    
                    # Note: With function calling, RAG queries are handled via function calls
                    # This transcription handler is kept for fallback/backward compatibility
                    # In the new flow, OpenAI will call rag_knowledge function when needed
                
                elif message_type == "function_call":
                    # Handle function call execution request
                    call_id = message.get("call_id")
                    function_name = message.get("function_name")
                    arguments = message.get("arguments", {})
                    
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
                                
                                # Send function call result back to frontend
                                await connection_manager.send_message(session_id, {
                                    "type": "function_call_result",
                                    "call_id": call_id,
                                    "function_name": function_name,
                                    "result": {
                                        "context": context,
                                        "sources": sources,
                                        "success": True
                                    }
                                })
                            else:
                                # No context found
                                logger.info(f"No RAG context found for query: {query}")
                                await connection_manager.send_message(session_id, {
                                    "type": "function_call_result",
                                    "call_id": call_id,
                                    "function_name": function_name,
                                    "result": {
                                        "context": "",
                                        "sources": [],
                                        "success": True,
                                        "message": "No relevant information found in knowledge base"
                                    }
                                })
                        
                        except Exception as e:
                            logger.error(f"Error executing function call: {e}", exc_info=True)
                            await connection_manager.send_message(session_id, {
                                "type": "function_call_result",
                                "call_id": call_id,
                                "function_name": function_name,
                                "result": {
                                    "success": False,
                                    "error": str(e)
                                }
                            })
                    else:
                        logger.warning(f"Unknown function name: {function_name}")
                        await connection_manager.send_message(session_id, {
                            "type": "function_call_result",
                            "call_id": call_id,
                            "function_name": function_name,
                            "result": {
                                "success": False,
                                "error": f"Unknown function: {function_name}"
                            }
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

