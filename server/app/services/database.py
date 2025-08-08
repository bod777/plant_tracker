from fastapi.encoders import jsonable_encoder
from pymongo.server_api import ServerApi
import motor.motor_asyncio
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime, timezone
import uuid

from ..config import Config
from ..models.models import PlantInfo, PlantConfidence

client = motor.motor_asyncio.AsyncIOMotorClient(
    Config.MONGODB_URI,
    server_api=ServerApi("1"),
)
db = client[Config.MONGODB_DB_NAME]


async def insert_plant_record(
    userId: str,
    photos: List[Dict[str, Any]],
    location: Tuple[float, float]
) -> Dict[str, Any]:
    """
    Insert a new (partial) PlantRecord document.
    Only stores: recordId, userId, photos, locations, datetime, _ts.
    Excludes: plants, customName, notes (to be added later).
    """
    recordId = str(uuid.uuid4())
    now = datetime.now(timezone.utc)

    doc = {
        "recordId": recordId,
        "userId": userId,
        "photos": photos or [],
        "location": location or [],
        "createdAt": now.isoformat(),  # ISO 8601 with timezone
        "_ts": int(now.timestamp()),  # Unix timestamp (seconds)
    }

    # ensure clean JSON (e.g., if photos contains pydantic objects)
    payload = jsonable_encoder(doc)

    await db.plantRecord.insert_one(payload)
    # return the inserted document (without _id)
    return await db.plantRecord.find_one({"recordId": recordId}, {"_id": 0})


async def insert_plant_info(
    plant_info: PlantInfo
) -> Dict[str, Any]:
    """
    Insert a new (partial) PlantRecord document.
    Only stores: recordId, userId, photos, locations, datetime, _ts.
    Excludes: plants, customName, notes (to be added later).
    """
    # ensure clean JSON (e.g., if photos contains pydantic objects)
    payload = jsonable_encoder(plant_info)

    await db.plantRecord.insert_one(payload)
    # return the inserted document (without _id)
    return await db.plantRecord.find_one({"recordId": plant_info.plantId}, {"_id": 0})


async def save_plants_to_record(
    recordId: str,
    plants: List[PlantConfidence]
) -> Dict[str, Any]:
    payload = jsonable_encoder(plants)

    res = await db.plantRecord.update_one(
        {"recordId": recordId},
        {"$set": {"plants": payload}},
        upsert=False,  # change to True only if you want to create the doc implicitly
    )
    if res.matched_count == 0:
        return None

    return await db.plantRecord.find_one({"recordId": recordId}, {"_id": 0})


async def upsert_user(user_info: Dict[str, Any]) -> Dict[str, Any]:
    """Insert or update a user document in the database."""
    data = {
        "userId": user_info["sub"],
        "name": user_info.get("name"),
        "email": user_info.get("email"),
        "tier": user_info.get("tier", "free"),
    }
    await db.users.update_one(
        {"userId": data["userId"]},
        {
            "$set": {k: v for k, v in data.items() if v is not None},
            "$setOnInsert": {"createdAt": datetime.utcnow()},
        },
        upsert=True,
    )
    doc = await db.users.find_one({"userId": data["userId"]}, {"_id": 0})
    return doc


async def get_user_by_userId(userId: str) -> Optional[Dict[str, Any]]:
    """Fetch a user document by its userId."""
    return await db.users.find_one({"userId": userId}, {"_id": 0})