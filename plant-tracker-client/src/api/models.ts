/**
 * Frontend models for Plant Tracker
 */

export interface SimilarImage {
  url: string;
  similarity: number;
}

export interface Suggestion {
  id: string;
  name: string;
  probability: number;
  common_names?: string[];
  taxonomy?: Record<string, unknown>;
  url?: string;
  description?: string;
  synonyms?: string[];
  edible_parts?: string[];
  watering?: Record<string, unknown>;
  propagation_methods?: string[];
  best_light_condition?: string;
  best_soil_type?: string;
  cultural_significance?: string;
  best_watering?: string;
  similar_images?: SimilarImage[];
}

/**
 * Represents the raw response from the `identifyPlant` API endpoint.
 */
export interface ApiPlantResponse {
  user_id?: string;
  access_token?: string;
  is_plant_boolean: boolean;
  is_plant_probability: number;
  suggestions: Suggestion[];
  notes?: string;
  datetime?: string;
  latitude?: number;
  longitude?: number;
  image_data?: string;
}

/**
 * Represents a processed, flattened plant identification result used within the application's state.
 * This is derived from the top suggestion of an `ApiPlantResponse`.
 */
export interface IdentifiedPlant {
  id: string; // Unique ID for the result in the history list
  image: string; // The base64 image data of the identified plant
  plantName: string; // The primary name from the top suggestion
  scientificName?: string; // A common name, if available
  confidence: number; // Probability percentage
  description?: string;
  watering?: string;
  soil_type?: string;
  light_condition?: string;
  url?: string;
  similar_images?: SimilarImage[];
  timestamp: Date;
}

/**
 * Payload to update an existing plant's notes.
 */
export interface UpdateNotesRequest {
  /** Document ID of the plant to update */
  id: string;
  /** New notes text */
  notes: string;
}