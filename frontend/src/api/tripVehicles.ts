import { apiFetch } from "./client";
import type {
  TripVehicleGroup,
  TripVehicleGroupCostRequest,
  TripVehicleGroupCreateRequest,
} from "../types/vehicle";

export async function listVehicleGroups(tripId: string): Promise<TripVehicleGroup[]> {
  return apiFetch<TripVehicleGroup[]>(`/trips/${tripId}/vehicle-groups`);
}

export async function createVehicleGroup(
  tripId: string,
  payload: TripVehicleGroupCreateRequest,
): Promise<TripVehicleGroup> {
  return apiFetch<TripVehicleGroup>(`/trips/${tripId}/vehicle-groups`, {
    method: "POST",
    body: payload,
  });
}

export async function updateVehicleGroupCost(
  tripId: string,
  groupId: string,
  payload: TripVehicleGroupCostRequest,
): Promise<TripVehicleGroup> {
  return apiFetch<TripVehicleGroup>(`/trips/${tripId}/vehicle-groups/${groupId}/cost`, {
    method: "PUT",
    body: payload,
  });
}
