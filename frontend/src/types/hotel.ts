import type { Place } from "./place";

export interface TripHotelCreateRequest {
  place_id: string;
  nights: number;
  price_per_night: number;
  capacity_per_room: number;
}

export interface TripHotel {
  id: string;
  trip_id: string;
  place_id: string;
  nights: number;
  price_per_night: number;
  capacity_per_room: number;
  place: Place;
}
