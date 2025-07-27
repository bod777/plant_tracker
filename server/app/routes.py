# TO DO: Update Data Models
# TO DO: Update PlantNet route to save information in MongoDB
# TO DO: Update Perenual route to save information in MongoDB
# TO DO: Add a route to fetch plant information by ID
# TO DO: Update the notes route to check that the user is the owner of the plant

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
from .api.plantid import PlantIdClient
from .api.plantnet import PlantNetClient
from .api.perenual import PerenualClient
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

plantid_client = PlantIdClient()
plantnet_client = PlantNetClient()
perenual_client = PerenualClient()


@router.post("/plant-id")
async def get_plant_id(
    files: List[UploadFile] = File(..., description="up to 5 images"),
    latitude: float = Form(...),
    longitude: float = Form(...),
    user=Depends(get_current_user),
):
    """Identify a plant from uploaded image files."""
    try:
        # Use the combined identify_and_parse helper
        response: PlantResponse = await plantid_client.identify_and_parse(
            user_id=user.id,
            files=files,
            latitude=latitude,
            longitude=longitude,
        )
        # Persist the result
        save_to_db(response)
    except HTTPException:
        # Propagate HTTP exceptions as-is
        raise
    except Exception as exc:
        # Wrap other errors in a 500
        raise HTTPException(status_code=500, detail=f"Plant identification with plantid failed: {exc}")

    return response


@router.post("/plant-net")
async def get_plant_net(
    files: List[UploadFile] = File(..., description="up to 5 images"),
    organs: Optional[List[str]] = Form(None, description="List of plant organs to identify"),
    user=Depends(get_current_user),
):
    """Identify a plant from uploaded image files."""
    try:
        response = PlantNetClient.identify(files, organs)
    except:
        raise HTTPException(status_code=500, detail="Plant identification with plantnet failed")

    return response


@router.post("/perenual")
async def get_plant_net(
    identified_plant: dict,
    user=Depends(get_current_user)
):
    """Identify a plant from uploaded image files."""
    try:
        response, df = PerenualClient.get_plant_info(identified_plant)
    except:
        raise HTTPException(status_code=500, detail="Perenual search failed")

    return response


# --- Fetch Plants ---
@router.get("/plants", response_model=List[PlantResponse])
async def get_plants(user=Depends(get_current_user)):
    # with the index in place this is now a quick lookup
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
    result = await db.plants.delete_one(
        {"_id": ObjectId(plant_id), "user_id": user["sub"]}
    )
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
