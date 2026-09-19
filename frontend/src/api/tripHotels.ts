import { apiFetch } from "./client";
import type { TripHotel, TripHotelCreateRequest } from "../types/hotel";

export async function listTripHotels(tripId: string): Promise<TripHotel[]> {
  return apiFetch<TripHotel[]>(`/trips/${tripId}/hotels`);
}

export async function addTripHotel(
  tripId: string,
  payload: TripHotelCreateRequest,
): Promise<TripHotel> {
  return apiFetch<TripHotel>(`/trips/${tripId}/hotels`, { method: "POST", body: payload });
}

export async function removeTripHotel(tripId: string, hotelId: string): Promise<void> {
  return apiFetch<void>(`/trips/${tripId}/hotels/${hotelId}`, { method: "DELETE" });
}
