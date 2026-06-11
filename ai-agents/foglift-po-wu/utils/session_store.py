import secrets
from typing import Dict, Optional, Any
from datetime import datetime, timedelta

class SessionStore:
    def __init__(self, ttl_minutes: int = 30):
        self._store: Dict[str, Dict[str, Any]] = {}
        self._ttl = timedelta(minutes=ttl_minutes)

    def create(self, data: Dict[str, Any]) -> str:
        session_id = secrets.token_urlsafe(16)
        self._store[session_id] = {
            "data": data,
            "created_at": datetime.now()
        }
        return session_id

    def get(self, session_id: str) -> Optional[Dict[str, Any]]:
        if session_id not in self._store:
            return None
        entry = self._store[session_id]
        if datetime.now() - entry["created_at"] > self._ttl:
            del self._store[session_id]
            return None
        return entry["data"]

    def update(self, session_id: str, data: Dict[str, Any]) -> bool:
        if session_id in self._store:
            self._store[session_id]["data"].update(data)
            return True
        return False

    def delete(self, session_id: str) -> bool:
        if session_id in self._store:
            del self._store[session_id]
            return True
        return False

session_store = SessionStore()
