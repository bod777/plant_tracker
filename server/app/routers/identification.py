from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from typing import List, Optional

from .auth.deps import get_current_user
from ..services.plantid import PlantIdClient
from ..services.plantnet import PlantNetClient
from ..services.perenual import PerenualClient
from ..services.database import insert_plant_record, save_plants_to_record
from ..models.models import PlantRecord, PlantImage, PlantInfo, PlantConfidence
from ..models.utils import convert_to_plant_images

router = APIRouter(prefix="/api")

plantid_client = PlantIdClient()
plantnet_client = PlantNetClient()
perenual_client = PerenualClient()


@router.post("/identify")
async def identify_plant(
    files: List[UploadFile] = File(..., description="up to 5 images"),
    organs: Optional[List[str]] = Form(None, description="List of plant organs to identify"),
    latitude: float = Form(...),
    longitude: float = Form(...),
    user=Depends(get_current_user),
):
    """Identify a plant from uploaded image files using Plant.id."""
    try:
        plant_images = await convert_to_plant_images(files, organs)
        record = insert_plant_record(user["userId"], plant_images, (longitude, latitude))
        if user["tier"] == "premium":
            plant_recommendations, list_plant_info = await plantid_client.identify_and_parse(
                files=files,
                latitude=latitude,
                longitude=longitude,
            )
            save_plants_to_record(record["recordId"], plant_recommendations)
        else:
            print("User is not premium, skipping plant.id identification")
            # Fallback to PlantNet if user is not premium
            # Uncomment when PlantNet integration is ready
            # ideally it will return the plant net results first 
            # and then check the perenual API to help with latency
            # response = await plantnet_client.identify(
            #     img_bytes_list=[await file.read() for file in files],
            #     latitude=latitude,
            #     longitude=longitude,
            # )
        
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Plant identification with plantid failed: {exc}")
    return plant_recommendations, list_plant_info