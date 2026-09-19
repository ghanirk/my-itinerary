import { apiFetch } from "./client";
import type {
  TripInstallment,
  TripInstallmentAdjustRequest,
  TripInstallmentPayRequest,
} from "../types/installment";

export async function generateInstallments(tripId: string): Promise<TripInstallment[]> {
  return apiFetch<TripInstallment[]>(`/trips/${tripId}/installments/generate`, { method: "POST" });
}

export async function listInstallments(tripId: string): Promise<TripInstallment[]> {
  return apiFetch<TripInstallment[]>(`/trips/${tripId}/installments`);
}

export async function payInstallment(
  tripId: string,
  installmentId: string,
  payload: TripInstallmentPayRequest,
): Promise<TripInstallment> {
  return apiFetch<TripInstallment>(`/trips/${tripId}/installments/${installmentId}/pay`, {
    method: "PUT",
    body: payload,
  });
}

export async function adjustInstallments(
  tripId: string,
  payload: TripInstallmentAdjustRequest,
): Promise<TripInstallment[]> {
  return apiFetch<TripInstallment[]>(`/trips/${tripId}/installments/adjust`, {
    method: "POST",
    body: payload,
  });
}
