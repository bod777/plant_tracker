from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict, Any


# --- Pydantic Models ---
class IdentifyRequest(BaseModel):
    user_id: Optional[str] = None
    image_data: List[str]  # up to 5 base64-encoded images
    latitude: float
    longitude: float
    organs: Optional[List[str]] = None


class SimilarImage(BaseModel):
    url: HttpUrl
    similarity: float


class Suggestion(BaseModel):
    id: str
    name: str
    probability: float
    common_names: Optional[List[str]] = []
    taxonomy: Optional[Dict[str, Any]] = None
    url: Optional[HttpUrl] = None
    description: Optional[str] = None
    synonyms: Optional[List[str]] = []
    edible_parts: Optional[List[str]] = None
    watering: Optional[Dict[str, Any]] = None
    propagation_methods: Optional[List[str]] = []
    best_light_condition: Optional[str] = None
    best_soil_type: Optional[str] = None
    cultural_significance: Optional[str] = None
    best_watering: Optional[str] = None
    similar_images: Optional[List[SimilarImage]] = []


class PlantResponse(BaseModel):
    id: Optional[str] = None
    user_id: Optional[str] = None
    access_token: Optional[str] = None
    is_plant_boolean: Optional[bool] = None
    is_plant_probability: Optional[float] = None
    suggestions: Optional[List[Suggestion]] = []
    notes: Optional[str] = None
    datetime: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    image_data: Optional[List[str]] = None
    organs: Optional[List[str]] = None
    _ts: Optional[int] = None


class UpdateNotesRequest(BaseModel):
    id: str
    notes: str
