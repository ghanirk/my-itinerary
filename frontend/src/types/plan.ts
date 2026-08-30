import type { Place, PlaceCategory } from "./place";

export type PlanType = "manual" | "generated";

export interface PlanItemCreateRequest {
  place_id: string;
  order_index?: number;
}

export interface PlanCreateRequest {
  name?: string | null;
  type?: PlanType;
  budget?: number | null;
  items: PlanItemCreateRequest[];
}

export interface PlanItem {
  id: string;
  place_id: string;
  order_index: number;
  place: Place;
}

export interface Plan {
  id: string;
  name: string | null;
  type: PlanType;
  budget: number | null;
  created_at: string;
  items: PlanItem[];
}

export interface GeneratePlanRequest {
  budget: number;
  city: string;
  jumlah_tempat: number;
  categories?: PlaceCategory[] | null;
}
