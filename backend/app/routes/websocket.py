import json
import logging
from fastapi import WebSocket, WebSocketDisconnect
from app.services.session_manager import session_manager
from app.services.webrtc import webrtc_service
from app.services.openai_gateway import openai_gateway
from app.services.rag_client import rag_client

logger = logging.getLogger(__name__)


async def websocket_signaling(websocket: WebSocket):
    """WebSocket endpoint for WebRTC signaling"""
    await websocket.accept()
    logger.info("WebSocket connection accepted")
    
    session = None
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            message_type = data.get("type")
            session_id = data.get("session_id")
            
            logger.info(f"Received message type: {message_type}, session_id: {session_id}")
            
            if message_type == "session_request":
                # Create or get session
                if session_id:
                    session = session_manager.get_session(session_id)
                    if not session:
                        session = session_manager.create_session(session_id)
                else:
                    session = session_manager.create_session()
                
                session.websocket = websocket
                session.status = "connecting"
                
                # Create OpenAI session callback handlers
                async def on_transcription(text: str):
                    """Handle transcription from OpenAI"""
                    await websocket.send_json({
                        "type": "transcription",
                        "text": text,
                        "session_id": session.session_id
                    })
                    
                    # Retrieve context from RAG service
                    try:
                        context = await rag_client.retrieve_context(text)
                        if context:
                            # Inject context into OpenAI session
                            await openai_gateway.inject_context(session.session_id, context)
                            logger.info(f"Injected RAG context for query: {text[:50]}...")
                        
                        # Submit user message to OpenAI session
                        await openai_gateway.submit_user_message(session.session_id, text)
                    except Exception as e:
                        logger.error(f"Error retrieving RAG context: {e}", exc_info=True)
                        # Continue without context if RAG fails
                        await openai_gateway.submit_user_message(session.session_id, text)
                
                async def on_response_text(text: str):
                    """Handle response text from OpenAI"""
                    await websocket.send_json({
                        "type": "response_text",
                        "text": text,
                        "session_id": session.session_id
                    })
                
                async def on_audio_chunk(audio_data: bytes):
                    """Handle audio chunk from OpenAI"""
                    # Send audio to WebRTC peer
                    await webrtc_service.send_audio_to_peer(session, audio_data)
                
                # Create OpenAI session
                await openai_gateway.create_session(
                    session,
                    on_transcription=on_transcription,
                    on_response_text=on_response_text,
                    on_audio_chunk=on_audio_chunk
                )
                
                # Create peer connection with audio handler
                async def on_audio_received(audio_data: bytes):
                    """Handle audio received from client"""
                    await openai_gateway.send_audio(session.session_id, audio_data)
                
                pc = await webrtc_service.create_peer_connection(
                    session,
                    on_audio_received=on_audio_received
                )
                
                # Create offer
                offer = await webrtc_service.create_offer(pc)
                
                # Send offer to client
                await websocket.send_json({
                    "type": "offer",
                    "sdp": offer.sdp,
                    "type": offer.type,
                    "session_id": session.session_id
                })
                
                logger.info(f"Sent offer for session: {session.session_id}")
            
            elif message_type == "answer" and session:
                # Handle answer from client
                sdp = data.get("sdp")
                answer_type = data.get("type", "answer")
                
                if session.peer_connection:
                    await webrtc_service.set_remote_description(
                        session.peer_connection,
                        sdp,
                        answer_type
                    )
                    
                    session.status = "connected"
                    
                    # Send session ready message
                    await websocket.send_json({
                        "type": "session_ready",
                        "session_id": session.session_id
                    })
                    
                    logger.info(f"Session ready: {session.session_id}")
            
            elif message_type == "ice_candidate" and session:
                # Handle ICE candidate from client
                candidate = data.get("candidate")
                
                if session.peer_connection and candidate:
                    await webrtc_service.add_ice_candidate(
                        session.peer_connection,
                        candidate
                    )
                    logger.info(f"Added ICE candidate for session: {session.session_id}")
            
            elif message_type == "end_session" and session:
                # End session
                await webrtc_service.close_peer_connection(session)
                session_manager.remove_session(session.session_id)
                await websocket.send_json({
                    "type": "session_ended",
                    "session_id": session.session_id
                })
                break
    
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
        if session:
            await webrtc_service.close_peer_connection(session)
            await openai_gateway.close_session(session.session_id)
            session_manager.remove_session(session.session_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
        if session:
            await webrtc_service.close_peer_connection(session)
            await openai_gateway.close_session(session.session_id)
            session_manager.remove_session(session.session_id)
        await websocket.close()

