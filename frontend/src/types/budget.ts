export interface TripBudgetSummary {
  id: string;
  trip_id: string;
  total_cost: number;
  cost_per_member: number;
  details: string | null; // JSON string, lihat TripBudgetDetails
  calculated_at: string;
}

// Bentuk `details` setelah di-JSON.parse (lihat backend app/services/budget_calculator.py)
export interface TripBudgetDetails {
  transport: number;
  hotel: number;
  activities: number;
  makan: number;
  lokal: number;
  num_members: number;
  duration_days: number;
}
