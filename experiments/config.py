import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).parent / ".env")

class Config():
    """Application configuration loaded from environment variables."""
    MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "plant_tracker")
    SESSION_SECRET_KEY = os.getenv("SESSION_SECRET_KEY", "a-strong-fallback-secret")
    ALLOWED_ORIGINS =  os.getenv("ALLOWED_ORIGINS", "http://localhost:8080")
    ORIGINS_ARRAY = [o.strip() for o in ALLOWED_ORIGINS.split(",")]
    PLANTNET_API = "https://my-api.plantnet.org/v2/identify/"
    PLANTNET_PROJECT = "all"
    PLANT_ID_API_KEY = os.getenv("PLANT_ID_API_KEY")
    PLANTNET_API_KEY = os.getenv("PLANTNET_API_KEY")
    PERENUAL_API_KEY = os.getenv("PERENUAL_API_KEY")
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET =  os.getenv("GOOGLE_CLIENT_SECRET")
    JWT_SECRET = os.getenv("JWT_SECRET", "secret")
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:8080/")
