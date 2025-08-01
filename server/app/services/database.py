from fastapi.encoders import jsonable_encoder
from pymongo.server_api import ServerApi
import motor.motor_asyncio

from ..config import settings
from ..models import PlantResponse

client = motor.motor_asyncio.AsyncIOMotorClient(
    settings.mongodb_uri,
    server_api=ServerApi("1"),
)
db = client[settings.mongodb_db_name]


async def save_to_db(response: PlantResponse) -> PlantResponse:
    """Save the identification result to MongoDB."""
    doc = jsonable_encoder(response)
    result = await db.plants.insert_one(doc)
    response.id = str(result.inserted_id)
    return response
