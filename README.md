# Plant Tracker Web App

A full-stack plant tracker web application built with:

- **Frontend**: React + Vite
- **Backend**: FastAPI + Uvicorn
- **Database**: MongoDB (Motor)
- **Plant ID API**: Plant.id

## Getting Started

1. **Clone the repo**  
   ```bash
   git clone <this-repo-url>
   cd plant-tracker
   ```

2. **Backend Setup**
   ```bash
   cd server
   pip install -r requirements.txt
   cp .env.sample .env
   # Fill in the required environment variables in .env
   # FRONTEND_URL controls where the auth flow redirects after login
   # ALLOWED_ORIGINS is a comma separated list used for CORS
   uvicorn app.main:app --reload
   ```

3. **Frontend Setup**
   ```bash
   cd flora-finder-webapp-main
   cp .env.sample .env
   # Set VITE_API_BASE to your backend URL (e.g. http://localhost:8000)
   # Optionally set VITE_GOOGLE_SITE_VERIFICATION for Google search console
   npm install
   npm run dev
   ```

4. **Use the App**
   - Frontend runs at http://localhost:8080 (or the URL specified in `FRONTEND_URL`)
   - Backend runs at http://localhost:8000
   - Backend CORS allows requests from the origins defined in `ALLOWED_ORIGINS`
   - Upload plant images, identify, and save to MongoDB.

## Deploying to Heroku

This repository contains both the FastAPI backend and the React frontend. To
deploy them as a single Heroku app:

1. Add the Node and Python buildpacks (Node first):
   ```bash
   heroku buildpacks:add heroku/nodejs
   heroku buildpacks:add heroku/python
   ```
2. Push the code to Heroku. The root `package.json` defines a
   `heroku-postbuild` script which installs dependencies (including dev
   dependencies) and builds the React app. The compiled assets are served by
   FastAPI from the `dist/` directory.
3. Python dependencies are installed from the root `requirements.txt`, which
   simply references `server/requirements.txt`.
4. Heroku will start the backend using the root `Procfile`:
   ```bash
   web: uvicorn app.main:app --host=0.0.0.0 --port=$PORT --app-dir server
   ```
