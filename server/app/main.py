from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
import os
from .routes import router
from .auth import router as auth_router

app = FastAPI()

# Add this *before* you include your auth router:
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET_KEY", "a-strong-fallback-secret"),
    session_cookie="session",       # optional, defaults to "session"
    max_age=86400,                  # optional, seconds until cookie expires
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Then include your routers:
app.include_router(auth_router)
app.include_router(router)
