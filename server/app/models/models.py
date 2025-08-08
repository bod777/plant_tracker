from typing import List, Literal, Optional, Tuple
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr


class User(BaseModel):
    userId: str = Field(..., description="Google's sub ID (primary key)")
    name: str = Field(..., description="Full name of the user")
    email: EmailStr = Field(..., description="User's email address")
    createdAt: datetime = Field(default_factory=datetime.utcnow, description="Account creation timestamp")
    tier: Literal['free', 'pro', 'enterprise'] = Field(..., description="User subscription tier")


class PlantConfidence(BaseModel):
    plantId: str = Field(..., description="ID of the detected plant")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score between 0 and 1")


class PlantImage(BaseModel):
    image_data: str = None
    organs: str = "auto"


class PlantRecord(BaseModel):
    recordId: str = Field(..., description="Unique record ID (primary key)")
    userId: str = Field(..., description="ID of the user who created this record")
    plants: List[PlantConfidence] = Field(..., description="List of detected plants with confidence scores")
    customName: Optional[str] = Field(None, description="Custom name of the plant")
    photos: List[PlantImage] = Field(..., description="List of photos with their organ classifications")
    notes: Optional[str] = Field(None, description="User-provided notes about the plant record")
    location: Tuple[float, float] = Field(default_factory=list, description="A tuple of latitude and longitude coordinates")
    createdAt: Optional[str] = None
    _ts: Optional[int] = None


class PlantIdObject(BaseModel):
    accessToken: str = Field(..., description="Access token for Plant.id API")
    id: str = Field(..., description="Unique identifier for the plant")
    taxonomy = Field(..., description="Taxonomy information of the plant")
    url = Field(..., description="URL to the plant's page on Plant.id")
    description = Field(..., description="Description of the plant")
    synonyms = Field(..., description="List of synonyms for the plant")
    image = Field(..., description="Base64 encoded image of the plant")
    edible_parts = Field(..., description="List of edible parts of the plant")
    propagation_methods = Field(..., description="List of propagation methods for the plant")
    best_soil_type = Field(..., description="Best soil type for the plant")
    cultural_significance = Field(..., description="Cultural significance of the plant")


class PlantInfo(BaseModel):
    plantId: str = Field(..., description="Unique plant ID (primary key)")
    createdAt: Optional[str] = None
    _ts: Optional[int] = None
    source: Literal['perennial', 'plant_id'] = Field(..., description="Source of the plant information")
    commonName: Optional[str] = Field(None, description="Common name of the plant")
    scientificName: Optional[str] = Field(None, description="Scientific name of the plant")
    photos: List[str] = Field(default_factory=list, description="List of reference photo URLs")
    sunlight: Optional[str] = Field(None, description="Sunlight requirements description")
    watering: Optional[str] = Field(None, description="Watering instructions")
    originalApiResponse: Optional[PlantIdObject] = Field(None, description="Additional info (description, taxonomy, pruning, etc.)")
