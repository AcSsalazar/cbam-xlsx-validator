import { apiClient } from "./api";
import type { PaginatedRecords } from "../types/api";

export async function listRecords(
  page: number,
  pageSize: number,
): Promise<PaginatedRecords> {
  const response = await apiClient.get<PaginatedRecords>("/records", {
    params: { page, page_size: pageSize },
  });
  return response.data;
}
