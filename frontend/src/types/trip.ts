import type { TripActivity } from "./activity";
import type { TripHotel } from "./hotel";
import type { TripMember } from "./member";

export type TransportMode = "kereta" | "mobil_pribadi" | "pesawat" | "travel" | "bis";

export type TripStatus = "draft" | "confirmed";

export interface TripCreateRequest {
  name: string;
  destination_city: string;
  duration_days: number;
  departure_month_target: string; // ISO datetime
  transport_mode: TransportMode;
}

export interface TripUpdateRequest {
  name?: string;
  destination_city?: string;
  duration_days?: number;
  departure_month_target?: string;
  transport_mode?: TransportMode;
  status?: TripStatus;
}

export interface Trip {
  id: string;
  owner_id: string;
  name: string;
  destination_city: string;
  duration_days: number;
  departure_month_target: string;
  transport_mode: TransportMode;
  status: TripStatus;
  created_at: string;
  updated_at: string;
  members?: TripMember[] | null;
  hotels?: TripHotel[] | null;
  activities?: TripActivity[] | null;
}
