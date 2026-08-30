"""Registration and login."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..schemas import LoginRequest, RegisterRequest, TokenResponse
from ..security import create_access_token, hash_password, verify_password
from ..storage import store

router = APIRouter(prefix="/api", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=201)
def register(body: RegisterRequest):
    if store.get_user_by_username(body.username):
        raise HTTPException(status_code=409, detail="Username already exists")

    user_id = store.create_user(
        username=body.username,
        password_hash=hash_password(body.password),
        role=body.role.value,
        full_name=body.full_name,
    )
    store.log_audit(
        action="REGISTER", actor=body.username, actor_role=body.role.value,
        target=body.username, details=f"New account with role '{body.role.value}'",
    )
    token = create_access_token(user_id=user_id, username=body.username, role=body.role.value)
    return TokenResponse(access_token=token, role=body.role.value, username=body.username)


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest):
    user = store.get_user_by_username(body.username)
    if not user or not verify_password(body.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(user_id=user["id"], username=user["username"], role=user["role"])
    return TokenResponse(access_token=token, role=user["role"], username=user["username"])
