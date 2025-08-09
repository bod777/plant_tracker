import time
from typing import List

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException

# from ..models import PlantResponse, UpdateNotesRequest
from .auth.deps import get_current_user
from ..services.database import db
from ..models.models import PlantRecord, PlantInfo

router = APIRouter(prefix="/api")


@router.get("/plant-records", response_model=List[PlantRecord])
async def get_plant_records(user=Depends(get_current_user)):
    """Fetch all plant records for the current user."""
    docs = await db.plantRecord.find({"userId": user["userId"]}, {"_id": 0}).to_list(length=100)
    return docs


@router.get("/plant-info/{plant_id}", response_model=PlantInfo)
async def get_plant_info(plant_id: str):
    """Fetch static plant information by plant ID."""
    doc = await db.plantInfo.find_one({"plantId": plant_id}, {"_id": 0})
    if not doc:
        raise HTTPException(status_code=404, detail="Plant info not found")
    return doc


@router.delete("/plants/{plant_id}")
async def delete_plant_by_id(plant_id: str, user=Depends(get_current_user)):
    """Delete a plant record by ID for the current user."""
    if not ObjectId.is_valid(plant_id):
        raise HTTPException(status_code=400, detail="Invalid plant ID")
    result = await db.plants.delete_one({"_id": ObjectId(plant_id), "user_id": user["userId"]})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Plant not found")
    return {"id": plant_id}


# @router.put("/plants/{plant_id}/notes")
# async def update_plant_notes_by_id(plant_id: str, request: UpdateNotesRequest):
#     if not ObjectId.is_valid(plant_id):
#         raise HTTPException(status_code=400, detail="Invalid plant ID")
#     result = await db.plants.update_one(
#         {"_id": ObjectId(plant_id)},
#         {"$set": {"notes": request.notes, "_ts": int(time.time())}},
#     )
#     if result.matched_count == 0:
#         raise HTTPException(status_code=404, detail="Plant not found")
#     return {"id": plant_id, "notes": request.notes}
