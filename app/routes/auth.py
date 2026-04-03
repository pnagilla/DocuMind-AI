import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError

from app.db import get_db
from app.models.user import LoginRequest, RegisterRequest, TokenResponse
from app.services.auth_service import create_access_token, decode_token, hash_password, verify_password

router = APIRouter()
security = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = decode_token(credentials.credentials)
        return {"user_id": payload["sub"], "username": payload["username"]}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token. Please log in again.",
        )


@router.post("/register", response_model=TokenResponse)
async def register(request: RegisterRequest):
    if len(request.username) < 3:
        raise HTTPException(status_code=400, detail="Username must be at least 3 characters.")
    if len(request.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters.")

    db = get_db()
    existing = db.execute(
        "SELECT id FROM users WHERE username = ? OR email = ?",
        (request.username, request.email),
    ).fetchone()

    if existing:
        db.close()
        raise HTTPException(status_code=400, detail="Username or email already exists.")

    user_id = str(uuid.uuid4())
    db.execute(
        "INSERT INTO users (id, username, email, hashed_password, created_at) VALUES (?, ?, ?, ?, ?)",
        (user_id, request.username, request.email, hash_password(request.password),
         datetime.now(timezone.utc).isoformat()),
    )
    db.commit()
    db.close()

    token = create_access_token(user_id, request.username)
    return TokenResponse(access_token=token, username=request.username)


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE username = ?", (request.username,)).fetchone()
    db.close()

    if not user or not verify_password(request.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid username or password.")

    token = create_access_token(user["id"], user["username"])
    return TokenResponse(access_token=token, username=user["username"])
