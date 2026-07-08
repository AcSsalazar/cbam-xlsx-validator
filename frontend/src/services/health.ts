import { apiClient } from "./api";
import type { HealthResponse } from "../types/api";

export async function checkHealth(): Promise<boolean> {
  try {
    const response = await apiClient.get<HealthResponse>("/health");
    return response.data.status === "ok";
  } catch {
    return false;
  }
}
