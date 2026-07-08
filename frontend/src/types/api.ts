/** API contract types - mirror backend Pydantic schemas. */

export interface FieldError {
  row: number;
  field: string;
  value: string;
  message: string;
}

export interface UploadReport {
  filename: string;
  total_rows: number;
  valid_rows: number;
  invalid_rows: number;
  errors: FieldError[];
}

export interface RecordItem {
  id: number;
  row_number: number;
  created_at: string;
  payload: Record<string, string>;
}

export interface PaginatedRecords {
  page: number;
  page_size: number;
  total: number;
  items: RecordItem[];
}

export interface HealthResponse {
  status: string;
}
