import axios from 'axios';
import { toast } from '@/hooks/use-toast';
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
 * Send one or more image files to the identify endpoint and save immediately.
 * @param files Array of image File objects
 * @returns PlantResponse from server
 */
export async function identifyPlant(
  files: File[],
  latitude?: number,
  longitude?: number,
  organs?: string[],
): Promise<IdentifiedPlant> {
  const formData = new FormData();
  files.forEach(f => formData.append('files', f));
  if (latitude !== undefined) formData.append('latitude', latitude.toString());
  if (longitude !== undefined) formData.append('longitude', longitude.toString());
  if (organs) organs.forEach(o => formData.append('organs', o));

  const response = await apiClient.post<ApiPlantResponse>('/identify-plant', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  const resp = response.data
  // It's good practice to check if suggestions exist
  if (!resp.suggestions || resp.suggestions.length === 0) {
    toast({ description: 'Could not identify the plant from the image.' });
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
    taxonomy: topSuggestion.taxonomy as Record<string, string> | undefined,
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
    taxonomy: topSuggestion.taxonomy as Record<string, string> | undefined,
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

/**
 * Delete a plant record by id.
 * @param id Document id to delete
 */
export async function deletePlant(id: string): Promise<void> {
  await apiClient.delete(`/delete-plant/${id}`);
}
