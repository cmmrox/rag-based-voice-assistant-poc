import json
import logging
import asyncio
from typing import Optional, Callable
from aiortc import RTCPeerConnection, RTCSessionDescription, RTCIceCandidate, MediaStreamTrack
from aiortc.contrib.media import MediaPlayer, MediaRelay
from app.models.session import Session

logger = logging.getLogger(__name__)


class WebRTCService:
    """WebRTC peer connection service"""
    
    def __init__(self):
        self.relay = MediaRelay()
    
    async def create_peer_connection(
        self, 
        session: Session,
        on_audio_received: Optional[Callable[[bytes], None]] = None
    ) -> RTCPeerConnection:
        """Create a new RTCPeerConnection for a session"""
        pc = RTCPeerConnection()
        session.peer_connection = pc
        
        # Handle incoming tracks
        @pc.on("track")
        async def on_track(track):
            logger.info(f"Received track: {track.kind}")
            if track.kind == "audio":
                # Handle audio track
                asyncio.create_task(self._handle_audio_track(track, on_audio_received))
        
        # Handle ICE candidates
        @pc.on("icecandidate")
        async def on_ice_candidate(candidate):
            if candidate:
                await self._send_ice_candidate(session, candidate)
        
        # Handle connection state changes
        @pc.on("connectionstatechange")
        async def on_connection_state_change():
            logger.info(f"Connection state changed: {pc.connectionState}")
            session.status = pc.connectionState
        
        return pc
    
    async def _handle_audio_track(
        self, 
        track: MediaStreamTrack,
        on_audio_received: Optional[Callable[[bytes], None]]
    ):
        """Handle incoming audio track"""
        try:
            while True:
                frame = await track.recv()
                if frame:
                    # Convert audio frame to bytes
                    # Note: This is a simplified version - actual implementation
                    # would need proper audio format conversion
                    if on_audio_received:
                        # For now, we'll need to implement proper audio conversion
                        # This is a placeholder
                        pass
        except Exception as e:
            logger.error(f"Error handling audio track: {e}", exc_info=True)
    
    async def create_offer(self, pc: RTCPeerConnection) -> RTCSessionDescription:
        """Create a WebRTC offer"""
        offer = await pc.createOffer()
        await pc.setLocalDescription(offer)
        return offer
    
    async def set_remote_description(
        self, 
        pc: RTCPeerConnection, 
        sdp: str, 
        type: str
    ):
        """Set remote description"""
        desc = RTCSessionDescription(sdp=sdp, type=type)
        await pc.setRemoteDescription(desc)
    
    async def create_answer(self, pc: RTCPeerConnection) -> RTCSessionDescription:
        """Create a WebRTC answer"""
        answer = await pc.createAnswer()
        await pc.setLocalDescription(answer)
        return answer
    
    async def add_ice_candidate(
        self, 
        pc: RTCPeerConnection, 
        candidate_dict: dict
    ):
        """Add ICE candidate"""
        candidate = RTCIceCandidate(
            candidate=candidate_dict.get("candidate"),
            sdpMid=candidate_dict.get("sdpMid"),
            sdpMLineIndex=candidate_dict.get("sdpMLineIndex")
        )
        await pc.addIceCandidate(candidate)
    
    async def _send_ice_candidate(self, session: Session, candidate: RTCIceCandidate):
        """Send ICE candidate to client via WebSocket"""
        if session.websocket:
            message = {
                "type": "ice_candidate",
                "candidate": {
                    "candidate": candidate.candidate,
                    "sdpMid": candidate.sdpMid,
                    "sdpMLineIndex": candidate.sdpMLineIndex
                },
                "session_id": session.session_id
            }
            try:
                await session.websocket.send_json(message)
            except Exception as e:
                logger.error(f"Error sending ICE candidate: {e}")
    
    async def send_audio_to_peer(self, session: Session, audio_data: bytes):
        """Send audio data to peer connection"""
        # This would need to be implemented with proper audio track creation
        # For now, this is a placeholder
        logger.debug(f"Sending audio to peer: {len(audio_data)} bytes")
        pass
    
    async def close_peer_connection(self, session: Session):
        """Close peer connection and cleanup"""
        if session.peer_connection:
            await session.peer_connection.close()
            session.peer_connection = None
        session.status = "idle"


# Global WebRTC service instance
webrtc_service = WebRTCService()

