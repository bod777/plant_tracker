from datetime import datetime
from fastapi.encoders import jsonable_encoder
from pymongo.server_api import ServerApi
import motor.motor_asyncio
from typing import Optional, Dict, Any

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


async def upsert_user(user_info: Dict[str, Any]) -> Dict[str, Any]:
    """Insert or update a user document in the database."""
    data = {
        "sub": user_info["sub"],
        "email": user_info.get("email"),
        "name": user_info.get("name"),
        "picture": user_info.get("picture"),
        "tier": user_info.get("tier", "free"),
    }
    await db.users.update_one(
        {"sub": data["sub"]},
        {
            "$set": {k: v for k, v in data.items() if v is not None},
            "$setOnInsert": {"created_at": datetime.utcnow()},
        },
        upsert=True,
    )
    doc = await db.users.find_one({"sub": data["sub"]})
    doc["id"] = str(doc.pop("_id"))
    return doc


async def get_user_by_sub(sub: str) -> Optional[Dict[str, Any]]:
    """Fetch a user document by its subject identifier."""
    doc = await db.users.find_one({"sub": sub})
    if doc:
        doc["id"] = str(doc.pop("_id"))
        return doc
    return None
