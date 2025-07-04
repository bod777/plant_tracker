from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict, Any

# --- Pydantic Models ---
class IdentifyRequest(BaseModel):
    user_id: Optional[str] = None
    image_data: str  # base64-encoded image
    latitude: float
    longitude: float

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
    is_plant_boolean: bool
    is_plant_probability: float
    suggestions: List[Suggestion]
    notes: Optional[str] = None
    datetime: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    image_data: Optional[str] = None

class UpdateNotesRequest(BaseModel):
    id: str
    notes: str
