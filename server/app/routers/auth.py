from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from ..deps import get_current_user

router = APIRouter(prefix="/api/auth")


@router.get("/me")
async def me(user=Depends(get_current_user)):
    """Return information about the current authenticated user."""
    return {"email": user["email"], "sub": user["sub"]}


@router.post("/logout")
async def logout():
    """Clear the auth cookie so the user is fully logged out."""
    response = JSONResponse({"detail": "Logged out"})
    response.delete_cookie("access_token")
    return response
