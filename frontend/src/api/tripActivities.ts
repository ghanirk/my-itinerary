import { apiFetch } from "./client";
import type { TripActivity, TripActivityCreateRequest } from "../types/activity";

export async function listTripActivities(tripId: string): Promise<TripActivity[]> {
  return apiFetch<TripActivity[]>(`/trips/${tripId}/activities`);
}

export async function addTripActivity(
  tripId: string,
  payload: TripActivityCreateRequest,
): Promise<TripActivity> {
  return apiFetch<TripActivity>(`/trips/${tripId}/activities`, { method: "POST", body: payload });
}

export async function removeTripActivity(tripId: string, activityId: string): Promise<void> {
  return apiFetch<void>(`/trips/${tripId}/activities/${activityId}`, { method: "DELETE" });
}
