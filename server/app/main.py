from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi import Request, HTTPException
import os

from .routers.auth import auth as auth_routes
from .routers.auth.authig import settings

from .auth import router as oauth_router
from .routers import identification, plants
from .services.database import db

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
    secret_key=settings.session_secret_key,
    session_cookie="session",
    max_age=86400,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# === Routers ===
app.include_router(oauth_router)
app.include_router(auth_routes.router)
app.include_router(identification.router)
app.include_router(plants.router)

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
