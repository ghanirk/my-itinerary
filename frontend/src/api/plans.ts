import { apiFetch } from "./client";
import type { GeneratePlanRequest, Plan, PlanCreateRequest } from "../types/plan";

export async function listMyPlans(): Promise<Plan[]> {
  return apiFetch<Plan[]>("/plans");
}

export async function createPlan(payload: PlanCreateRequest): Promise<Plan> {
  return apiFetch<Plan>("/plans", { method: "POST", body: payload });
}

export async function generatePlan(payload: GeneratePlanRequest): Promise<Plan> {
  return apiFetch<Plan>("/plans/generate", { method: "POST", body: payload });
}

export async function deletePlan(planId: string): Promise<void> {
  return apiFetch<void>(`/plans/${planId}`, { method: "DELETE" });
}
