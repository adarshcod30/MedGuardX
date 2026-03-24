"""Authentication routes."""
from fastapi import APIRouter, HTTPException
from ..models import UserCreate, UserLogin, TokenResponse
from ..auth import hash_password, verify_password, create_token
from ..database import get_db

router = APIRouter(prefix="/api", tags=["auth"])


@router.post("/register", response_model=TokenResponse)
def register(user: UserCreate):
    db = get_db()
    existing = db.execute("SELECT id FROM users WHERE username = ?", (user.username,)).fetchone()
    if existing:
        db.close()
        raise HTTPException(400, "Username already exists")

    pw_hash = hash_password(user.password)
    db.execute(
        "INSERT INTO users (username, password_hash, role, full_name) VALUES (?,?,?,?)",
        (user.username, pw_hash, user.role.value, user.full_name)
    )
    db.commit()
    db.close()

    token = create_token({"sub": user.username, "role": user.role.value})
    return TokenResponse(access_token=token, role=user.role.value, username=user.username)


@router.post("/login", response_model=TokenResponse)
def login(user: UserLogin):
    db = get_db()
    row = db.execute("SELECT * FROM users WHERE username = ?", (user.username,)).fetchone()
    db.close()

    if not row or not verify_password(user.password, row["password_hash"]):
        raise HTTPException(401, "Invalid credentials")

    token = create_token({"sub": row["username"], "role": row["role"]})
    return TokenResponse(access_token=token, role=row["role"], username=row["username"])
