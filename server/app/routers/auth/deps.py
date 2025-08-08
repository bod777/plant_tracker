# server/app/deps.py
from ...config import Config
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

from ...services.database import get_user_by_userId

oauth2_scheme = HTTPBearer(auto_error=False)

async def get_current_user(request: Request):
    """Retrieve the current user document from the database."""
    credentials: HTTPAuthorizationCredentials | None = await oauth2_scheme(request)
    token = credentials.credentials if credentials else request.cookies.get("access_token")
    if not token:
        raise HTTPException(401, "Invalid auth token")
    try:
        payload = jwt.decode(token, Config.JWT_SECRET, algorithms=["HS256"])
    except jwt.PyJWTError:
        raise HTTPException(401, "Invalid auth token")
    user = await get_user_by_userId(payload.get("userId"))
    if not user:
        raise HTTPException(401, "User not found")
    return user
