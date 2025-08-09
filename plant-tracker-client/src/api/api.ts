import axios from 'axios';

import { PlantRecord, PlantInfo } from './models';

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
  withCredentials: true,
});

/**
 * Fetch all plant records for the current user.
 * @returns Array of PlantRecord
 */
export async function fetchPlantRecords(): Promise<PlantRecord[]> {
  const response = await apiClient.get<PlantRecord[]>('/plant-records');
  return response.data;
}

/**
 * Fetch static plant information by plant ID.
 * @param plantId Plant identifier to look up
 * @returns PlantInfo from the backend
 */
export async function fetchPlantInfo(plantId: string): Promise<PlantInfo> {
  const response = await apiClient.get<PlantInfo>(`/plant-info/${plantId}`);
  return response.data;
}

