import axios from 'axios';
import {
  ApiPlantResponse,
  UpdateNotesRequest,
  IdentifiedPlant,
} from './models';

// Base API URL used throughout the frontend when communicating with the backend
// Falls back to localhost if the env variable is undefined
export const API_BASE =
  import.meta.env.VITE_API_BASE ||
  '//localhost:8000'; // protocol-relative fallback to avoid mixed content

// Base API client
const apiClient = axios.create({
  baseURL: `${API_BASE}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,    // ← this line!
});

/**
 * Send one or more base64 images to the identify endpoint and save immediately.
 * @param images Array of base64-encoded image strings
 * @param notes Optional user notes
 * @param userId Optional user identifier
 * @returns PlantResponse from server
 */
export async function identifyPlant(
  image_data: string[],
  latitude?: number,
  longitude?: number,
  userId?: string,
  threshold?: number,
): Promise<IdentifiedPlant> {
  const payload: Partial<ApiPlantResponse> = {
    image_data,
    latitude,
    longitude
  };
  if (userId) payload.user_id = userId;
  if (threshold) {
    payload.threshold = threshold;
  } else {
    payload.threshold = 0.01;
  }
  const response = await apiClient.post<ApiPlantResponse>('/identify-plant', payload);
  const resp = response.data
  // It's good practice to check if suggestions exist
  if (!resp.suggestions || resp.suggestions.length === 0) {
    alert('Could not identify the plant from the image.');
    return;
  }

  const topSuggestion = resp.suggestions[0];

  const newIdentification: IdentifiedPlant = {
    id: resp.id || topSuggestion.id || Date.now().toString(),
    image_data: resp.image_data,
    plantName: topSuggestion.common_names?.[0] || topSuggestion.name, // Prefer common name, fallback to scientific
    scientificName: topSuggestion.name, // Always store the scientific name
    confidence: Math.round(topSuggestion.probability * 100),
    description: topSuggestion.description,
    watering: topSuggestion.best_watering,
    soil_type: topSuggestion.best_soil_type,
    light_condition: topSuggestion.best_light_condition,
    similar_images: topSuggestion.similar_images,
    timestamp: new Date(resp.datetime!),
    notes: resp.notes
  };
  return newIdentification;
}

/**
 * Fetch all saved plants from the server.
 * @returns Array of IdentifiedPlant
 */
export async function fetchPlants(): Promise<IdentifiedPlant[]> {
  const response = await apiClient.get<ApiPlantResponse[]>('/my-plants');
  
  // Map the raw API response to the frontend's IdentifiedPlant model
  const identifiedPlants = response.data.map(resp => {
    // A saved plant should always have suggestions, but it's safe to guard this.
    if (!resp.suggestions || resp.suggestions.length === 0) {
      console.warn('Skipping a history item with no suggestions:', resp);
      return null;
    }
    const topSuggestion = resp.suggestions[0];

    const newIdentification: IdentifiedPlant = {
      id: resp.id || topSuggestion.id || resp.datetime || Date.now().toString(),
      image_data: resp.image_data,
      plantName: topSuggestion.common_names?.[0] || topSuggestion.name,
      scientificName: topSuggestion.name,
      confidence: Math.round(topSuggestion.probability * 100),
      description: topSuggestion.description,
      watering: topSuggestion.best_watering,
      soil_type: topSuggestion.best_soil_type,
      light_condition: topSuggestion.best_light_condition,
      url: topSuggestion.url,
      similar_images: topSuggestion.similar_images,
      timestamp: new Date(resp.datetime!),
      notes: resp.notes
    };
    return newIdentification;
  }).filter((plant): plant is IdentifiedPlant => plant !== null); // Filter out any nulls

  return identifiedPlants;
}

/**
 * Update the notes field of an existing plant document.
 * @param params Contains plant id and new notes
 * @returns Updated id and notes
 */
export async function updatePlantNotes(
  params: UpdateNotesRequest
): Promise<UpdateNotesRequest> {
  const response = await apiClient.put<UpdateNotesRequest>('/update-plant-notes', params);
  return response.data;
}
