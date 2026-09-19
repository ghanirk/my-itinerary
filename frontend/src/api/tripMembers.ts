import { apiFetch } from "./client";
import type { TripMember, TripMemberCreateRequest, TripTransport, TripTransportUpdateRequest } from "../types/member";

export async function listTripMembers(tripId: string): Promise<TripMember[]> {
  return apiFetch<TripMember[]>(`/trips/${tripId}/members`);
}

export async function addTripMember(
  tripId: string,
  payload: TripMemberCreateRequest,
): Promise<TripMember> {
  return apiFetch<TripMember>(`/trips/${tripId}/members`, { method: "POST", body: payload });
}

export async function removeTripMember(tripId: string, memberId: string): Promise<void> {
  return apiFetch<void>(`/trips/${tripId}/members/${memberId}`, { method: "DELETE" });
}

export async function setMemberTransportPrice(
  tripId: string,
  memberId: string,
  payload: TripTransportUpdateRequest,
): Promise<TripTransport> {
  return apiFetch<TripTransport>(`/trips/${tripId}/members/${memberId}/transport`, {
    method: "PUT",
    body: payload,
  });
}
