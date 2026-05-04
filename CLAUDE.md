# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Backend (run from `server/`)
```powershell
.venv\Scripts\Activate.ps1          # activate venv (Windows)
uvicorn app.main:app --reload --port 8000
```

### Frontend (run from `plant-tracker-client/`)
```powershell
npm install   # first time only
npm run dev   # runs on http://localhost:8080
npm run build # production build (output goes to dist/, served by FastAPI)
```

### Run both at once (from repo root)
```
start.cmd
```

## Architecture

### Request Flow
1. Browser hits the React frontend at `:8080` (dev) or is served as static files from FastAPI in production.
2. API calls go to the FastAPI backend at `:8000/api/...`.
3. Auth uses Google OAuth — login hits `/api/auth/google/login`, Google redirects to `/api/auth/google/callback`, which sets an `httponly` JWT cookie and redirects to `FRONTEND_URL`.
4. All protected routes read the JWT from either the cookie or a Bearer header (`deps.py:get_current_user`).

### Backend (`server/`)
- `app/main.py` — FastAPI app, CORS/session middleware, mounts the compiled React `dist/` as static files for production.
- `app/routes.py` — all `/api/*` plant endpoints: identify, list, count, delete, update notes.
- `app/auth.py` — Google OAuth flow, issues JWT cookie on success. `FRONTEND_URL` env var controls where the browser is sent after login; `secure=True` on the cookie is set automatically based on whether `FRONTEND_URL` starts with `https://`.
- `app/storage.py` — Cloudflare R2 via boto3. `upload_image_bytes()` is the primary function (takes raw bytes). `upload_base64_image()` delegates to it and is kept for the migration script.
- `app/deps.py` — `get_current_user` dependency; reads JWT from cookie or Bearer header.
- `app/models.py` — Pydantic models for API responses.
- `app/mongodb_server.py` — Motor async client; `db` is imported everywhere that hits Mongo.

### Frontend (`plant-tracker-client/src/`)
- `api/api.ts` — all HTTP calls. `identifyPlant()` sends images as `multipart/form-data` (raw binary, not base64). `API_BASE` falls back to `//localhost:8000` if `VITE_API_BASE` is unset.
- `api/models.ts` — TypeScript interfaces (`IdentifiedPlant` is the app-internal type; `ApiPlantResponse` is the raw server shape).
- `pages/Index.tsx` — root component, owns all state: auth, history list, pagination, current result. Renders child views via React Router.
- Components are stateless and receive data/callbacks from `Index.tsx`.

### Image Handling
- Images are captured from the camera or file picker as data URLs (canvas `toDataURL`), capped at 2048px / 0.85 JPEG quality.
- Before sending, `dataURLToBlob()` in `api.ts` converts data URLs to binary blobs, which are appended to `FormData`.
- FastAPI receives `List[UploadFile]`, reads raw bytes, passes them to the Plant.id client, then uploads to R2 via `upload_image_bytes()`.
- R2 public URLs are stored in MongoDB; `image_data` (base64) is excluded from list queries but may exist on old records.

### Pagination
- History uses accumulating load-more pagination. `Index.tsx` appends each page to `identificationHistory`. `HistorySection` shows a "Load More" button when `history.length < totalCount`.

## Environment Variables

### `server/.env`
| Variable | Purpose |
|---|---|
| `MONGODB_URI` | MongoDB Atlas connection string |
| `MONGODB_DB_NAME` | Database name (default: `plant_tracker`) |
| `PLANT_ID_API_KEY` | plant.id API key |
| `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` | Google OAuth app credentials |
| `JWT_SECRET` | Signs JWT tokens (any long random string) |
| `SESSION_SECRET_KEY` | Signs Starlette sessions (any long random string) |
| `FRONTEND_URL` | Where auth redirects after login — **must be `http://localhost:8080/` locally** |
| `ALLOWED_ORIGINS` | Comma-separated CORS origins — **must include `http://localhost:8080` locally** |
| `R2_ACCOUNT_ID` / `R2_ACCESS_KEY_ID` / `R2_SECRET_ACCESS_KEY` | Cloudflare R2 credentials |
| `R2_BUCKET_NAME` | R2 bucket name |
| `R2_PUBLIC_URL` | Public base URL of the R2 bucket |

### `plant-tracker-client/.env`
| Variable | Purpose |
|---|---|
| `VITE_API_BASE` | Backend URL (e.g. `http://localhost:8000`) |

## Common Gotchas
- **`secure` cookie on localhost**: The auth cookie uses `secure=True` only when `FRONTEND_URL` starts with `https://`. Plain `http://localhost` will set `secure=False` so browsers accept the cookie.
- **`FRONTEND_URL` / `ALLOWED_ORIGINS` in production env**: If you run locally with a `server/.env` that still points to the Railway/production URL, the OAuth callback will redirect to production instead of localhost.
- **`ProxyHeadersMiddleware`** is configured with `trusted_hosts="*"` so Railway's proxy generates correct `https://` redirect URIs. This has no effect locally.
- **boto3 is synchronous**: R2 uploads run in a `ThreadPoolExecutor` inside the async route handlers.
