from pymongo.server_api import ServerApi
from fastapi.encoders import jsonable_encoder
from .models import PlantResponse
import motor.motor_asyncio
import os
from dotenv import load_dotenv
load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME   = os.getenv("MONGODB_DB_NAME", "plant_tracker")

client = motor.motor_asyncio.AsyncIOMotorClient(
    MONGODB_URI,
    server_api=ServerApi("1")
) 
db = client[DB_NAME]

async def save_to_db(
    response: PlantResponse
) -> PlantResponse:
    """Save the identification result to MongoDB."""
    doc = jsonable_encoder(response)
    result = await db.plants.insert_one(doc)
    response.id = str(result.inserted_id)
    return response