from pymongo.server_api import ServerApi
import motor.motor_asyncio
import os
from dotenv import load_dotenv
load_dotenv()

MONGO_URI = os.getenv("MONGODB_URI")
DB_NAME   = os.getenv("MONGODB_DB_NAME", "plant_tracker")

client = motor.motor_asyncio.AsyncIOMotorClient(
    MONGO_URI,
    server_api=ServerApi("1")
) 
db = client[DB_NAME]
