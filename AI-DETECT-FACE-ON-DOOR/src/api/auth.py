# src/api/auth.py
import secrets
import time
from ..core.config import WEB_PASSWORD

_sessions: dict = {}


def login(password: str):
    """Validate password and return a session token, or None on failure."""
    if password == WEB_PASSWORD:
        token = secrets.token_hex(32)
        _sessions[token] = time.time() + 28800  # 8 hours TTL
        return token
    return None


def is_valid(token: str) -> bool:
    """Return True if the token exists and has not expired."""
    exp = _sessions.get(token)
    if exp and exp > time.time():
        return True
    _sessions.pop(token, None)
    return False


def logout(token: str):
    """Invalidate a session token."""
    _sessions.pop(token, None)
