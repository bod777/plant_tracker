import time
import base64
from typing import List

from fastapi import UploadFile, HTTPException
from kindwise import PlantApi, PlantIdentification, ClassificationLevel
from ..config import settings

from ..models import PlantResponse, Suggestion, SimilarImage


class PlantIdClient:
    """
    Wrapper class for identifying plants using the Plant.id API
    """

    def __init__(self, api_key: str = None):
        # Initialize API key and client

        key = api_key or settings.plant_id_api_key
        if not key:
            raise RuntimeError("PLANT_ID_API_KEY not set in environment variables or provided")
        self.plant_client = PlantApi(api_key=key)

    async def identify(
        self,
        img_bytes_list: List[bytes],
        latitude: float,
        longitude: float
    ) -> PlantIdentification:
        """
        Identify plant images using the Plant.id API.
        """
        try:
            identification: PlantIdentification = self.plant_client.identify(
                img_bytes_list,
                details=[
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
                ],
                latitude_longitude=(latitude, longitude),
                language=["en"],
                classification_level=ClassificationLevel.ALL,
            )
        except Exception as exc:
            raise HTTPException(status_code=502, detail=f"Identification failed: {exc}")

        # Ensure identification succeeded
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
        self,
        user_id: str,
        encoded_images: List[str],
        identification: PlantIdentification
    ) -> PlantResponse:
        """
        Parse the PlantIdentification result into a PlantResponse model.
        """
        suggestions: List[Suggestion] = []
        for s in identification.result.classification.suggestions or []:
            details = s.details or {}
            description_val = None
            if details.get("description"):
                description_val = details["description"].get("value")

            suggestions.append(
                Suggestion(
                    id=s.id,
                    name=s.name.title(),
                    probability=s.probability,
                    common_names=[c.title() for c in details.get("common_names") or []],
                    taxonomy=details.get("taxonomy"),
                    url=details.get("url"),
                    description=description_val,
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

    async def identify_and_parse(
        self,
        user_id: str,
        files: List[UploadFile],
        latitude: float,
        longitude: float
    ) -> PlantResponse:
        """
        High-level helper: reads uploaded files, performs identification, and parses the results.
        """
        # Read file bytes and build encoded image strings
        img_bytes_list: List[bytes] = []
        encoded_images: List[str] = []
        for f in files:
            content = await f.read()
            img_bytes_list.append(content)
            # Base64-encode for storage or return
            encoded_images.append(base64.b64encode(content).decode('utf-8'))

        # Call identification
        identification = await self.identify(
            img_bytes_list=img_bytes_list,
            latitude=latitude,
            longitude=longitude
        )

        # Parse into response model
        return await self.parse_identification(
            user_id=user_id,
            encoded_images=encoded_images,
            identification=identification
        )
