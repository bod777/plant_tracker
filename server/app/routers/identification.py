from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from typing import List, Optional

from ..models import PlantResponse
from ..deps import get_current_user
from ..services.plantid import PlantIdClient
from ..services.plantnet import PlantNetClient
from ..services.perenual import PerenualClient
from ..services.database import save_to_db

router = APIRouter(prefix="/api")

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
    """Identify a plant from uploaded image files using Plant.id."""
    try:
        response: PlantResponse = await plantid_client.identify_and_parse(
            user_id=user["sub"],
            files=files,
            latitude=latitude,
            longitude=longitude,
        )
        save_to_db(response)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Plant identification with plantid failed: {exc}")
    return response


@router.post("/plant-net")
async def get_plant_net(
    files: List[UploadFile] = File(..., description="up to 5 images"),
    organs: Optional[List[str]] = Form(None, description="List of plant organs to identify"),
    user=Depends(get_current_user),
):
    """Identify a plant from uploaded image files using PlantNet."""
    try:
        response = await plantnet_client.identify(files, organs)
    except Exception:
        raise HTTPException(status_code=500, detail="Plant identification with plantnet failed")
    return response


@router.post("/perenual")
async def get_perenual(
    identified_plant: dict,
    user=Depends(get_current_user),
):
    """Retrieve plant care information from Perenual."""
    try:
        response, _ = await perenual_client.get_plant_info(identified_plant)
    except Exception:
        raise HTTPException(status_code=500, detail="Perenual search failed")
    return response
