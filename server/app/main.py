from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
import os

from .routes import router
from .auth import router as auth_router
from .mongodb_server import db  # <-- your Motor client

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup code ---
    # 1) Warm up the driver / open pool & auth
    await db.client.admin.command("ping")
    # 2) Create index on user_id for fast lookups
    await db.plants.create_index("user_id", name="idx_user_id")
    yield
    # --- (optional) Shutdown code could go here ---

app = FastAPI(lifespan=lifespan)

# === Middlewares ===
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET_KEY", "a-strong-fallback-secret"),
    session_cookie="session",
    max_age=86400,
)

origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:8080")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Routers ===
app.include_router(auth_router)
app.include_router(router)