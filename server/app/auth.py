# server/app/auth.py
import os
from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth, OAuthError
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/api/auth")

# 1) Configure the OAuth client
oauth = OAuth()
oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
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
    # user_info contains keys like: sub, email, name, picture, ...
    # Now you can upsert this user into Mongo and issue your own JWT / session cookie

    # e.g.:
    # db.users.update_one({ "google_id": user_info["sub"] }, { "$set": {...} }, upsert=True)
    #
    # Then create your own signed token (JWT) to send back:
    from fastapi import Response
    import jwt, time

    payload = {
        "sub": user_info["sub"],
        "email": user_info["email"],
        "exp": time.time() + 3600
    }
    jwt_token = jwt.encode(payload, os.getenv("JWT_SECRET"), algorithm="HS256")

    response = RedirectResponse(url="http://localhost:8080/")  # send user home
    response.set_cookie("access_token", jwt_token, httponly=True, max_age=3600)
    return response
