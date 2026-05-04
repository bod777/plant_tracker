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

function dataURLToBlob(dataURL: string): Blob {
  const [header, data] = dataURL.split(',');
  const mime = header.match(/:(.*?);/)?.[1] ?? 'image/jpeg';
  const binary = atob(data);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
  return new Blob([bytes], { type: mime });
}

export async function identifyPlant(
  image_data: string[],
  latitude?: number,
  longitude?: number,
): Promise<IdentifiedPlant> {
  const formData = new FormData();
  image_data.forEach((dataURL, i) => {
    const blob = dataURLToBlob(dataURL);
    const ext = blob.type.split('/')[1] === 'jpeg' ? 'jpg' : (blob.type.split('/')[1] ?? 'jpg');
    formData.append('images', blob, `image${i}.${ext}`);
  });
  if (latitude !== undefined) formData.append('latitude', String(latitude));
  if (longitude !== undefined) formData.append('longitude', String(longitude));

  const response = await apiClient.post<ApiPlantResponse>('/identify-plant', formData, {
    headers: { 'Content-Type': undefined },
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
    image_urls: resp.image_urls?.length ? resp.image_urls : (resp.image_data || []),
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
 * Fetch the count of saved plants for the current user.
 */
export async function fetchPlantCount(): Promise<number> {
  const response = await apiClient.get<{ count: number }>('/my-plants/count');
  return response.data.count;
}

function mapResponseToPlant(resp: ApiPlantResponse): IdentifiedPlant | null {
  if (!resp.suggestions || resp.suggestions.length === 0) {
    console.warn('Skipping a history item with no suggestions:', resp);
    return null;
  }
  const topSuggestion = resp.suggestions[0];
  return {
    id: resp.id || topSuggestion.id || resp.datetime || Date.now().toString(),
    image_urls: resp.image_urls?.length ? resp.image_urls : (resp.image_data || []),
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
    notes: resp.notes,
  };
}

/**
 * Fetch a page of saved plants from the server (10 per page, no image data).
 */
export async function fetchPlants(page = 1): Promise<IdentifiedPlant[]> {
  const response = await apiClient.get<ApiPlantResponse[]>('/my-plants', { params: { page } });
  return response.data.map(mapResponseToPlant).filter((p): p is IdentifiedPlant => p !== null);
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
