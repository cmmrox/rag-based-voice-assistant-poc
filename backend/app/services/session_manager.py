from typing import Dict, Optional
from app.models.session import Session


class SessionManager:
    """In-memory session manager"""
    
    def __init__(self):
        self.sessions: Dict[str, Session] = {}
    
    def create_session(self, session_id: Optional[str] = None) -> Session:
        """Create a new session"""
        session = Session(session_id)
        self.sessions[session.session_id] = session
        return session
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """Get a session by ID"""
        return self.sessions.get(session_id)
    
    def remove_session(self, session_id: str):
        """Remove a session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
    
    def get_all_sessions(self) -> Dict[str, Session]:
        """Get all active sessions"""
        return self.sessions.copy()


# Global session manager instance
session_manager = SessionManager()

