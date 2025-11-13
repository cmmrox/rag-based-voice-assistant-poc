from typing import Optional
from datetime import datetime
import uuid


class Session:
    """Session model for tracking voice sessions"""
    
    def __init__(self, session_id: Optional[str] = None):
        self.session_id = session_id or str(uuid.uuid4())
        self.created_at = datetime.now()
        self.peer_connection = None
        self.websocket = None
        self.status = "idle"  # idle, connecting, connected, error
        self.transcript = []
        
    def add_transcript_entry(self, role: str, text: str):
        """Add a transcript entry"""
        self.transcript.append({
            "role": role,
            "text": text,
            "timestamp": datetime.now().isoformat()
        })
    
    def to_dict(self):
        """Convert session to dictionary"""
        return {
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat(),
            "status": self.status,
            "transcript_count": len(self.transcript)
        }

