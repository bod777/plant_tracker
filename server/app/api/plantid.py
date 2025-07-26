import os
from typing import List

from fastapi import UploadFile, HTTPException
from kindwise import PlantApi, PlantIdentification, ClassificationLevel
from ..models import PlantResponse, Suggestion, SimilarImage

from ..models import PlantResponse

api_key = os.getenv("PLANT_ID_API_KEY")
if not api_key:
    raise RuntimeError("PLANT_ID_API_KEY not set in environment variables")
plant_client = PlantApi(api_key=api_key)


async def identify(
    files: List[UploadFile],
    latitude: float,
    longitude: float
) -> PlantResponse:
    """Identify plant images using Plant.id and persist the result."""
    img_bytes_list = [await f.read() for f in files]

    details_to_return = [
        "common_names",
        "url",
        "description",
        "synonyms",
        "edible_parts",
        "propagation_methods",
        "watering",
        "best_watering",
        "taxonomy",
        "best_light_condition",
        "best_soil_type",
        "cultural_significance",
        "image",
    ]

    try:
        identification: PlantIdentification = plant_client.identify(
            img_bytes_list,
            details=details_to_return,
            latitude_longitude=(latitude, longitude),
            language=["en"],
            classification_level=ClassificationLevel.ALL,
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Identification failed: {exc}")

    if (
        identification.status.name != "COMPLETED"
        or not identification.result
        or not identification.result.classification
    ):
        raise HTTPException(
            status_code=500,
            detail="Identification incomplete or missing classification",
        )
    
    return identification


async def parse_identification(
    user_id: str,
    encoded_images: List[str],
    identification: PlantIdentification
) -> PlantResponse:
    suggestions: List[Suggestion] = []
    for s in identification.result.classification.suggestions or []:
        details = s.details
        desc = None
        if details.get("description"):
            desc = details["description"].get("value")
        suggestions.append(
            Suggestion(
                id=s.id,
                name=s.name.title(),
                probability=s.probability,
                common_names=[c.title() for c in details.get("common_names")],
                taxonomy=details.get("taxonomy"),
                url=details.get("url"),
                description=desc,
                synonyms=details.get("synonyms"),
                edible_parts=details.get("edible_parts"),
                watering=details.get("watering"),
                propagation_methods=details.get("propagation_methods"),
                best_light_condition=details.get("best_light_condition"),
                best_soil_type=details.get("best_soil_type"),
                cultural_significance=details.get("cultural_significance"),
                best_watering=details.get("best_watering"),
                similar_images=[
                    SimilarImage(url=img.url, similarity=img.similarity)
                    for img in (s.similar_images or [])
                ],
            )
        )

    response = PlantResponse(
        user_id=user_id,
        access_token=identification.access_token,
        is_plant_boolean=identification.result.is_plant.binary,
        is_plant_probability=identification.result.is_plant.probability,
        suggestions=suggestions,
        notes="",
        datetime=str(identification.input.datetime),
        latitude=identification.input.latitude,
        longitude=identification.input.longitude,
        image_data=encoded_images,
        _ts=int(time.time()),
    )

    return response