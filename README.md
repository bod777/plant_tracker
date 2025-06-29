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
   cp .env.example .env
   # Fill in MONGODB_URI and PLANT_ID_API_KEY in .env
   uvicorn app.main:app --reload
   ```

3. **Frontend Setup**  
   ```bash
   cd client
   npm install
   npm run dev
   ```

4. **Use the App**
   - Frontend runs at http://localhost:8080
   - Backend runs at http://localhost:8000
   - Backend CORS allows requests from http://localhost:8080
   - Upload plant images, identify, and save to MongoDB.
