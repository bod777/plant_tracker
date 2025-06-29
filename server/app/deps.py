# server/app/deps.py
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt, os

oauth2_scheme = HTTPBearer(auto_error=False)

async def get_current_user(request: Request):
    """Return JWT payload from header or cookie."""
    credentials: HTTPAuthorizationCredentials | None = await oauth2_scheme(request)
    token = None
    if credentials:
        token = credentials.credentials
    else:
        token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(401, "Invalid auth token")
    try:
        payload = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=["HS256"])
    except jwt.PyJWTError:
        raise HTTPException(401, "Invalid auth token")
    return payload  # e.g. { sub, email, exp }
