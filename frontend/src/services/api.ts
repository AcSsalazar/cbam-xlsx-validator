import axios from "axios";

/**
 * Centralised Axios instance. Base URL is read from VITE_API_URL at build
 * time, falling back to the local FastAPI default.
 */
export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000",
  timeout: 30_000,
  headers: {
    Accept: "application/json",
  },
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Re-throw a normalized error so callers only need to inspect .detail.
    if (axios.isAxiosError(error) && error.response) {
      const detail =
        (error.response.data as { detail?: string } | undefined)?.detail ??
        error.message;
      return Promise.reject(new Error(detail));
    }
    return Promise.reject(error instanceof Error ? error : new Error(String(error)));
  },
);
