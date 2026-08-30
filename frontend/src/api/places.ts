import { apiFetch } from "./client";
import type {
  ImportBulkRequest,
  ImportBulkResponse,
  ImportPreviewResponse,
  Place,
  PlaceCreateRequest,
  PlaceListParams,
  PlaceListResponse,
  PlaceReportRequest,
} from "../types/place";

function buildQuery(params: PlaceListParams): string {
  const search = new URLSearchParams();
  if (params.city) search.set("city", params.city);
  if (params.category) search.set("category", params.category);
  if (params.budget_min !== undefined) search.set("budget_min", String(params.budget_min));
  if (params.budget_max !== undefined) search.set("budget_max", String(params.budget_max));
  if (params.q) search.set("q", params.q);
  search.set("limit", String(params.limit ?? 20));
  search.set("offset", String(params.offset ?? 0));
  return search.toString();
}

export async function listPlaces(params: PlaceListParams = {}): Promise<PlaceListResponse> {
  return apiFetch<PlaceListResponse>(`/places?${buildQuery(params)}`, { auth: false });
}

export async function getPlace(placeId: string): Promise<Place> {
  return apiFetch<Place>(`/places/${placeId}`, { auth: false });
}

export async function createPlace(payload: PlaceCreateRequest): Promise<Place> {
  return apiFetch<Place>("/places", { method: "POST", body: payload });
}

export async function reportPlace(
  placeId: string,
  payload: PlaceReportRequest,
): Promise<{ message: string }> {
  return apiFetch(`/places/${placeId}/report`, { method: "POST", body: payload });
}

export async function importPreview(url: string): Promise<ImportPreviewResponse> {
  return apiFetch<ImportPreviewResponse>("/places/import/preview", {
    method: "POST",
    body: { url },
  });
}

export async function importBulk(payload: ImportBulkRequest): Promise<ImportBulkResponse> {
  return apiFetch<ImportBulkResponse>("/places/import/bulk", {
    method: "POST",
    body: payload,
  });
}
