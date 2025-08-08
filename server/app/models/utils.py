import base64
from typing import List, Optional
from fastapi import UploadFile, File, Form
from .models import PlantImage

async def convert_to_plant_images(
    files: List[UploadFile] = File(..., description="up to 5 images"),
    organs: Optional[List[str]] = Form(None, description="List of plant organs to identify"),
) -> List[PlantImage]:
    """
    Convert uploaded files + organs into a list of PlantImage objects.
    - Encodes each file as base64 string.
    - Uses corresponding organ or defaults to 'auto'.
    """
    plant_images: List[PlantImage] = []

    for idx, file in enumerate(files):
        # read file and encode as base64
        file_bytes = await file.read()
        image_b64 = base64.b64encode(file_bytes).decode("utf-8")

        # pick organ from list if available
        organ_value = organs[idx] if organs and idx < len(organs) else "auto"

        plant_images.append(
            PlantImage(
                image_data=image_b64,
                organs=organ_value
            )
        )

    return plant_images
