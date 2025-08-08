import time
import base64
from typing import List
import os
from datetime import datetime, timezone
import uuid

from fastapi import UploadFile, HTTPException
from kindwise import PlantApi, PlantIdentification, ClassificationLevel
from ..config import Config

from ..models.models import PlantInfo, PlantConfidence, PlantIdObject
from ..services.database import insert_plant_info

class PlantIdClient:
    """
    Wrapper class for identifying plants using the Plant.id API
    """

    def __init__(self, api_key: str = None):
        # Initialize API key and client
        key = api_key or Config.PLANT_ID_API_KEY
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
        identification: PlantIdentification
    ) -> PlantInfo:
        
        plant_identifications = []
        list_plant_info = []
        now = datetime.now(timezone.utc)
        for s in identification.result.classification.suggestions or []:
            details = s.details or {}
            plantId = str(uuid.uuid4())

            plant_info = PlantInfo(
                plantId=plantId,
                createdAt=now.isoformat(),  # ISO 8601 with timezone
                _ts=int(now.timestamp()),  # Unix timestamp (seconds)
                source="plant_id",
                commonName=details.get("common_names")[0].title(),
                scientificName=details.get("scientific_name"),
                photos=[img.url for img in (s.similar_images or [])],
                sunlight=details.get("best_light_condition"),
                watering=details.get("watering"),
                originalApiResponse=PlantIdObject(
                    accessToken=identification.access_token,
                    id=s.id,
                    taxonomy=s.taxonomy,
                    url=s.url,
                    description=s.description,
                    synonyms=s.synonyms,
                    image=base64.b64encode(s.image).decode('utf-8'),
                    edible_parts=details.get("edible_parts", []),
                    propagation_methods=details.get("propagation_methods", []),
                    best_soil_type=details.get("best_soil_type"),
                    cultural_significance=details.get("cultural_significance"),
                )
            )

            insert_plant_info(plant_info)
            list_plant_info.append(plant_info)
            plant_identifications.append({
                "plantId": plantId,
                "confidence": s.probability
            })

        return plant_identifications, list_plant_info


    async def identify_and_parse(
        self,
        files: List[UploadFile],
        latitude: float,
        longitude: float
    ) -> List[PlantConfidence]:
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
            identification=identification
        )
