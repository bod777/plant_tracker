import time
from typing import List

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException

from ..models import PlantResponse, UpdateNotesRequest
from ..deps import get_current_user
from ..services.database import db

router = APIRouter(prefix="/api")


@router.get("/plants", response_model=List[PlantResponse])
async def get_plants(user=Depends(get_current_user)):
    """Fetch all plants for the current user."""
    docs = await db.plants.find({"user_id": user["sub"]}).to_list(length=20)
    results = []
    for doc in docs:
        doc["id"] = str(doc.get("_id"))
        results.append(PlantResponse(**doc))
    return results


@router.delete("/plants/{plant_id}")
async def delete_plant_by_id(plant_id: str, user=Depends(get_current_user)):
    """Delete a plant record by ID for the current user."""
    if not ObjectId.is_valid(plant_id):
        raise HTTPException(status_code=400, detail="Invalid plant ID")
    result = await db.plants.delete_one({"_id": ObjectId(plant_id), "user_id": user["sub"]})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Plant not found")
    return {"id": plant_id}


@router.put("/plants/{plant_id}/notes")
async def update_plant_notes_by_id(plant_id: str, request: UpdateNotesRequest):
    if not ObjectId.is_valid(plant_id):
        raise HTTPException(status_code=400, detail="Invalid plant ID")
    result = await db.plants.update_one(
        {"_id": ObjectId(plant_id)},
        {"$set": {"notes": request.notes, "_ts": int(time.time())}},
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Plant not found")
    return {"id": plant_id, "notes": request.notes}
