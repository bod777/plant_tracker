from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi import Request, HTTPException
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
origins_array = [o.strip() for o in origins.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins_array,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Routers ===
app.include_router(auth_router)
app.include_router(router)

# === Static Files ===
frontend_dir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../plant-tracker-client/dist")
)
if os.path.isdir(frontend_dir):
    class SPAStaticFiles(StaticFiles):
        async def get_response(self, path, scope):
            response = await super().get_response(path, scope)
            if response.status_code == 404:
                # Return index.html for any non-file path so that client-side
                # routing works when the page is refreshed or directly visited.
                return FileResponse(os.path.join(self.directory, "index.html"))
            return response

    app.mount("/", SPAStaticFiles(directory=frontend_dir, html=True), name="frontend")

    @app.exception_handler(404)
    async def spa_fallback(request: Request, exc: HTTPException):
        """Serve index.html for unknown non-API routes."""
        if not request.url.path.startswith("/api"):
            return FileResponse(os.path.join(frontend_dir, "index.html"))
        return JSONResponse({"detail": "Not Found"}, status_code=404)
