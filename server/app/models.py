from typing import List, Literal, Optional
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
    organs: str = None


class PlantRecord(BaseModel):
    recordId: str = Field(..., description="Unique record ID (primary key)")
    userId: str = Field(..., description="ID of the user who created this record")
    plants: List[PlantConfidence] = Field(..., description="List of detected plants with confidence scores")
    photos: List[PlantImage] = Field(..., description="List of photos with their organ classifications")
    notes: Optional[str] = Field(None, description="User-provided notes about the plant record")
    locations: List[str] = Field(default_factory=list, description="List of location names or coordinates")
    datetime: Optional[str] = None
    _ts: Optional[int] = None


class PlantInfo(BaseModel):
    plantId: str = Field(..., description="Unique plant ID (primary key)")
    commonName: Optional[str] = Field(None, description="Common name of the plant")
    scientificName: Optional[str] = Field(None, description="Scientific name of the plant")
    photos: List[str] = Field(default_factory=list, description="List of reference photo URLs")
    source: Literal['perennial', 'plant_id'] = Field(..., description="Source of the plant information")
    sunlight: Optional[str] = Field(None, description="Sunlight requirements description")
    watering: Optional[str] = Field(None, description="Watering instructions")
    originalApiResponse: Optional[dict] = Field(None, description="Additional info (description, taxonomy, pruning, etc.)")
