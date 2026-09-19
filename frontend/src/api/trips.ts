import { apiFetch } from "./client";
import type { Trip, TripCreateRequest, TripUpdateRequest } from "../types/trip";

export async function listTrips(): Promise<Trip[]> {
  return apiFetch<Trip[]>("/trips/");
}

export async function getTrip(tripId: string): Promise<Trip> {
  return apiFetch<Trip>(`/trips/${tripId}`);
}

export async function createTrip(payload: TripCreateRequest): Promise<Trip> {
  return apiFetch<Trip>("/trips/", { method: "POST", body: payload });
}

export async function updateTrip(tripId: string, payload: TripUpdateRequest): Promise<Trip> {
  return apiFetch<Trip>(`/trips/${tripId}`, { method: "PUT", body: payload });
}

export async function deleteTrip(tripId: string): Promise<void> {
  return apiFetch<void>(`/trips/${tripId}`, { method: "DELETE" });
}
