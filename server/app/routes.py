from dotenv import load_dotenv
import os
import base64
from fastapi import Depends, APIRouter, Response, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from typing import List
from bson import ObjectId
from kindwise import PlantApi, PlantIdentification

from .mongodb_server import db
from .models import PlantResponse, IdentifyRequest, Suggestion, SimilarImage, UpdateNotesRequest
from .deps import get_current_user

# Load environment variables
load_dotenv()

router = APIRouter(prefix="/api")

# Initialize Plant.id client
api_key = os.getenv("PLANT_ID_API_KEY")
if not api_key:
    raise RuntimeError("PLANT_ID_API_KEY not set in environment variables")
plant_client = PlantApi(api_key=api_key)

@router.post("/identify-plant")
async def identify_plant(request: IdentifyRequest, user=Depends(get_current_user)):
    """
    Identify a plant from a base64-encoded image string.
    """
    try:
        # Decode base64 string to bytes
        b64_str = request.image_data.split(",", 1)[1]
        details_to_return = ['common_names', 'url', 'description', 'synonyms', 'edible_parts', 'propagation_methods', 'watering', 'best_watering',  'taxonomy', 'best_light_condition', 'best_soil_type', 'cultural_significance', 'image']

        # 2a) if you want to pass raw bytes:
        img_bytes = base64.b64decode(b64_str)
        identification: PlantIdentification = plant_client.identify(
            img_bytes,
            details=details_to_return,
            latitude_longitude=(request.latitude, request.longitude),
            language=['en'],
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
        if s.probability < 0.5:
            continue
        details = s.details
        desc = None
        if details.get('description'):
            desc = details['description'].get('value')
        suggestions.append(Suggestion(
            id=s.id,
            name=s.name,
            probability=s.probability,
            common_names=details.get('common_names'),
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
        image_data=request.image_data
    )

    # Immediately save to MongoDB
    doc = jsonable_encoder(response)
    await db.plants.insert_one(doc)

    return response

@router.put("/update-plant-notes")
async def update_plant_notes(request: UpdateNotesRequest):
    if not ObjectId.is_valid(request.id):
        raise HTTPException(status_code=400, detail="Invalid plant ID")
    result = await db.plants.update_one(
        {"_id": ObjectId(request.id)},
        {"$set": {"notes": request.notes}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Plant not found")
    return {"id": request.id, "notes": request.notes}

# --- Fetch Plants ---
@router.get("/my-plants", response_model=List[PlantResponse])
async def get_plants(user=Depends(get_current_user)):
    sub = user["sub"]
    print(f"[my-plants] · querying for user_id={sub!r}")
    
    # with the index in place this is now a quick lookup
    docs = await db.plants.find().to_list(length=20)
    
    print(f"[my-plants] · returned {len(docs)} docs")
    return [PlantResponse(**doc) for doc in docs]


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
