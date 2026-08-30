"""Authentication and authorization.

This is the fix for the old build's central flaw: the JWT is now actually
verified on every protected route, and the caller's role is taken from the
*verified token*, never from the request body. ``get_current_user`` is a FastAPI
dependency; ``require_roles`` builds role-gated dependencies.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Iterable

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from .config import get_settings

_pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
_bearer = HTTPBearer(auto_error=True)


def hash_password(password: str) -> str:
    return _pwd.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return _pwd.verify(plain, hashed)


def create_access_token(*, user_id: int, username: str, role: str) -> str:
    settings = get_settings()
    now = datetime.now(timezone.utc)
    payload = {
        "sub": username,
        "uid": user_id,
        "role": role,
        "iat": now,
        "exp": now + timedelta(hours=settings.access_token_expire_hours),
    }
    return jwt.encode(payload, settings.resolved_jwt_secret(), algorithm=settings.jwt_algorithm)


def _decode(token: str) -> dict:
    settings = get_settings()
    try:
        return jwt.decode(token, settings.resolved_jwt_secret(), algorithms=[settings.jwt_algorithm])
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")


class CurrentUser:
    __slots__ = ("id", "username", "role")

    def __init__(self, payload: dict) -> None:
        self.id = payload.get("uid")
        self.username = payload.get("sub")
        self.role = payload.get("role")


def get_current_user(creds: HTTPAuthorizationCredentials = Depends(_bearer)) -> CurrentUser:
    """Verify the bearer token and return the authenticated user."""
    payload = _decode(creds.credentials)
    if not payload.get("sub") or not payload.get("role"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Malformed token")
    return CurrentUser(payload)


def require_roles(*roles: str):
    """Dependency factory that restricts a route to the given roles."""
    allowed = {r.lower() for r in roles}

    def _dep(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if user.role.lower() not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{user.role}' is not permitted for this action.",
            )
        return user

    return _dep
