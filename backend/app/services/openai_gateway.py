import asyncio
import logging
import base64
from typing import Optional, Callable
from openai import OpenAI
from app.config import settings
from app.models.session import Session

logger = logging.getLogger(__name__)


class OpenAIGateway:
    """OpenAI Realtime API Gateway"""
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.sessions: dict[str, any] = {}  # Store OpenAI session objects
    
    async def create_session(
        self, 
        session: Session,
        on_transcription: Optional[Callable[[str], None]] = None,
        on_response_text: Optional[Callable[[str], None]] = None,
        on_audio_chunk: Optional[Callable[[bytes], None]] = None
    ):
        """Create OpenAI Realtime API session"""
        try:
            # Create OpenAI Realtime API session
            openai_session = self.client.beta.realtime.connect(
                model="gpt-4o-realtime-preview-2024-10-01",
                voice="alloy",
                instructions="You are a helpful voice assistant. Be concise and natural in your responses."
            )
            
            self.sessions[session.session_id] = {
                "openai_session": openai_session,
                "session": session,
                "on_transcription": on_transcription,
                "on_response_text": on_response_text,
                "on_audio_chunk": on_audio_chunk
            }
            
            # Start event handler
            asyncio.create_task(self._handle_events(session.session_id))
            
            logger.info(f"Created OpenAI session for: {session.session_id}")
            return openai_session
            
        except Exception as e:
            logger.error(f"Error creating OpenAI session: {e}", exc_info=True)
            raise
    
    async def _handle_events(self, session_id: str):
        """Handle events from OpenAI Realtime API"""
        try:
            session_data = self.sessions.get(session_id)
            if not session_data:
                return
            
            openai_session = session_data["openai_session"]
            on_transcription = session_data["on_transcription"]
            on_response_text = session_data["on_response_text"]
            on_audio_chunk = session_data["on_audio_chunk"]
            
            async for event in openai_session:
                event_type = getattr(event, 'type', None)
                
                if event_type == "input_audio_buffer.speech_started":
                    logger.info("Speech started")
                    if session_data["session"]:
                        session_data["session"].status = "listening"
                
                elif event_type == "input_audio_buffer.transcription.completed":
                    transcript = getattr(event, 'transcript', '')
                    logger.info(f"Transcription completed: {transcript}")
                    
                    if on_transcription:
                        on_transcription(transcript)
                    
                    if session_data["session"]:
                        session_data["session"].add_transcript_entry("user", transcript)
                        session_data["session"].status = "processing"
                
                elif event_type == "response.audio_transcript.delta":
                    delta = getattr(event, 'delta', '')
                    if delta and on_response_text:
                        on_response_text(delta)
                
                elif event_type == "response.audio.delta":
                    # Audio chunk from OpenAI
                    audio_data = getattr(event, 'delta', b'')
                    if audio_data and on_audio_chunk:
                        # Decode base64 audio if needed
                        try:
                            audio_bytes = base64.b64decode(audio_data) if isinstance(audio_data, str) else audio_data
                            on_audio_chunk(audio_bytes)
                        except Exception as e:
                            logger.error(f"Error processing audio chunk: {e}")
                
                elif event_type == "response.done":
                    logger.info("Response done")
                    if session_data["session"]:
                        session_data["session"].status = "connected"
                
                elif event_type == "error":
                    error = getattr(event, 'error', {})
                    logger.error(f"OpenAI API error: {error}")
                    if session_data["session"]:
                        session_data["session"].status = "error"
        
        except Exception as e:
            logger.error(f"Error handling OpenAI events: {e}", exc_info=True)
            if session_id in self.sessions:
                session_data = self.sessions[session_id]
                if session_data["session"]:
                    session_data["session"].status = "error"
    
    async def send_audio(self, session_id: str, audio_data: bytes):
        """Send audio data to OpenAI Realtime API"""
        try:
            session_data = self.sessions.get(session_id)
            if not session_data:
                logger.warning(f"Session not found: {session_id}")
                return
            
            openai_session = session_data["openai_session"]
            
            # Convert audio to base64 if needed
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            
            # Send audio to OpenAI
            openai_session.submit(
                type="input_audio_buffer.append",
                audio=audio_base64
            )
            
        except Exception as e:
            logger.error(f"Error sending audio to OpenAI: {e}", exc_info=True)
    
    async def inject_context(self, session_id: str, context: str):
        """Inject RAG context into OpenAI session"""
        try:
            session_data = self.sessions.get(session_id)
            if not session_data:
                logger.warning(f"Session not found: {session_id}")
                return
            
            openai_session = session_data["openai_session"]
            
            # Update instructions with context
            updated_instructions = f"""You are a helpful voice assistant. Use the following context to answer questions.

Context:
{context}

If the context doesn't contain relevant information, say so. Be concise and natural in your responses."""
            
            openai_session.update(instructions=updated_instructions)
            
            logger.info(f"Injected context into session: {session_id}")
            
        except Exception as e:
            logger.error(f"Error injecting context: {e}", exc_info=True)
    
    async def submit_user_message(self, session_id: str, message: str):
        """Submit user message to OpenAI session"""
        try:
            session_data = self.sessions.get(session_id)
            if not session_data:
                logger.warning(f"Session not found: {session_id}")
                return
            
            openai_session = session_data["openai_session"]
            
            openai_session.submit(
                type="conversation.item.create",
                item={
                    "type": "message",
                    "role": "user",
                    "content": message
                }
            )
            
            logger.info(f"Submitted user message to session: {session_id}")
            
        except Exception as e:
            logger.error(f"Error submitting user message: {e}", exc_info=True)
    
    async def close_session(self, session_id: str):
        """Close OpenAI session"""
        try:
            if session_id in self.sessions:
                session_data = self.sessions[session_id]
                openai_session = session_data["openai_session"]
                
                # Close OpenAI session
                openai_session.close()
                
                del self.sessions[session_id]
                logger.info(f"Closed OpenAI session: {session_id}")
        
        except Exception as e:
            logger.error(f"Error closing OpenAI session: {e}", exc_info=True)
    
    async def check_health(self) -> dict:
        """Check OpenAI API connectivity and configuration"""
        api_key_configured = bool(settings.openai_api_key and settings.openai_api_key.strip())
        
        if not api_key_configured:
            logger.warning("OpenAI API key not configured")
            return {
                "status": "error",
                "api_key_configured": False,
                "details": {"error": "API key not configured"}
            }
        
        try:
            # Make a lightweight API call to verify connectivity
            # Using models.list() as it's a simple, fast endpoint
            loop = asyncio.get_event_loop()
            
            # Run the synchronous OpenAI call in a thread pool to avoid blocking
            # Just iterate once to verify API is accessible without fetching all models
            def check_openai():
                models_iter = self.client.models.list()
                # Just try to get the first model to verify connectivity
                try:
                    first_model = next(iter(models_iter))
                    return first_model is not None
                except StopIteration:
                    # Empty iterator but API is accessible
                    return True
            
            models_available = await loop.run_in_executor(None, check_openai)
            
            logger.info("OpenAI API health check successful")
            return {
                "status": "connected",
                "api_key_configured": True,
                "details": {"message": "API accessible", "models_available": models_available}
            }
        
        except Exception as e:
            error_msg = str(e)
            error_type = type(e).__name__
            
            # Check for authentication errors
            if "authentication" in error_msg.lower() or "401" in error_msg or "unauthorized" in error_msg.lower():
                logger.warning(f"OpenAI API authentication error: {error_msg}")
                return {
                    "status": "error",
                    "api_key_configured": True,
                    "details": {"error": "Authentication failed - invalid API key"}
                }
            
            # Check for network errors
            if "connection" in error_msg.lower() or "timeout" in error_msg.lower() or "network" in error_msg.lower():
                logger.warning(f"OpenAI API connection error: {error_msg}")
                return {
                    "status": "unavailable",
                    "api_key_configured": True,
                    "details": {"error": f"Connection error: {error_type}"}
                }
            
            # Other errors
            logger.error(f"OpenAI API health check error: {error_msg}", exc_info=True)
            return {
                "status": "error",
                "api_key_configured": True,
                "details": {"error": f"{error_type}: {error_msg[:100]}"}
            }


# Global OpenAI gateway instance
openai_gateway = OpenAIGateway()

