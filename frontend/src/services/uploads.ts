import { apiClient } from "./api";
import type { UploadReport } from "../types/api";

export async function uploadFile(file: File): Promise<UploadReport> {
  const form = new FormData();
  form.append("file", file);
  const response = await apiClient.post<UploadReport>("/upload", form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return response.data;
}
