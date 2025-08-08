from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth, OAuthError

from ...config import Config
from .deps import get_current_user
from ...services.database import upsert_user

router = APIRouter(prefix="/api/auth")

# 1) Configure the OAuth client
oauth = OAuth()
oauth.register(
    name='google',
    client_id=Config.GOOGLE_CLIENT_ID,
    client_secret=Config.GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

# 2) “Login” endpoint: redirect user to Google
@router.get("/google/login")
async def login(request: Request):
    redirect_uri = request.url_for("auth_callback")  # points to /api/auth/google/callback
    return await oauth.google.authorize_redirect(request, redirect_uri)

# 3) Callback: Google redirects back here!
@router.get("/google/callback", name="auth_callback")
async def auth_callback(request: Request):
    try:
        token = await oauth.google.authorize_access_token(request)
    except OAuthError:
        return RedirectResponse(url="/?error=oauth_failure")

    # 4) Fetch the user’s profile
    # user_info = await oauth.google.parse_id_token(request, token)
    resp = await oauth.google.get('https://openidconnect.googleapis.com/v1/userinfo', token=token)
    user_info = resp.json()
    stored_user = await upsert_user(user_info)

    from fastapi import Response
    import jwt, time

    payload = {
        "userId": user_info["sub"],
        "email": stored_user.get("email"),
        "exp": time.time() + 3600,
    }
    jwt_token = jwt.encode(payload, Config.JWT_SECRET, algorithm="HS256")

    frontend_url = Config.FRONTEND_URL
    response = RedirectResponse(url=frontend_url)  # send user home
    response.set_cookie("access_token", jwt_token, httponly=True, max_age=3600)
    return response

@router.get("/me")
async def me(user=Depends(get_current_user)):
    """Return information about the current authenticated user."""
    return {"email": user["email"], "userId": user["userId"]}


@router.post("/logout")
async def logout():
    """Clear the auth cookie so the user is fully logged out."""
    response = JSONResponse({"detail": "Logged out"})
    response.delete_cookie("access_token")
    return response
