import type { Place } from "./place";

export interface TripActivityCreateRequest {
  place_id: string;
  day_index: number;
}

export interface TripActivity {
  id: string;
  trip_id: string;
  place_id: string;
  day_index: number;
  place: Place;
}
