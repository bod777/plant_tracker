import os
import base64
import time
from fastapi import Depends, APIRouter, HTTPException, UploadFile, File, Form
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from typing import List, Optional
from bson import ObjectId
from kindwise import PlantApi, PlantIdentification, ClassificationLevel

from .mongodb_server import db, save_to_db
from .models import (
    PlantResponse,
    Suggestion,
    SimilarImage,
    UpdateNotesRequest,
)
from .deps import get_current_user

router = APIRouter(prefix="/api")

# Initialize Plant.id client
api_key = os.getenv("PLANT_ID_API_KEY")
if not api_key:
    raise RuntimeError("PLANT_ID_API_KEY not set in environment variables")
plant_client = PlantApi(api_key=api_key)


@router.post("/identify-plant")
async def identify_plant(
    files: List[UploadFile] = File(..., description="up to 5 images"),
    latitude: float = Form(...),
    longitude: float = Form(...),
    user=Depends(get_current_user),
):
    """Identify a plant from uploaded image files."""
    try:
        identification = identify(files, latitude, longitude, user)
        response = parse_identification()
        save_to_db(response)
    except:
        raise HTTPException(status_code=500, detail="Plant identification failed")

    return response


@router.put("/update-plant-notes")
async def update_plant_notes(request: UpdateNotesRequest):
    if not ObjectId.is_valid(request.id):
        raise HTTPException(status_code=400, detail="Invalid plant ID")
    result = await db.plants.update_one(
        {"_id": ObjectId(request.id)},
        {"$set": {"notes": request.notes, "_ts": int(time.time())}},
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Plant not found")
    return {"id": request.id, "notes": request.notes}


@router.delete("/delete-plant/{plant_id}")
async def delete_plant(plant_id: str, user=Depends(get_current_user)):
    """Delete a plant record by id for the current user."""
    if not ObjectId.is_valid(plant_id):
        raise HTTPException(status_code=400, detail="Invalid plant ID")
    result = await db.plants.delete_one(
        {"_id": ObjectId(plant_id), "user_id": user["sub"]}
    )
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Plant not found")
    return {"id": plant_id}


# --- Fetch Plants ---
@router.get("/my-plants", response_model=List[PlantResponse])
async def get_plants(user=Depends(get_current_user)):
    # with the index in place this is now a quick lookup
    docs = await db.plants.find({"user_id": user["sub"]}).to_list(length=20)
    results = []
    for doc in docs:
        doc["id"] = str(doc.get("_id"))
        results.append(PlantResponse(**doc))
    return results


@router.get("/auth/me")
async def me(user=Depends(get_current_user)):
    # get_current_user returned the JWT payload with user info
    return {"email": user["email"], "sub": user["sub"]}


@router.post("/auth/logout")
async def logout():
    """Clear the auth cookie so the user is fully logged out."""
    response = JSONResponse({"detail": "Logged out"})
    response.delete_cookie("access_token")
    return response
