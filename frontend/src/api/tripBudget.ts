import { apiFetch } from "./client";
import type { TripBudgetSummary } from "../types/budget";

export async function calculateTripBudget(tripId: string): Promise<TripBudgetSummary> {
  return apiFetch<TripBudgetSummary>(`/trips/${tripId}/calculate-budget`, { method: "POST" });
}

export async function getTripBudget(tripId: string): Promise<TripBudgetSummary> {
  return apiFetch<TripBudgetSummary>(`/trips/${tripId}/budget`);
}
