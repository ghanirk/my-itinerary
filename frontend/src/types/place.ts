export type PlaceCategory = "kuliner" | "fun" | "sport" | "alam";

export type SourceType = "manual" | "tiktok" | "youtube";

export type PlaceStatus = "draft" | "published";

export interface Place {
  id: string;
  name: string;
  category: PlaceCategory;
  price_min: number;
  price_max: number;
  gmaps_url: string;
  city: string;
  source_type: SourceType;
  source_url: string | null;
  photo_url: string | null;
  opening_hours: string | null;
  notes: string | null;
  status: PlaceStatus;
  created_by: string;
  created_at: string;
}

export interface PlaceCreateRequest {
  name: string;
  category: PlaceCategory;
  price_min?: number;
  price_max?: number;
  gmaps_url: string;
  city: string;
  source_type?: SourceType;
  source_url?: string | null;
  photo_url?: string | null;
  opening_hours?: string | null;
  notes?: string | null;
}

export interface PlaceListParams {
  city?: string;
  category?: PlaceCategory;
  budget_min?: number;
  budget_max?: number;
  q?: string;
  limit?: number;
  offset?: number;
}

export interface PlaceListResponse {
  items: Place[];
  total: number;
  limit: number;
  offset: number;
}

export interface PlaceReportRequest {
  reason: string;
}

// ---------- Auto-import dari TikTok / YouTube ----------

export interface ImportPreviewItem {
  name: string;
  category: PlaceCategory;
  price_min: number;
  price_max: number;
  city: string;
  gmaps_url: string;
  confidence: "high" | "low";
  warning: string | null;
}

export interface ImportPreviewResponse {
  is_compilation: boolean;
  source_type: SourceType;
  source_url: string;
  photo_url: string | null;
  items: ImportPreviewItem[];
}

export interface ImportBulkPlaceItem {
  name: string;
  category: PlaceCategory;
  price_min?: number;
  price_max?: number;
  gmaps_url: string;
  city: string;
  photo_url?: string | null;
  opening_hours?: string | null;
  notes?: string | null;
}

export interface ImportBulkRequest {
  source_type: SourceType;
  source_url: string;
  items: ImportBulkPlaceItem[];
}

export interface ImportBulkResultItem {
  name: string;
  status: "created" | "duplicate" | "error";
  place: Place | null;
  detail: string | null;
}

export interface ImportBulkResponse {
  results: ImportBulkResultItem[];
  created_count: number;
  skipped_count: number;
}
