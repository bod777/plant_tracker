import os
import base64
import time
from fastapi import Depends, APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from typing import List
from bson import ObjectId
from kindwise import PlantApi, PlantIdentification, ClassificationLevel

from .mongodb_server import db
from .models import PlantResponse, IdentifyRequest, Suggestion, SimilarImage, UpdateNotesRequest
from .deps import get_current_user

router = APIRouter(prefix="/api")

# Initialize Plant.id client
api_key = os.getenv("PLANT_ID_API_KEY")
if not api_key:
    raise RuntimeError("PLANT_ID_API_KEY not set in environment variables")
plant_client = PlantApi(api_key=api_key)

@router.post("/identify-plant")
async def identify_plant(request: IdentifyRequest, user=Depends(get_current_user)):
    """Identify a plant from one or more base64-encoded image strings."""
    try:
        # Decode each base64 string to raw bytes
        b64_images = [img.split(",", 1)[1] if "," in img else img for img in request.image_data]
        img_bytes_list = [base64.b64decode(b64) for b64 in b64_images]
        details_to_return = [
            'common_names', 'url', 'description', 'synonyms', 'edible_parts',
            'propagation_methods', 'watering', 'best_watering', 'taxonomy',
            'best_light_condition', 'best_soil_type', 'cultural_significance', 'image'
        ]
        # Pass the raw bytes list to the client
        identification: PlantIdentification = plant_client.identify(
            img_bytes_list,
            details=details_to_return,
            latitude_longitude=(request.latitude, request.longitude),
            language=['en'],
            classification_level=ClassificationLevel.ALL
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Identification failed: {e}")

    if (identification.status.name != 'COMPLETED' or
        not identification.result or
        not identification.result.classification):
        raise HTTPException(
            status_code=500,
            detail="Identification incomplete or missing classification"
        )

    suggestions: List[Suggestion] = []
    for s in identification.result.classification.suggestions or []:
        # if s.probability < request.threshold:
        #     continue
        details = s.details
        desc = None
        if details.get('description'):
            desc = details['description'].get('value')
        suggestions.append(Suggestion(
            id=s.id,
            name=s.name.title(),
            probability=s.probability,
            common_names=[c.title() for c in details.get('common_names')],
            taxonomy=details.get('taxonomy'),
            url=details.get('url'),
            description=desc,
            synonyms=details.get('synonyms'),
            edible_parts=details.get('edible_parts'),
            watering=details.get('watering'),
            propagation_methods=details.get('propagation_methods'),
            best_light_condition=details.get('best_light_condition'),
            best_soil_type=details.get('best_soil_type'),
            cultural_significance=details.get('cultural_significance'),
            best_watering=details.get('best_watering'),
            similar_images=[SimilarImage(url=img.url, similarity=img.similarity)
                             for img in (s.similar_images or [])]
        ))

    response = PlantResponse(
        user_id=user["sub"],
        access_token=identification.access_token,
        is_plant_boolean=identification.result.is_plant.binary,
        is_plant_probability=identification.result.is_plant.probability,
        suggestions=suggestions,
        notes="",
        datetime=str(identification.input.datetime),
        latitude=identification.input.latitude,
        longitude=identification.input.longitude,
        image_data=request.image_data,
        _ts=int(time.time())
    )

    # Immediately save to MongoDB
    doc = jsonable_encoder(response)
    result = await db.plants.insert_one(doc)
    response.id = str(result.inserted_id)

    return response

@router.put("/update-plant-notes")
async def update_plant_notes(request: UpdateNotesRequest):
    if not ObjectId.is_valid(request.id):
        raise HTTPException(status_code=400, detail="Invalid plant ID")
    result = await db.plants.update_one(
        {"_id": ObjectId(request.id)},
        {"$set": {"notes": request.notes, "_ts": int(time.time())}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Plant not found")
    return {"id": request.id, "notes": request.notes}

@router.delete("/delete-plant/{plant_id}")
async def delete_plant(plant_id: str, user=Depends(get_current_user)):
    """Delete a plant record by id for the current user."""
    if not ObjectId.is_valid(plant_id):
        raise HTTPException(status_code=400, detail="Invalid plant ID")
    result = await db.plants.delete_one({"_id": ObjectId(plant_id), "user_id": user["sub"]})
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
    return { "email": user["email"], "sub": user["sub"] }

@router.post("/auth/logout")
async def logout():
    """Clear the auth cookie so the user is fully logged out."""
    response = JSONResponse({"detail": "Logged out"})
    response.delete_cookie("access_token")
    return response
