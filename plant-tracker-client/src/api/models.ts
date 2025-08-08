// models.ts

/** User subscription tiers */
export type Tier = 'free' | 'pro' | 'enterprise';

/** User */
export interface User {
  userId: string;
  name: string;
  email: string; 
  createdAt: string;
  tier: Tier;
}

/** Confidence for a detected plant */
export interface PlantConfidence {
  plantId: string;
  confidence: number;
}

/** Uploaded/derived plant image */
export interface PlantImage {
  image_data: string | null;
  organs: string;
}

/** A plant record owned by a user */
export interface PlantRecord {
  recordId: string;
  userId: string;
  plants: PlantConfidence[];
  customName?: string | null;
  photos: PlantImage[];
  notes?: string | null;
  location: [number, number];
  createdAt?: string | null;
  _ts?: number | null;
}

/** Static information about a plant */
export type PlantInfoSource = 'perennial' | 'plant_id';

export interface PlantIdObject {
    accessToken: string;
    id: string;
    taxonomy: string[];
    url: string;
    description: string;
    synonyms: string[];
    image: string[];
    edible_parts: string[];
    propagation_methods: string[];
    best_soil_type: string;
    cultural_significance: string;
}

export interface PlantInfo {
  plantId: string;
  createdAt?: string | null;
  _ts?: number | null;
  source: PlantInfoSource;
  commonName?: string | null;
  scientificName?: string | null;
  photos: string[];
  sunlight?: string | null;
  watering?: string | null;
  originalApiResponse?: PlantIdObject | null; // Store raw API response if needed
}
